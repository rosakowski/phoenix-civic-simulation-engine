"""
Simulation Core - Predictive Modeling Engine

Agent-based modeling of urban heat dynamics and intervention impacts.
"""

import logging
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Tuple, Any
import random

import numpy as np
import pandas as pd
from scipy.spatial import cKDTree

logger = logging.getLogger(__name__)


class DemographicProfile(Enum):
    """Vulnerability profiles based on age, income, housing."""
    LOW_RISK = "low_risk"
    MODERATE_RISK = "moderate_risk" 
    HIGH_RISK = "high_risk"
    EXTREME_RISK = "extreme_risk"


@dataclass
class SyntheticResident:
    """
    An agent representing a synthetic resident of Phoenix.
    
    Attributes:
        id: Unique identifier
        lat, lon: Geographic location
        age: Age in years
        income: Annual income
        has_ac: Access to air conditioning
        has_car: Access to personal vehicle
        works_outdoors: Occupation requires outdoor work
        health_conditions: List of relevant conditions (diabetes, heart disease, etc.)
        social_isolation: 0-1 scale of social connectedness
        heat_vulnerability: Computed 0-100 vulnerability score
    """
    id: int
    lat: float
    lon: float
    age: int
    income: float
    has_ac: bool
    has_car: bool
    works_outdoors: bool
    health_conditions: List[str] = field(default_factory=list)
    social_isolation: float = 0.0
    
    # Dynamic state
    current_location: Tuple[float, float] = field(init=False)
    heat_exposure_today: float = 0.0
    hydration_level: float = 1.0
    health_status: str = "healthy"  # healthy, stressed, heat_illness, severe
    
    def __post_init__(self):
        self.current_location = (self.lat, self.lon)
        self.heat_vulnerability = self._compute_vulnerability()
    
    def _compute_vulnerability(self) -> float:
        """Compute heat vulnerability score (0-100)."""
        score = 0.0
        
        # Age factor
        if self.age > 65:
            score += 25
        elif self.age < 5:
            score += 20
        elif self.age > 50:
            score += 10
        
        # Income factor (poverty = higher risk)
        if self.income < 20000:
            score += 20
        elif self.income < 40000:
            score += 10
        
        # AC access (critical factor)
        if not self.has_ac:
            score += 30
        
        # Outdoor work
        if self.works_outdoors:
            score += 15
        
        # Health conditions
        score += len(self.health_conditions) * 5
        
        # Social isolation
        score += self.social_isolation * 10
        
        return min(100, score)
    
    def profile(self) -> DemographicProfile:
        """Classify into risk profile."""
        if self.heat_vulnerability < 25:
            return DemographicProfile.LOW_RISK
        elif self.heat_vulnerability < 50:
            return DemographicProfile.MODERATE_RISK
        elif self.heat_vulnerability < 75:
            return DemographicProfile.HIGH_RISK
        else:
            return DemographicProfile.EXTREME_RISK
    
    def update_daily(self, max_temp: float, interventions: Dict[str, Any]):
        """Update agent state for a day given temperature and interventions."""
        
        # Heat exposure
        base_exposure = max(0, max_temp - 85)  # Stress starts at 85°F
        
        # Intervention effects
        if interventions.get('cooling_center_nearby') and max_temp > 105:
            base_exposure *= 0.5
        
        if interventions.get('transit_cooling') and not self.has_car:
            base_exposure *= 0.8
        
        if interventions.get('neighborhood_canopy_increase'):
            base_exposure *= 0.85
        
        self.heat_exposure_today = base_exposure
        
        # Health impact
        if base_exposure > 20:
            self.hydration_level -= 0.1
            if random.random() < 0.01 * self.heat_vulnerability / 100:
                self.health_status = "heat_illness"
        
        if base_exposure > 30 and self.heat_vulnerability > 60:
            if random.random() < 0.05:
                self.health_status = "severe"
        
        # Recovery overnight
        self.hydration_level = min(1.0, self.hydration_level + 0.5)


@dataclass
class InterventionScenario:
    """
    A proposed urban intervention.
    
    Examples:
    - Plant 1,000 trees in census tract X
    - Deploy 5 cooling buses on route Y
    - Add cool roofs to Z square feet
    - Open 3 new cooling centers
    """
    name: str
    intervention_type: str  # 'tree_canopy', 'cooling_center', 'transit_cooling', 'cool_roofs'
    target_area: Dict[str, Any]  # GeoJSON polygon or census tract IDs
    implementation_cost: float  # Dollars
    timeline_months: int
    expected_outcomes: Dict[str, float] = field(default_factory=dict)
    
    VALID_TYPES = {"tree_canopy", "cooling_center", "transit_cooling", "cool_roofs"}

    def validate(self) -> bool:
        """Check if intervention is feasible given constraints.

        Validates:
        - intervention_type is a recognized type
        - implementation_cost is positive
        - target_area has required geographic fields with sane values
        - timeline_months is positive
        """
        if self.intervention_type not in self.VALID_TYPES:
            return False

        if self.implementation_cost <= 0:
            return False

        if self.timeline_months <= 0:
            return False

        # Validate target area geography
        if "center_lat" in self.target_area:
            lat = self.target_area.get("center_lat")
            lon = self.target_area.get("center_lon")
            radius = self.target_area.get("radius_km", 1.0)

            if lat is None or lon is None:
                return False
            if not (-90 <= lat <= 90):
                return False
            if not (-180 <= lon <= 180):
                return False
            if radius <= 0 or radius > 50:
                return False

        return True


