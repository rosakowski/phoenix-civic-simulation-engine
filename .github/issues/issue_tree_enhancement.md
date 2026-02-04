# [IMPLEMENT] Enhanced Tree Canopy System with Species Database

**Priority:** High
**Complexity:** Medium
**Estimated Time:** 4-6 hours

## Context
The current "Plant 1,000 Trees" intervention is too simplistic. City planners need detailed species selection, cost breakdowns, and growth projections to make informed decisions.

## Current State
- Single "tree canopy" toggle
- No species differentiation
- No growth timeline
- No water usage data

## Target State
Comprehensive tree planting system with Phoenix-appropriate species, costs, and interactive planning tools.

## Technical Requirements

### 1. Tree Species Database
Create `pcse/data/tree_species.json`:

```json
{
  "desert_willow": {
    "name": "Desert Willow",
    "scientific_name": "Chilopsis linearis",
    "cost_planting": 85,
    "cost_3year_maintenance": 120,
    "cost_annual_maintenance": 25,
    "mature_canopy_ft": 15,
    "years_to_effective_shade": 3,
    "water_usage_gallons_per_year": 450,
    "native": true,
    "drought_tolerant": true,
    "max_lifespan_years": 50,
    "cooling_effect_c": 1.5,
    "suitable_locations": ["residential", "parks", "medians"],
    "avoid_near": ["power_lines", "septic_systems"]
  },
  "palo_verde": {
    "name": "Palo Verde",
    "scientific_name": "Parkinsonia spp.",
    "cost_planting": 120,
    "cost_3year_maintenance": 150,
    "cost_annual_maintenance": 30,
    "mature_canopy_ft": 25,
    "years_to_effective_shade": 5,
    "water_usage_gallons_per_year": 200,
    "native": true,
    "drought_tolerant": true,
    "max_lifespan_years": 80,
    "cooling_effect_c": 2.0,
    "suitable_locations": ["parks", "medians", "commercial"],
    "avoid_near": ["sidewalks"]
  },
  "mesquite": {
    "name": "Velvet Mesquite",
    "scientific_name": "Prosopis velutina",
    "cost_planting": 150,
    "cost_3year_maintenance": 180,
    "cost_annual_maintenance": 40,
    "mature_canopy_ft": 30,
    "years_to_effective_shade": 7,
    "water_usage_gallons_per_year": 300,
    "native": true,
    "drought_tolerant": true,
    "max_lifespan_years": 100,
    "cooling_effect_c": 2.5,
    "suitable_locations": ["parks", "large_median", "schools"],
    "avoid_near": ["foundations", "underground_utilities"]
  },
  "arizona_ash": {
    "name": "Arizona Ash",
    "scientific_name": "Fraxinus velutina",
    "cost_planting": 200,
    "cost_3year_maintenance": 250,
    "cost_annual_maintenance": 60,
    "mature_canopy_ft": 40,
    "years_to_effective_shade": 10,
    "water_usage_gallons_per_year": 800,
    "native": true,
    "drought_tolerant": false,
    "max_lifespan_years": 60,
    "cooling_effect_c": 3.5,
    "suitable_locations": ["parks", "large_open_areas"],
    "avoid_near": []
  }
}
```

### 2. Planting Pattern Templates
Add to simulation:

**Pattern Types:**
- `corridor`: Trees along pedestrian routes (spacing: every 30ft)
- `grove`: Clustered group (5-20 trees, 15ft spacing)
- `avenue`: Street tree line (both sides, every 25ft)
- `park_expansion`: Large area planting (mixed species)

### 3. Interactive Map Tools
Frontend enhancements:

**Tree Placement Tools:**
- Single tree click-to-place
- Line tool for corridors (click start → click end → auto-space trees)
- Polygon tool for groves (draw area → fill with optimal spacing)
- Drag to move individual trees
- Right-click to delete

**Visual Feedback:**
- Tree icons show species type
- Canopy radius circles (grow over time)
- Coverage percentage calculator
- Cost accumulator (updates as you add trees)

### 4. Cost Calculator
Backend endpoint `/api/trees/calculate-cost`:

**Input:**
```json
{
  "trees": [
    {"species": "desert_willow", "count": 50},
    {"species": "palo_verde", "count": 30}
  ],
  "timeline_years": 20
}
```

**Output:**
```json
{
  "initial_cost": 7850,
  "maintenance_3year": 6900,
  "maintenance_annual_average": 2150,
  "total_20year_cost": 59250,
  "total_water_usage_gallons_annual": 28500,
  "canopy_coverage_year_5": 1250,
  "canopy_coverage_year_10": 2450,
  "canopy_coverage_year_20": 3200,
  "cooling_effect_c": 2.1,
  "lives_saved_estimate": 3.2
}
```

### 5. Growth Timeline Visualization
Add to dashboard:

**Year-by-Year Projection:**
- Slider: 0-20 years
- Map updates: Canopy circles grow
- Stats update: Coverage %, cooling effect
- Photos: Show representative tree at each stage

## Implementation Steps

1. **Create data structure** - Tree species JSON
2. **Backend endpoints** - Cost calculator, species API
3. **Frontend tree selector** - Dropdown with species info cards
4. **Map drawing tools** - Line, polygon for mass planting
5. **Timeline visualization** - Year slider with canopy growth
6. **Cost dashboard** - Real-time budget tracker

## Acceptance Criteria

- [ ] 4+ Phoenix-appropriate tree species in database
- [ ] Click-to-place single trees on map
- [ ] Line tool for corridor planting
- [ ] Polygon tool for grove planting
- [ ] Cost calculator with 20-year projection
- [ ] Timeline slider showing canopy growth
- [ ] Water usage estimates per species
- [ ] Coverage percentage calculator

## API Endpoints Needed

```python
@app.get("/api/trees/species")
async def get_tree_species() -> List[TreeSpecies]:
    """Return all available tree species with details."""

@app.post("/api/trees/calculate")
async def calculate_tree_project(request: TreeProjectRequest) -> TreeProjectResult:
    """Calculate costs and benefits for a tree planting project."""

@app.post("/api/trees/placement-optimize")
async def optimize_tree_placement(request: PlacementRequest) -> List[TreeLocation]:
    """Suggest optimal tree locations given area and goals."""
```

## Related Files
- `pcse/interface/dashboard.html` - Add tree tools
- `pcse/api.py` - Add endpoints
- `pcse/simulation/interventions.py` - Enhance tree simulation

## Notes
- Use Phoenix native species when possible
- Water usage is critical in desert climate
- Consider root systems vs. underground utilities
- Prioritize shade over speed of growth

@Claude-Code: Please implement this comprehensive tree planning system!