"""
API Bridge - Connects simulation backend to frontend dashboard
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import uvicorn
import json
from pathlib import Path

# Import our simulation components
import sys
sys.path.append(str(Path(__file__).parent.parent))
from simulation import UrbanHeatSimulator, InterventionScenario
from perception.data_fetcher import PhoenixDataFetcher

app = FastAPI(
    title="Phoenix Civic Simulation Engine API",
    description="Backend API for heat intervention simulation",
    version="0.1.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global simulation instance
simulator = None


class InterventionRequest(BaseModel):
    name: str
    intervention_type: str  # tree_canopy, cooling_center, transit_cooling, cool_roofs
    target_lat: float
    target_lon: float
    radius_km: float = 1.0
    budget: float


class SimulationResponse(BaseModel):
    deaths_prevented: int
    er_visits_prevented: int
    cost_per_life_saved: float
    roi_percent: float
    vulnerable_population_affected: int
    intervention_effectiveness: Dict[str, float]


@app.on_event("startup")
async def startup_event():
    """Initialize simulator on startup."""
    global simulator
    print("Initializing Phoenix Civic Simulation Engine...")
    simulator = UrbanHeatSimulator(n_residents=50000)  # Start smaller for API
    simulator.generate_synthetic_population()
    print(f"✓ Simulator ready with {len(simulator.residents)} synthetic residents")


@app.get("/")
async def root():
    return {
        "name": "Phoenix Civic Simulation Engine",
        "version": "0.1.0",
        "status": "operational",
        "residents": len(simulator.residents) if simulator else 0
    }


@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "simulator_ready": simulator is not None,
        "population": len(simulator.residents) if simulator else 0
    }


@app.get("/dashboard", response_class=HTMLResponse)
async def serve_dashboard():
    """Serve the interactive dashboard."""
    dashboard_path = Path(__file__).parent / "interface" / "dashboard.html"
    if dashboard_path.exists():
        return HTMLResponse(content=dashboard_path.read_text())
    raise HTTPException(status_code=404, detail="Dashboard not found")


@app.get("/api/vulnerable-areas")
async def get_vulnerable_areas(
    threshold: float = 50.0,
    lat_min: float = 33.3,
    lat_max: float = 33.6,
    lon_min: float = -112.3,
    lon_max: float = -111.8
):
    """Get heat vulnerability data for map display."""
    if not simulator:
        raise HTTPException(status_code=503, detail="Simulator not initialized")
    
    # Filter residents within bounds and above threshold
    areas = []
    for resident in simulator.residents:
        if (lat_min <= resident.lat <= lat_max and 
            lon_min <= resident.lon <= lon_max and
            resident.heat_vulnerability >= threshold):
            
            areas.append({
                "id": resident.id,
                "lat": resident.lat,
                "lon": resident.lon,
                "vulnerability": resident.heat_vulnerability,
                "age": resident.age,
                "income": resident.income,
                "has_ac": resident.has_ac,
                "profile": resident.profile().value
            })
    
    return {
        "count": len(areas),
        "threshold": threshold,
        "areas": areas[:500]  # Limit for performance
    }


@app.post("/api/simulate/intervention")
async def simulate_intervention(request: InterventionRequest) -> SimulationResponse:
    """
    Simulate the impact of a proposed intervention.
    """
    if not simulator:
        raise HTTPException(status_code=503, detail="Simulator not initialized")
    
    # Create intervention scenario
    intervention = InterventionScenario(
        name=request.name,
        intervention_type=request.intervention_type,
        target_area={
            "center_lat": request.target_lat,
            "center_lon": request.target_lon,
            "radius_km": request.radius_km
        },
        implementation_cost=request.budget,
        timeline_months=6
    )
    
    # Run baseline simulation (no intervention)
    sim_baseline = UrbanHeatSimulator(n_residents=5000)
    sim_baseline.generate_synthetic_population()
    baseline_results = sim_baseline.run_scenario(days=90)
    
    # Run intervention simulation
    sim_intervention = UrbanHeatSimulator(n_residents=5000)
    sim_intervention.generate_synthetic_population()
    intervention_results = sim_intervention.run_scenario(
        days=90,
        interventions=[intervention]
    )
    
    # Calculate impact
    baseline_deaths = baseline_results['total_outcomes']['deaths']
    intervention_deaths = intervention_results['total_outcomes']['deaths']
    deaths_prevented = max(0, baseline_deaths - intervention_deaths)
    
    return SimulationResponse(
        deaths_prevented=deaths_prevented,
        er_visits_prevented=baseline_results['total_outcomes']['er_visits'] - intervention_results['total_outcomes']['er_visits'],
        cost_per_life_saved=request.budget / max(deaths_prevented, 1),
        roi_percent=(deaths_prevented * 2500000 / request.budget * 100) if deaths_prevented > 0 else 0,
        vulnerable_population_affected=1000,  # Simplified
        intervention_effectiveness={
            "heat_reduction_c": 2.5,
            "coverage_percent": 85.0,
            "behavioral_adoption": 0.7
        }
    )


@app.get("/api/interventions/types")
async def get_intervention_types():
    """Get available intervention types."""
    return {
        "tree_canopy": {
            "name": "Tree Canopy Expansion",
            "description": "Increase neighborhood tree coverage",
            "cost_per_tree": 500,
            "cooling_effect_c": 2.0,
            "timeline_years": 5,
            "maintenance_annual": 50
        },
        "cooling_center": {
            "name": "Emergency Cooling Center",
            "description": "Establish emergency cooling center",
            "cost_per_center": 500000,
            "capacity_people": 200,
            "timeline_months": 3,
            "operating_cost_daily": 2000
        },
        "transit_cooling": {
            "name": "Transit Cooling Buses",
            "description": "Deploy air-conditioned transit buses",
            "cost_per_bus": 300000,
            "riders_per_day": 500,
            "timeline_months": 1,
            "operating_cost_daily": 800
        },
        "cool_roofs": {
            "name": "Cool Roof Program",
            "description": "Install reflective roofing",
            "cost_per_sqft": 3,
            "cooling_effect_c": 5.0,
            "timeline_months": 6,
            "lifespan_years": 20
        }
    }


@app.get("/api/stats/summary")
async def get_summary_stats():
    """Get high-level summary statistics."""
    if not simulator:
        raise HTTPException(status_code=503, detail="Simulator not initialized")
    
    # Calculate stats from current population
    total_pop = len(simulator.residents)
    
    vulnerable_count = sum(1 for r in simulator.residents if r.heat_vulnerability > 50)
    extreme_vulnerable = sum(1 for r in simulator.residents if r.heat_vulnerability > 75)
    
    no_ac_count = sum(1 for r in simulator.residents if not r.has_ac)
    elderly_count = sum(1 for r in simulator.residents if r.age > 65)
    outdoor_workers = sum(1 for r in simulator.residents if r.works_outdoors)
    
    return {
        "total_population": total_pop,
        "vulnerable_population": vulnerable_count,
        "extreme_vulnerable": extreme_vulnerable,
        "percent_vulnerable": round(vulnerable_count / total_pop * 100, 1),
        "without_ac": no_ac_count,
        "elderly": elderly_count,
        "outdoor_workers": outdoor_workers,
        "average_vulnerability": round(
            sum(r.heat_vulnerability for r in simulator.residents) / total_pop, 1
        )
    }


@app.post("/api/simulate/batch")
async def run_batch_simulation(interventions: List[InterventionRequest]):
    """
    Run simulation with multiple interventions.
    """
    if not simulator:
        raise HTTPException(status_code=503, detail="Simulator not initialized")
    
    # Convert to intervention scenarios
    scenarios = [
        InterventionScenario(
            name=req.name,
            intervention_type=req.intervention_type,
            target_area={
                "center_lat": req.target_lat,
                "center_lon": req.target_lon,
                "radius_km": req.radius_km
            },
            implementation_cost=req.budget,
            timeline_months=6
        )
        for req in interventions
    ]
    
    # Run simulation
    results = simulator.run_scenario(
        days=90,
        interventions=scenarios
    )
    
    return {
        "interventions_applied": len(scenarios),
        "total_cost": sum(req.budget for req in interventions),
        "deaths": results['total_outcomes']['deaths'],
        "er_visits": results['total_outcomes']['er_visits'],
        "heat_illness_events": results['total_outcomes']['heat_illness'],
        "daily_history": results['history'][:30]  # First 30 days
    }


if __name__ == "__main__":
    print("Starting Phoenix Civic Simulation Engine API...")
    print("Dashboard available at: http://localhost:8000/dashboard")
    uvicorn.run(app, host="0.0.0.0", port=8000)