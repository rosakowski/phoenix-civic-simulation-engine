# [IMPLEMENT] Granular Cooling Center Planning Tool

**Priority:** High
**Complexity:** High
**Estimated Time:** 6-8 hours

## Context
City planners need sophisticated tools to determine WHERE to place cooling centers, not just IF. Current implementation is too coarse.

## Current State
- Single toggle: "Deploy Cooling Centers"
- No location specificity
- No coverage analysis
- No population data integration

## Target State
Interactive tool for optimizing cooling center placement with population density, transit access, vulnerability data, and coverage gap analysis.

## Technical Requirements

### 1. Multi-Layer Data Integration

**Data Sources to Integrate:**
- Population density (census block groups)
- Heat vulnerability index
- Transit stops (bus, light rail)
- Foot traffic patterns (near grocery, libraries, services)
- Homeless shelter locations
- Existing cooling centers
- AC access data (rental units without central air)
- Electrical grid capacity
- ADA accessibility
- Parking availability

**Backend Endpoint:** `/api/cooling-centers/location-data`

**Output Format:**
```json
{
  "grid_cells": [
    {
      "lat": 33.45,
      "lon": -112.07,
      "population": 4500,
      "vulnerability_score": 68.5,
      "ac_access_percent": 45,
      "transit_stops_nearby": 3,
      "nearest_cooling_center_km": 2.3,
      "homeless_population_estimate": 120,
      "foot_traffic_score": 7.2,
      "priority_score": 85.3
    }
  ]
}
```

### 2. Three Cooling Center Types

**Type 1: 24/7 Emergency Center**
- Cost: $500K setup, $2K/day operations
- Capacity: 200 people
- Staff: Medical + security
- Features: Cots, meals, showers
- Activation: >110°F forecast

**Type 2: Extended Hours Library**
- Cost: $50K retrofit, $500/day operations  
- Capacity: 100 people
- Staff: Librarians + volunteers
- Features: Books, WiFi, quiet space
- Hours: 8am-midnight during heat emergency

**Type 3: Mobile Cooling Station**
- Cost: $150K vehicle, $300/day operations
- Capacity: 40 people
- Staff: Driver + aide
- Features: Mobile, flexible location
- Deploy: Follows demand

### 3. Interactive Map Features

**Heat Vulnerability Overlay:**
- Color gradient: Green (low) → Red (extreme)
- Click for detailed tract breakdown
- Toggle layers: Age, income, AC access

**Coverage Radius Visualization:**
- 0.5-mile walking radius circles
- Show population within each circle
- Highlight coverage gaps (areas not covered)
- Calculate "heat exposure minutes" for uncovered areas

**Smart Placement Suggestions:**
- AI suggests top 10 locations
- Scores each by: population, vulnerability, accessibility
- Compare scenarios: 3 centers vs 5 centers
- Budget optimization: Maximize coverage per dollar

### 4. Coverage Gap Analysis

**Algorithm:**
```python
def find_coverage_gaps(centers: List[CoolingCenter], 
                       population_grid: List[GridCell]) -> List[Gap]:
    """
    Find areas with high vulnerability but no cooling center access.
    """
    gaps = []
    for cell in population_grid:
        if cell.vulnerability_score > 70:
            nearest_center = find_nearest_center(cell, centers)
            if nearest_center.distance_km > 0.8:  # 0.8km = ~10min walk
                gaps.append({
                    "location": cell,
                    "population_at_risk": cell.population,
                    "distance_to_nearest": nearest_center.distance_km,
                    "priority": calculate_priority(cell)
                })
    return sorted(gaps, key=lambda x: x.priority, reverse=True)
```

**Visualization:**
- Red zones = Coverage gaps
- Blue pins = Existing/proposed centers  
- Heatmap = Combined vulnerability + gap severity

### 5. Foot Traffic Pattern Analysis

**Data Integration:**
- Grocery store locations (high foot traffic)
- Library hours and visitation
- Community center schedules
- Bus stop ridership data
- Light rail stations

**Heatmaps:**
- Morning patterns (commute times)
- Midday patterns (shopping, services)
- Evening patterns (return home)
- Overlay with temperature curves

**Optimization:**
- Place centers where people ALREADY go
- Maximize "natural" foot traffic
- Reduce need for outreach/marketing

### 6. Implementation Timeline

**Gantt Chart Component:**
- Setup phases: Permitting, renovation, staffing
- Activation triggers: Temperature forecasts
- Seasonal operations: May-September focus
- Phased rollout: Priority zones first

**Critical Path Analysis:**
- Which centers must open first?
- Dependencies: Power, permits, staff training
- Risk factors: Delays, budget overruns

