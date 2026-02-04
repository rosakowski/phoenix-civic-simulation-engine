# [IMPLEMENT] Advanced Map Interactions & Visualization System

**Priority:** High
**Complexity:** High
**Estimated Time:** 8-10 hours

## Context
Current dashboard has basic map display. City planners need sophisticated visualization tools including 3D building views, time-lapse animations, interactive placement tools, and multi-layer data overlays.

## Current State
- Static heat vulnerability circles
- Basic click interactions
- Single time point visualization

## Target State
Professional-grade urban planning visualization with 3D buildings, time-based animations, interactive design tools, and scenario comparison.

## Technical Requirements

### 1. 3D Building Visualization

**Integrate Cesium.js or Three.js for 3D:**
```javascript
// Building footprints with height data
const buildings = await fetch('/api/buildings/footprints');

buildings.forEach(building => {
  const entity = viewer.entities.add({
    polygon: {
      hierarchy: Cesium.Cartesian3.fromDegreesArray(building.coordinates),
      extrudedHeight: building.height,
      material: getMaterialByType(building.type),
      outline: true,
      outlineColor: Cesium.Color.BLACK
    }
  });
});
```

**Building Types & Colors:**
- Residential (light blue)
- Commercial (gray)
- Industrial (dark gray)
- Schools (yellow)
- Hospitals (red)
- Parks (green)

**Roof Visualization:**
- Show current roof type (dark = hot, light = cool)
- Toggle to show "after cool roof" effect
- Heat retention visualization

### 2. Time-Lapse Animation System

**Heat Throughout the Day:**
```javascript
// Animate from 6am to midnight
const timeSlider = document.getElementById('time-slider');

function updateHeatMap(hour) {
  // Solar angle calculation
  const sunAngle = calculateSolarAngle(hour, date, lat, lon);
  
  // Building shadows
  const shadows = calculateShadows(buildings, sunAngle);
  
  // Surface temperatures
  const surfaceTemps = calculateSurfaceTemps(sunAngle, shadows, materialTypes);
  
  // Update heat map layer
  heatMapLayer.setData(surfaceTemps);
}

// Animation loop
let currentHour = 6;
setInterval(() => {
  currentHour = (currentHour + 0.5) % 24; // 30-min increments
  updateHeatMap(currentHour);
  timeSlider.value = currentHour;
}, 500); // Update every 500ms
```

**Time Controls:**
- Play/Pause animation
- Scrub timeline
- Speed control (1x, 2x, 4x)
- Date selector (compare summer vs winter)

### 3. Interactive Design Tools

**Intervention Drawing Tools:**

**Tree Corridor Tool:**
```javascript
// Line drawing mode
map.on('click', (e) => {
  if (drawingMode === 'tree-corridor') {
    corridorPoints.push(e.latlng);
    
    if (corridorPoints.length >= 2) {
      // Auto-space trees along line
      const trees = autoSpaceTrees(corridorPoints, spacing=30);
      trees.forEach(tree => addTreeMarker(tree));
      
      // Show cost preview
      updateCostPreview(trees.length, selectedSpecies);
    }
  }
});
```

**Cooling Center Placement:**
```javascript
// Click to place with coverage preview
map.on('click', (e) => {
  if (placingMode === 'cooling-center') {
    const center = L.marker(e.latlng).addTo(map);
    
    // Show 0.5-mile walking radius
    const coverage = L.circle(e.latlng, {
      radius: 800, // meters
      color: 'blue',
      fillColor: 'blue',
      fillOpacity: 0.2
    }).addTo(map);
    
    // Calculate coverage stats
    const stats = calculateCoverage(e.latlng, 800);
    showTooltip(`Population covered: ${stats.population}`);
  }
});
```

**Polygon Tools for Groves/Zones:**
- Draw polygon → auto-fill with pattern
- Adjust density slider
- Preview before confirming

### 4. Multi-Layer Data Overlays

**Layer Management System:**

```javascript
const layers = {
  'heat-vulnerability': {
    data: vulnerabilityData,
    visible: true,
    opacity: 0.7,
    zIndex: 1
  },
  'population-density': {
    data: populationData,
    visible: false,
    opacity: 0.5,
    zIndex: 2
  },
  'transit-routes': {
    data: transitData,
    visible: true,
    opacity: 1.0,
    zIndex: 3
  },
  'building-footprints': {
    data: buildingData,
    visible: false,
    opacity: 0.8,
    zIndex: 4
  },
  'interventions': {
    data: interventionData,
    visible: true,
    opacity: 1.0,
    zIndex: 5
  }
};

// Layer control UI
function createLayerControl() {
  Object.entries(layers).forEach(([name, config]) => {
    const checkbox = document.createElement('input');
    checkbox.type = 'checkbox';
    checkbox.checked = config.visible;
    checkbox.onchange = () => toggleLayer(name, checkbox.checked);
    
    const opacity = document.createElement('input');
    opacity.type = 'range';
    opacity.min = 0;
    opacity.max = 1;
    opacity.step = 0.1;
    opacity.value = config.opacity;
    opacity.oninput = () => setLayerOpacity(name, opacity.value);
  });
}
```

