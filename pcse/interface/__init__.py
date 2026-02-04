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


class InterventionRequest(BaseModel):
    """Request to simulate an intervention scenario."""
    name: str
    intervention_type: str
    target_lat: float
    target_lon: float
    radius_km: float
    budget: float


class SimulationResult(BaseModel):
    """Results from a simulation run."""
    deaths_prevented: int
    er_visits_prevented: int
    cost_per_life_saved: float
    roi_percent: float
    vulnerable_population_affected: int


@app.get("/")
async def root():
    return {
        "message": "Phoenix Civic Simulation Engine",
        "version": "0.1.0",
        "status": "operational"
    }


@app.get("/health")
async def health_check():
    return {"status": "healthy"}


@app.post("/simulate/intervention")
async def simulate_intervention(request: InterventionRequest) -> SimulationResult:
    """
    Simulate the impact of a proposed intervention.
    
    This is where human-AI collaboration happens:
    - AI runs the simulation
    - Human interprets results
    - Together iterate on intervention design
    """
    # TODO: Connect to actual simulation engine
    
    # Placeholder response
    return SimulationResult(
        deaths_prevented=5,
        er_visits_prevented=50,
        cost_per_life_saved=100000.0,
        roi_percent=250.0,
        vulnerable_population_affected=1000
    )


@app.get("/data/vulnerable-populations")
async def get_vulnerable_populations(threshold: float = 50.0):
    """Get census tracts with high heat vulnerability."""
    # TODO: Connect to perception layer
    return {
        "tracts": [
            {"id": "04013010100", "vulnerability": 78.5, "lat": 33.45, "lon": -112.07},
            {"id": "04013010200", "vulnerability": 65.2, "lat": 33.44, "lon": -112.08},
        ]
    }


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