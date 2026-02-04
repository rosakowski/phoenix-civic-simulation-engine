"""
Interface Layer - Human-AI Collaboration Dashboard

FastAPI-based web interface for exploring simulation results
and collaborating on intervention planning.
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import json
import sys
from pathlib import Path

# Ensure parent package is importable
sys.path.append(str(Path(__file__).parent.parent))
from simulation import UrbanHeatSimulator, InterventionScenario
from perception import PhoenixDataPortal

app = FastAPI(
    title="Phoenix Civic Simulation Engine",
    description="Human-AI collaborative urban heat intervention planning",
    version="0.1.0"
)

# CORS for development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global simulation instance
simulator = None
data_portal = None


class InterventionRequest(BaseModel):
    """Request to simulate an intervention scenario."""
    name: str
    intervention_type: str
    target_lat: float
    target_lon: float
    radius_km: float = 1.0
    budget: float


class SimulationResult(BaseModel):
    """Results from a simulation run."""
    deaths_prevented: int
    er_visits_prevented: int
    cost_per_life_saved: float
    roi_percent: float
    vulnerable_population_affected: int


@app.on_event("startup")
async def startup_event():
    """Initialize simulator and data portal on startup."""
    global simulator, data_portal
    simulator = UrbanHeatSimulator(n_residents=10000)
    simulator.generate_synthetic_population()
    data_portal = PhoenixDataPortal()


@app.get("/")
async def root():
    return {
        "message": "Phoenix Civic Simulation Engine",
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


@app.post("/simulate/intervention")
async def simulate_intervention(request: InterventionRequest) -> SimulationResult:
    """
    Simulate the impact of a proposed intervention.

    This is where human-AI collaboration happens:
    - AI runs the simulation
    - Human interprets results
    - Together iterate on intervention design
    """
    if not simulator:
        raise HTTPException(status_code=503, detail="Simulator not initialized")

    intervention = InterventionScenario(
        name=request.name,
        intervention_type=request.intervention_type,
        target_area={
            "center_lat": request.target_lat,
            "center_lon": request.target_lon,
            "radius_km": request.radius_km,
        },
        implementation_cost=request.budget,
        timeline_months=6,
    )

    if not intervention.validate():
        raise HTTPException(
            status_code=400,
            detail=f"Invalid intervention: type must be one of tree_canopy, "
                   f"cooling_center, transit_cooling, cool_roofs; "
                   f"budget must be positive; radius must be 0-50km"
        )

    # Run baseline simulation (no interventions)
    sim_baseline = UrbanHeatSimulator(n_residents=5000)
    sim_baseline.generate_synthetic_population()
    baseline_results = sim_baseline.run_scenario(days=90)

    # Run with-intervention simulation
    sim_intervention = UrbanHeatSimulator(n_residents=5000)
    sim_intervention.generate_synthetic_population()
    intervention_results = sim_intervention.run_scenario(
        days=90, interventions=[intervention]
    )

    baseline_deaths = baseline_results["total_outcomes"]["deaths"]
    intervention_deaths = intervention_results["total_outcomes"]["deaths"]
    deaths_prevented = max(0, baseline_deaths - intervention_deaths)

    baseline_er = baseline_results["total_outcomes"]["er_visits"]
    intervention_er = intervention_results["total_outcomes"]["er_visits"]
    er_prevented = max(0, baseline_er - intervention_er)

    vulnerable_count = sum(
        1 for r in sim_intervention.residents if r.heat_vulnerability > 50
    )

    return SimulationResult(
        deaths_prevented=deaths_prevented,
        er_visits_prevented=er_prevented,
        cost_per_life_saved=request.budget / max(deaths_prevented, 1),
        roi_percent=(deaths_prevented * 2500000 / request.budget * 100)
        if deaths_prevented > 0
        else 0,
        vulnerable_population_affected=vulnerable_count,
    )


@app.get("/data/vulnerable-populations")
async def get_vulnerable_populations(threshold: float = 50.0):
    """Get census tracts with high heat vulnerability."""
    if not simulator:
        raise HTTPException(status_code=503, detail="Simulator not initialized")

    df = simulator.get_vulnerable_populations(threshold=threshold)

    tracts = [
        {
            "id": str(row["id"]),
            "vulnerability": round(row["vulnerability"], 1),
            "lat": round(row["lat"], 6),
            "lon": round(row["lon"], 6),
            "age": row.get("age"),
            "income": row.get("income"),
            "has_ac": row.get("has_ac"),
            "profile": row.get("profile"),
        }
        for _, row in df.iterrows()
    ]

    return {"count": len(tracts), "threshold": threshold, "tracts": tracts[:500]}


@app.get("/interventions/types")
async def get_intervention_types():
    """Get available intervention types and their parameters."""
    return {
        "tree_canopy": {
            "description": "Increase neighborhood tree coverage",
            "cost_per_tree": 500,
            "cooling_effect_c": 2.0,
            "timeline_years": 5
        },
        "cooling_center": {
            "description": "Establish emergency cooling center",
            "cost_per_center": 500000,
            "capacity_people": 200,
            "timeline_months": 3
        },
        "transit_cooling": {
            "description": "Deploy air-conditioned transit buses",
            "cost_per_bus": 300000,
            "riders_per_day": 500,
            "timeline_months": 1
        },
        "cool_roofs": {
            "description": "Install reflective roofing",
            "cost_per_sqft": 3,
            "cooling_effect_c": 5.0,
            "timeline_months": 6
        }
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
