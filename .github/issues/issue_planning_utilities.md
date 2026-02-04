# [IMPLEMENT] New Planning Utilities: Cost Calculator, Equity Analysis & Reports

**Priority:** Medium
**Complexity:** Medium
**Estimated Time:** 5-7 hours

## Context
City planners need decision-support tools beyond the map. Cost optimization, equity analysis, and automated reporting are essential for budget justification and stakeholder communication.

## New Utilities to Build

### 1. Cost-Benefit Calculator

**Purpose:** Given a budget, suggest optimal intervention mix

**Input:**
```json
{
  "budget": 5000000,
  "priority": "lives_saved", // or "cost_effectiveness", "equity"
  "constraints": {
    "max_cooling_centers": 5,
    "tree_budget_max": 2000000,
    "timeline_years": 10
  }
}
```

**Algorithm:**
```python
def optimize_portfolio(budget, priority, constraints):
    """
    Use multi-objective optimization to find best intervention mix.
    """
    interventions = [
        {'type': 'trees', 'cost': 500, 'lives_saved': 0.001, 'coverage': 50},
        {'type': 'cooling_center', 'cost': 500000, 'lives_saved': 5, 'coverage': 10000},
        {'type': 'cool_roofs', 'cost': 5000, 'lives_saved': 0.01, 'coverage': 10},
    ]
    
    # Genetic algorithm or linear programming
    best_portfolio = optimize(
        budget=budget,
        interventions=interventions,
        objective=priority,
        constraints=constraints
    )
    
    return best_portfolio
```

**Output:**
```json
{
  "recommended_mix": [
    {"type": "cooling_center", "count": 4, "cost": 2000000},
    {"type": "trees", "count": 3000, "cost": 1500000},
    {"type": "cool_roofs", "count": 200, "cost": 1000000}
  ],
  "total_cost": 4500000,
  "lives_saved_10yr": 180,
  "cost_per_life_saved": 25000,
  "roi_percent": 850,
  "coverage_percent": 65
}
```

**UI Component:**
- Budget slider ($1M to $50M)
- Priority selector (lives saved / cost effectiveness / equity)
- Constraint inputs
- "Optimize" button
- Results: Recommended mix + pie chart + stats

### 2. Equity Analysis Tool

**Purpose:** Ensure interventions help those who need it most

**Metrics:**
- **Heat Protection Equity Score:** 0-100
  - Compare coverage in high vs low income areas
  - Compare by race/ethnicity
  - Compare by age demographics

- **Gini Coefficient of Heat Protection:**
  - 0 = perfect equity
  - 1 = maximum inequity
  - Track improvement over time

- **Disparate Impact Analysis:**
  - Does this plan disproportionately benefit one group?
  - Are vulnerable populations prioritized?

**Visualization:**
```javascript
// Equity dashboard
const equityData = {
  income_quintiles: [15, 22, 35, 48, 62], // protection % by income
  racial_groups: {
    "white": 58,
    "hispanic": 42,
    "black": 38,
    "asian": 55
  },
  gini_coefficient: 0.23
};

// Bar chart by income
// Bar chart by race
// Gini coefficient gauge
// "Equity Score": 73/100
```

**Alerts:**
- "Warning: Low-income areas receiving 40% less protection"
- "Suggestion: Add 2 cooling centers in high-vulnerability, low-income zones"

### 3. Scenario Comparison Tool

**Purpose:** Compare multiple intervention strategies side-by-side

**Features:**
- Save scenarios with names
- Compare up to 3 scenarios simultaneously
- Trade-off curves (cost vs lives saved)
- Pareto frontier visualization

**UI:**
```
Scenario A: "Aggressive Trees"     Scenario B: "Cooling Centers Focus"
Cost: $5M                          Cost: $5M
Lives Saved: 120                   Lives Saved: 180
Coverage: 45%                      Coverage: 65%
Equity Score: 68                   Equity Score: 82

[Detailed comparison table]
[Trade-off curve chart]
```

### 4. Auto-Generated Reports

**Purpose:** One-click reports for city council, media, stakeholders

**Report Types:**

**A. Executive Summary (1 page)**
- Problem statement
- Proposed solution overview
- Key numbers (lives saved, cost, ROI)
- Visual map highlight

**B. Technical Report (10-20 pages)**
- Methodology explanation
- Data sources
- Detailed simulation results
- Sensitivity analysis
- Limitations and caveats

**C. Budget Justification**
- Cost breakdown by intervention
- Comparison to alternatives
- Funding sources
- Timeline with milestones

**D. Equity Impact Statement**
- Demographic analysis
- Environmental justice considerations
- Community engagement plan