**Available Layers:**
1. Heat vulnerability (census tracts)
2. Population density (block groups)
3. Surface temperature (satellite thermal)
4. Tree canopy coverage (existing)
5. Transit routes (bus, light rail)
6. Building footprints (3D when zoomed)
7. Cooling center coverage (walking radii)
8. Intervention proposals (editable)
9. Historical heat deaths (aggregated)
10. Solar exposure (insolation maps)

### 5. Before/After Comparison Slider

**Swipe Tool:**
```javascript
// Split screen comparison
const beforeLayer = L.layerGroup([baselineHeatMap]);
const afterLayer = L.layerGroup([interventionHeatMap]);

const swipeControl = L.control.sideBySide(beforeLayer, afterLayer);
swipeControl.addTo(map);

// Update stats on drag
swipeControl.on('drag', (e) => {
  const splitPosition = e.value; // 0-1
  updateComparisonStats(splitPosition);
});
```

**Scenario Comparison:**
- Side-by-side maps
- Synchronized zoom/pan
- Hover to see same location on both
- Stats comparison panel

### 6. Heat Flow Animation

**Show How Heat Moves:**
```javascript
// Particle system showing heat flow
const particles = [];

function animateHeatFlow() {
  // Wind direction + temperature gradient
  const wind = getWindData();
  const tempGradient = calculateGradient(surfaceTemps);
  
  particles.forEach(particle => {
    // Move particle based on wind and heat
    particle.x += wind.x * 0.1 + tempGradient.x * 0.05;
    particle.y += wind.y * 0.1 + tempGradient.y * 0.05;
    
    // Color based on temperature
    particle.color = getTempColor(particle.temp);
  });
  
  requestAnimationFrame(animateHeatFlow);
}
```

**Urban Heat Island Effect:**
- Show heat radiating from concrete areas
- Cool air flowing from parks
- Building canyon heat trapping

### 7. Population Flow Animation

**Where People Go:**
```javascript
// Origin-destination flow lines
const flows = [
  {from: [33.45, -112.07], to: [33.46, -112.08], volume: 500},
  // ... more flows
];

flows.forEach(flow => {
  const line = L.polyline([flow.from, flow.to], {
    color: 'rgba(255, 100, 100, 0.6)',
    weight: flow.volume / 100
  }).addTo(map);
  
  // Animated flow
  animateFlow(line);
});
```

**Morning Commute:**
- Residential → Commercial zones
- High-traffic corridors light up

**Midday Activity:**
- Commercial centers peak
- Lunch rush patterns

**Evening Return:**
- Reverse commute
- Evening services (groceries, etc.)

### 8. Measurement Tools

**Distance & Area:**
```javascript
// Ruler tool
let rulerPoints = [];

map.on('click', (e) => {
  if (tool === 'ruler') {
    rulerPoints.push(e.latlng);
    
    if (rulerPoints.length === 2) {
      const distance = calculateDistance(rulerPoints[0], rulerPoints[1]);
      showMeasurement(`Distance: ${distance.toFixed(2)} km`);
    }
  }
});

// Area tool
if (tool === 'area') {
  const polygon = L.polygon(points).addTo(map);
  const area = calculateArea(polygon);
  showMeasurement(`Area: ${area.toFixed(2)} sq km`);
}
```

**Coverage Calculations:**
- Click point → show radius
- Draw polygon → calculate area + population
- Measure walking distances

## Implementation Steps

1. **Set up Cesium/Three.js** - 3D building rendering
2. **Time animation system** - Solar angle, shadows, heat progression
3. **Drawing tools** - Line, polygon, point placement
4. **Layer management** - Toggle, opacity, z-index
5. **Comparison tools** - Side-by-side, before/after slider
6. **Particle systems** - Heat flow, population flow
7. **Measurement tools** - Distance, area, coverage
8. **Performance optimization** - LOD, culling, progressive loading

## Libraries Needed

```json
{
  "cesium": "^1.110.0",
  "three": "^0.160.0",
  "d3": "^7.8.5",
  "turf": "^6.5.0"
}
```

## Performance Targets

- 60fps animation
- <2s initial load
- Smooth zoom to building level
- Handle 100k+ buildings
- Mobile responsive

## Acceptance Criteria

- [ ] 3D building visualization
- [ ] Time-lapse heat animation (6am-midnight)
- [ ] Interactive tree corridor drawing tool
- [ ] Cooling center placement with coverage preview
- [ ] Multi-layer overlay system (10+ layers)
- [ ] Before/after comparison slider
- [ ] Heat flow particle animation
- [ ] Population flow visualization
- [ ] Distance and area measurement tools
- [ ] Layer opacity controls
- [ ] Responsive design (works on tablet)

@Claude-Code: This is our most complex visualization task. Consider breaking into smaller PRs (3D buildings, then animations, then tools). Focus on performance from day one!