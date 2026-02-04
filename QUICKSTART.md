# Quick Start Guide

## Phoenix Civic Simulation Engine (PCSE)

### Prerequisites

```bash
# Python 3.9+
python --version

# Install dependencies
pip install -r requirements.txt
```

### Running the API Server

```bash
# Start the simulation API
python pcse/api.py

# Or with uvicorn directly
uvicorn pcse.api:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at:
- **Dashboard**: http://localhost:8000/dashboard
- **API Docs**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

### Running Simulations

```python
from pcse.simulation import UrbanHeatSimulator, InterventionScenario

# Create simulator
sim = UrbanHeatSimulator(n_residents=10000)
sim.generate_synthetic_population()

# Define intervention
intervention = InterventionScenario(
    name="Downtown Cooling Centers",
    intervention_type="cooling_center",
    target_area={'center_lat': 33.45, 'center_lon': -112.07, 'radius_km': 2.0},
    implementation_cost=500000,
    timeline_months=3
)

# Run simulation
results = sim.run_scenario(days=90, interventions=[intervention])

print(f"Deaths prevented: {results['total_outcomes']['deaths']}")
print(f"ER visits prevented: {results['total_outcomes']['er_visits']}")
```

### API Endpoints

#### Get Vulnerable Areas
```bash
curl "http://localhost:8000/api/vulnerable-areas?threshold=50"
```

#### Simulate Intervention
```bash
curl -X POST "http://localhost:8000/api/simulate/intervention" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "South Phoenix Trees",
    "intervention_type": "tree_canopy",
    "target_lat": 33.40,
    "target_lon": -112.10,
    "radius_km": 3.0,
    "budget": 2000000
  }'
```

#### Get Summary Stats
```bash
curl "http://localhost:8000/api/stats/summary"
```

### Development

```bash
# Run tests
pytest pcse/tests/

# Format code
black pcse/

# Check style
flake8 pcse/
```

### Project Structure

```
pcse/
├── perception/          # Data ingestion
│   ├── __init__.py
│   └── data_fetcher.py
├── simulation/          # Core modeling
│   └── __init__.py
├── interface/           # Web dashboard
│   ├── __init__.py
│   └── dashboard.html
├── api.py              # FastAPI server
└── __init__.py
```

### Data Sources

The system can connect to:
- **Phoenix Open Data Portal**: Transit, permits, infrastructure
- **ASU CAP LTER**: Heat vulnerability research data
- **NOAA**: Weather forecasts and historical data

### Human-AI Collaboration

This project is designed for collaborative development:

1. **AI proposes**: Simulations, data patterns, intervention scenarios
2. **Human validates**: Real-world context, ethical considerations, feasibility
3. **Together refine**: Iterative improvement based on outcomes
4. **Both learn**: Model improves, partnership deepens

### License

MIT - Open source for the common good.

---

Built with ❤️ by Ross Sakowski (PharmD) & Astra (AI Agent)