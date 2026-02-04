"""Tests for the main API (pcse/api.py)."""

import pytest
from httpx import AsyncClient, ASGITransport
import sys
from pathlib import Path

# Ensure pcse package is importable
sys.path.insert(0, str(Path(__file__).parent.parent / "pcse"))

import pcse.api as api_module
from pcse.api import app
from pcse.simulation import UrbanHeatSimulator


@pytest.fixture(autouse=True)
def _init_simulator():
    """Ensure the global simulator is initialized for all tests."""
    if api_module.simulator is None:
        api_module.simulator = UrbanHeatSimulator(n_residents=500)
        api_module.simulator.generate_synthetic_population()
    yield


@pytest.fixture
def anyio_backend():
    return "asyncio"


@pytest.mark.anyio
async def test_root():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Phoenix Civic Simulation Engine"
    assert data["version"] == "0.1.0"


@pytest.mark.anyio
async def test_health():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["simulator_ready"] is True


@pytest.mark.anyio
async def test_dashboard_serves_html():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/dashboard")
    assert response.status_code == 200
    assert "Phoenix Civic Simulation Engine" in response.text
    assert "<html" in response.text.lower()


@pytest.mark.anyio
async def test_intervention_types():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/api/interventions/types")
    assert response.status_code == 200
    data = response.json()
    assert "tree_canopy" in data
    assert "cooling_center" in data
    assert "transit_cooling" in data
    assert "cool_roofs" in data


@pytest.mark.anyio
async def test_vulnerable_areas():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/api/vulnerable-areas")
    assert response.status_code == 200
    data = response.json()
    assert "count" in data
    assert "areas" in data


@pytest.mark.anyio
async def test_stats_summary():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/api/stats/summary")
    assert response.status_code == 200
    data = response.json()
    assert "total_population" in data
    assert "vulnerable_population" in data
    assert data["total_population"] > 0


@pytest.mark.anyio
async def test_simulate_intervention():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post("/api/simulate/intervention", json={
            "name": "Test Trees",
            "intervention_type": "tree_canopy",
            "target_lat": 33.45,
            "target_lon": -112.07,
            "radius_km": 1.0,
            "budget": 100000,
        })
    assert response.status_code == 200
    data = response.json()
    assert "deaths_prevented" in data
    assert "cost_per_life_saved" in data