class UrbanHeatSimulator:
    """
    Main simulation engine for urban heat dynamics.
    
    Simulates:
    - 100,000 synthetic residents
    - Daily temperature variations
    - Intervention impacts
    - Health outcomes
    - Economic costs/benefits
    """
    
    def __init__(self, n_residents: int = 100000):
        self.n_residents = n_residents
        self.residents: List[SyntheticResident] = []
        self.spatial_index: Optional[cKDTree] = None
        self.current_day = 0
        self.history: List[Dict] = []
        
        # Phoenix bounds (rough)
        self.lat_min, self.lat_max = 33.3, 33.6
        self.lon_min, self.lon_max = -112.3, -111.8
    
    def generate_synthetic_population(self, demographic_data: Optional[pd.DataFrame] = None):
        """
        Generate synthetic residents based on Phoenix demographics.
        """
        logger.info(f"Generating {self.n_residents} synthetic residents...")
        
        random.seed(42)
        np.random.seed(42)
        
        for i in range(self.n_residents):
            # Geographic distribution (clustered like real Phoenix)
            lat = np.random.normal(33.45, 0.08)
            lon = np.random.normal(-112.07, 0.12)
            
            # Ensure within bounds
            lat = np.clip(lat, self.lat_min, self.lat_max)
            lon = np.clip(lon, self.lon_min, self.lon_max)
            
            # Demographics (simplified model)
            age = int(np.random.choice(
                [np.random.randint(0, 18), np.random.randint(18, 65), np.random.randint(65, 95)],
                p=[0.25, 0.60, 0.15]
            ))
            
            income = np.random.lognormal(11, 0.6)  # Median ~$50k
            
            # Access to resources (correlated with income)
            has_ac = random.random() < (0.5 + 0.4 * (income / 100000))
            has_car = random.random() < (0.6 + 0.3 * (income / 100000))
            
            # Employment
            works_outdoors = random.random() < 0.15 and age > 18 and age < 65
            
            # Health (correlated with age)
            health_conditions = []
            if age > 50 and random.random() < 0.3:
                health_conditions.append('cardiovascular')
            if age > 40 and random.random() < 0.2:
                health_conditions.append('diabetes')
            
            resident = SyntheticResident(
                id=i,
                lat=lat,
                lon=lon,
                age=age,
                income=income,
                has_ac=has_ac,
                has_car=has_car,
                works_outdoors=works_outdoors,
                health_conditions=health_conditions,
                social_isolation=random.random() * 0.5
            )
            
            self.residents.append(resident)
        
        # Build spatial index for fast geographic queries
        coords = np.array([[r.lat, r.lon] for r in self.residents])
        self.spatial_index = cKDTree(coords)
        
        logger.info(f"Generated {len(self.residents)} residents")
        
        # Log demographic breakdown
        profiles = [r.profile() for r in self.residents]
        for profile in DemographicProfile:
            count = profiles.count(profile)
            logger.info(f"  {profile.value}: {count} ({100*count/len(self.residents):.1f}%)")
    
    def run_day(self, max_temp: float, interventions: List[InterventionScenario] = None):
        """
        Simulate one day given temperature and active interventions.
        """
        interventions = interventions or []
        
        # Map interventions to residents
        resident_interventions = self._map_interventions(interventions)
        
        # Update each resident
        daily_outcomes = {
            'heat_illness': 0,
            'severe_heat_illness': 0,
            'deaths': 0,
            'er_visits': 0
        }
        
        for resident in self.residents:
            interv = resident_interventions.get(resident.id, {})
            resident.update_daily(max_temp, interv)
            
            # Track outcomes
            if resident.health_status == "heat_illness":
                daily_outcomes['heat_illness'] += 1
                if random.random() < 0.1:  # 10% of heat illness -> ER
                    daily_outcomes['er_visits'] += 1
            elif resident.health_status == "severe":
                daily_outcomes['severe_heat_illness'] += 1
                daily_outcomes['er_visits'] += 1
                if random.random() < 0.05:  # 5% mortality for severe
                    daily_outcomes['deaths'] += 1
                    resident.health_status = "dead"
        
        # Record history
        self.history.append({
            'day': self.current_day,
            'max_temp': max_temp,
            'outcomes': daily_outcomes,
            'active_interventions': len(interventions)
        })
        
        self.current_day += 1
        
        return daily_outcomes
    
    def _map_interventions(self, interventions: List[InterventionScenario]) -> Dict[int, Dict]:
        """Map interventions to affected residents."""
        resident_interventions = {}
        
        for intervention in interventions:
            # Simple distance-based mapping
            if 'center_lat' in intervention.target_area:
                center = (intervention.target_area['center_lat'], 
                         intervention.target_area['center_lon'])
                radius = intervention.target_area.get('radius_km', 1.0)
                
                # Find residents within radius
                nearby_indices = self.spatial_index.query_ball_point(
                    center, radius / 111  # Rough conversion km to degrees
                )
                
                for idx in nearby_indices:
                    if idx not in resident_interventions:
                        resident_interventions[idx] = {}
                    
                    # Apply intervention effect
                    if intervention.intervention_type == 'cooling_center':
                        resident_interventions[idx]['cooling_center_nearby'] = True
                    elif intervention.intervention_type == 'tree_canopy':
                        resident_interventions[idx]['neighborhood_canopy_increase'] = True
                    elif intervention.intervention_type == 'transit_cooling':
                        resident_interventions[idx]['transit_cooling'] = True
        
        return resident_interventions
    
    def run_scenario(self, 
                     days: int = 365,
                     temperature_profile: Optional[List[float]] = None,
                     interventions: List[InterventionScenario] = None) -> Dict:
        """
        Run a full simulation scenario.
        
        Returns summary statistics and outcomes.
        """
        interventions = interventions or []
        
        # Generate temperature profile if not provided
        if temperature_profile is None:
            temperature_profile = self._generate_phoenix_temperatures(days)
        
        logger.info(f"Running {days}-day simulation with {len(interventions)} interventions...")
        
        for day, temp in enumerate(temperature_profile):
            if day % 30 == 0:
                logger.info(f"Day {day}: {temp:.1f}°F")
            
            self.run_day(temp, interventions)
        
        # Compile results
        total_outcomes = {
            'heat_illness': sum(h['outcomes']['heat_illness'] for h in self.history),
            'severe_heat_illness': sum(h['outcomes']['severe_heat_illness'] for h in self.history),
            'deaths': sum(h['outcomes']['deaths'] for h in self.history),
            'er_visits': sum(h['outcomes']['er_visits'] for h in self.history),
        }
        
        logger.info("\n=== Simulation Complete ===")
        logger.info(f"Total deaths: {total_outcomes['deaths']}")
        logger.info(f"Total ER visits: {total_outcomes['er_visits']}")
        logger.info(f"Heat illness events: {total_outcomes['heat_illness']}")
        
        return {
            'total_outcomes': total_outcomes,
            'daily_history': self.history,
            'interventions': [i.name for i in interventions]
        }
    
    def _generate_phoenix_temperatures(self, days: int) -> List[float]:
        """Generate realistic Phoenix temperature profile."""
        temps = []
        for day in range(days):
            # Seasonal cycle
            day_of_year = day % 365
            base_temp = 70 + 35 * np.sin(2 * np.pi * day_of_year / 365 - np.pi/2)
            
            # Daily variation
            noise = np.random.normal(0, 5)
            temps.append(base_temp + noise)
        
        return temps
    
    def get_vulnerable_populations(self, threshold: float = 50.0) -> pd.DataFrame:
        """Get residents with vulnerability above threshold."""
        vulnerable = [r for r in self.residents if r.heat_vulnerability > threshold]
        
        return pd.DataFrame([
            {
                'id': r.id,
                'lat': r.lat,
                'lon': r.lon,
                'vulnerability': r.heat_vulnerability,
                'age': r.age,
                'income': r.income,
                'has_ac': r.has_ac,
                'profile': r.profile().value
            }
            for r in vulnerable
        ])


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    # Demo simulation
    sim = UrbanHeatSimulator(n_residents=10000)  # Small for demo
    sim.generate_synthetic_population()
    
    # Baseline scenario (no interventions)
    print("\n--- Baseline (No Interventions) ---")
    baseline_results = sim.run_scenario(days=90)  # 3 months
    
    # Intervention scenario
    print("\n--- With Interventions ---")
    sim2 = UrbanHeatSimulator(n_residents=10000)
    sim2.generate_synthetic_population()
    
    interventions = [
        InterventionScenario(
            name="Downtown Cooling Centers",
            intervention_type="cooling_center",
            target_area={'center_lat': 33.45, 'center_lon': -112.07, 'radius_km': 2.0},
            implementation_cost=500000,
            timeline_months=3
        ),
        InterventionScenario(
            name="South Phoenix Tree Initiative",
            intervention_type="tree_canopy",
            target_area={'center_lat': 33.40, 'center_lon': -112.10, 'radius_km': 3.0},
            implementation_cost=2000000,
            timeline_months=12
        )
    ]
    
    intervention_results = sim2.run_scenario(days=90, interventions=interventions)
    
    # Compare
    print("\n=== Impact Analysis ===")
    baseline_deaths = baseline_results['total_outcomes']['deaths']
    intervention_deaths = intervention_results['total_outcomes']['deaths']
    deaths_prevented = baseline_deaths - intervention_deaths
    
    print(f"Deaths prevented: {deaths_prevented}")
    print(f"Cost per death prevented: ${(2500000 / max(deaths_prevented, 1)):,.0f}")