### 7. Cost-Benefit Deep Dive

**Per-Center Calculations:**
```
Setup Costs:
- Building lease/purchase: $____
- HVAC installation: $____
- Furniture & equipment: $____
- ADA compliance: $____
- Total Setup: $____

Operating Costs (per heat emergency day):
- Staff (medical + support): $____
- Utilities (electricity, water): $____
- Supplies (water, snacks, cots): $____
- Security: $____
- Daily Total: $____

Benefits:
- Lives saved: X people
- ER visits prevented: Y visits
- Energy assistance reduced: $Z
- Societal value: $____

ROI: ____%
Cost per life saved: $____
```

## Implementation Steps

1. **Data pipeline** - Integrate population, transit, vulnerability data
2. **Backend API** - Grid analysis, coverage calculations, optimization
3. **Map visualization** - Heat vulnerability overlay, coverage circles
4. **Interactive tools** - Click to place, drag to move, coverage analysis
5. **Cost calculator** - Per-center and city-wide budget projections
6. **Timeline component** - Gantt chart, critical path, seasonal planning

## Frontend Components

**New Dashboard Section: "Cooling Center Planner"**

```html
<div id="cooling-center-planner">
  <!-- Layer toggles -->
  <div class="layer-controls">
    <label><input type="checkbox" id="show-vulnerability"> Heat Vulnerability</label>
    <label><input type="checkbox" id="show-population"> Population Density</label>
    <label><input type="checkbox" id="show-transit"> Transit Stops</label>
    <label><input type="checkbox" id="show-gaps"> Coverage Gaps</label>
  </div>
  
  <!-- Center type selector -->
  <div class="center-type-selector">
    <button class="center-type" data-type="emergency">24/7 Emergency Center</button>
    <button class="center-type" data-type="library">Extended Hours Library</button>
    <button class="center-type" data-type="mobile">Mobile Station</button>
  </div>
  
  <!-- Coverage analysis -->
  <div class="coverage-stats">
    <div>Population Covered: <span id="pop-covered">0</span></div>
    <div>Coverage Gaps: <span id="coverage-gaps">0</span> zones</div>
    <div>Estimated Daily Capacity: <span id="total-capacity">0</span></div>
  </div>
  
  <!-- Budget tracker -->
  <div class="budget-tracker">
    <div>Setup Costs: $<span id="setup-costs">0</span></div>
    <div>Daily Operations: $<span id="daily-ops">0</span></div>
  </div>
</div>
```

## Acceptance Criteria

- [ ] Heat vulnerability overlay on map
- [ ] Three cooling center types with different specs
- [ ] Click-to-place with drag-to-move
- [ ] Coverage radius visualization (0.5-mile walk)
- [ ] Coverage gap analysis highlighting underserved areas
- [ ] Population density integration
- [ ] Transit stop proximity data
- [ ] Cost breakdown per center type
- [ ] Budget accumulator as centers are added
- [ ] AI suggestions for optimal placement
- [ ] Compare multiple scenarios (3 vs 5 vs 10 centers)

## API Endpoints

```python
@app.get("/api/cooling-centers/location-data")
async def get_location_data(
    lat_min: float, lat_max: float, 
    lon_min: float, lon_max: float
) -> List[LocationCell]:
    """Get grid cells with population, vulnerability, transit data."""

@app.post("/api/cooling-centers/analyze-coverage")
async def analyze_coverage(centers: List[CoolingCenterLocation]) -> CoverageAnalysis:
    """Analyze coverage given proposed center locations."""

@app.post("/api/cooling-centers/optimize-placement")
async def optimize_placement(
    budget: float, 
    target_coverage_percent: float
) -> OptimizationResult:
    """Suggest optimal center locations given budget constraints."""

@app.get("/api/cooling-centers/cost-estimate")
async def get_cost_estimate(
    center_type: str, 
    count: int
) -> CostEstimate:
    """Calculate setup and operating costs for cooling centers."""
```

## Data Sources

- **Population**: US Census Bureau (census block groups)
- **Transit**: Valley Metro GTFS data
- **Vulnerability**: ASU Heat Vulnerability Index
- **Buildings**: Phoenix Open Data (libraries, community centers)
- **Homeless**: Maricopa Association of Governments point-in-time count

## Performance Considerations

- Grid resolution: 0.5km x 0.5km cells
- Cache location data (updates daily max)
- Progressive loading (load visible area first)
- Spatial indexing for fast nearest-neighbor queries

@Claude-Code: This is a complex feature requiring data integration, geospatial analysis, and interactive visualization. Break it into smaller PRs if needed!