**Auto-Generation:**
```python
@app.post("/api/reports/generate")
async def generate_report(request: ReportRequest) -> PDF:
    """
    Generate formatted PDF report.
    """
    # Fetch current scenario data
    scenario_data = get_scenario_data(request.scenario_id)
    
    # Generate charts
    charts = [
        create_map_visualization(scenario_data),
        create_cost_chart(scenario_data),
        create_lives_saved_chart(scenario_data),
        create_equity_chart(scenario_data)
    ]
    
    # Compile PDF
    pdf = ReportPDF(template=request.report_type)
    pdf.add_title(f"Phoenix Heat Intervention Plan: {scenario_data.name}")
    pdf.add_summary(scenario_data)
    pdf.add_charts(charts)
    pdf.add_methodology()
    pdf.add_data_sources()
    
    return pdf
```

### 5. Implementation Timeline

**Purpose:** Gantt chart showing rollout schedule

**Features:**
- Phased deployment (Year 1, 2, 3...)
- Seasonal considerations (plant trees in fall)
- Critical path analysis
- Dependencies between interventions
- Milestone tracking

**UI:**
- Interactive Gantt chart
- Drag to adjust timelines
- Resource allocation view
- Risk indicators

### 6. Real-Time Monitoring Dashboard

**Purpose:** Track interventions after deployment

**Live Data:**
- Weather station network
- Temperature sensors across city
- Cooling center occupancy
- Heat emergency alerts

**Alerts:**
- "Heat emergency declared: >110°F forecast"
- "Cooling Center at 90% capacity"
- "Tree mortality high in Sector 7 - check irrigation"

## API Endpoints

```python
@app.post("/api/optimize-portfolio")
async def optimize_portfolio(request: OptimizationRequest) -> OptimizationResult:
    """Suggest optimal intervention mix given budget and priorities."""

@app.get("/api/equity-analysis")
async def analyze_equity(scenario_id: str) -> EquityAnalysis:
    """Calculate equity metrics for a given scenario."""

@app.post("/api/scenarios/compare")
async def compare_scenarios(scenario_ids: List[str]) -> ComparisonResult:
    """Compare multiple scenarios side-by-side."""

@app.post("/api/reports/generate")
async def generate_report(request: ReportRequest) -> FileResponse:
    """Generate PDF report for stakeholders."""

@app.get("/api/timeline/{scenario_id}")
async def get_implementation_timeline(scenario_id: str) -> Timeline:
    """Get Gantt chart data for implementation schedule."""

@app.get("/api/monitoring/current")
async def get_monitoring_data() -> MonitoringData:
    """Get real-time temperature and intervention status."""
```

## Frontend Components

**New Dashboard Section: "Planning Tools"**

```html
<div id="planning-tools">
  <!-- Cost Calculator -->
  <div class="tool-panel">
    <h3>Budget Optimizer</h3>
    <input type="range" id="budget-slider" min="1000000" max="50000000">
    <select id="priority-select">
      <option value="lives_saved">Maximize Lives Saved</option>
      <option value="cost_effectiveness">Best ROI</option>
      <option value="equity">Maximize Equity</option>
    </select>
    <button onclick="optimize()">Generate Recommendations</button>
    <div id="optimization-results"></div>
  </div>
  
  <!-- Equity Analysis -->
  <div class="tool-panel">
    <h3>Equity Analysis</h3>
    <div id="equity-score">Equity Score: 73/100</div>
    <canvas id="equity-chart"></canvas>
    <div id="equity-alerts"></div>
  </div>
  
  <!-- Report Generator -->
  <div class="tool-panel">
    <h3>Generate Report</h3>
    <select id="report-type">
      <option value="executive">Executive Summary (1 page)</option>
      <option value="technical">Technical Report</option>
      <option value="budget">Budget Justification</option>
    </select>
    <button onclick="generateReport()">Download PDF</button>
  </div>
</div>
```

## Implementation Order

1. **Cost Calculator** (highest value, medium complexity)
2. **Equity Analysis** (critical for justice, medium complexity)
3. **Report Generator** (needed for stakeholders, high value)
4. **Scenario Comparison** (useful for iteration)
5. **Timeline/Gantt** (nice-to-have for planning)
6. **Real-time Monitoring** (future enhancement)

## Acceptance Criteria

- [ ] Budget optimizer suggests intervention mix
- [ ] Cost per life saved calculation
- [ ] ROI percentage calculation
- [ ] Equity score (0-100) by income/race
- [ ] Gini coefficient of heat protection
- [ ] Disparate impact warnings
- [ ] Compare 2-3 scenarios side-by-side
- [ ] Generate executive summary PDF
- [ ] Generate technical report PDF
- [ ] Implementation timeline Gantt chart

@Claude-Code: These utilities transform the tool from a visualization into a decision-support system. Start with the cost calculator - it's the highest impact for city planners!