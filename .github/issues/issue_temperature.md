# [IMPLEMENT] Connect Dashboard to Real-Time Weather Data

**Priority:** Medium

## Context
The dashboard currently shows a hardcoded temperature of 108°F, but it should display today's actual high temperature for Phoenix, AZ. This is important for accurate simulation and user trust in the system.

## Current Behavior
- Dashboard shows: 108°F (hardcoded)
- Today's actual: 84°F high / 52°F low (Feb 4, 2026)

## Specification
Replace the hardcoded temperature with real-time data from NOAA Weather API.

### Technical Requirements
1. **API Integration**: Use NOAA Weather API (no API key required)
   - Endpoint: `https://api.weather.gov/gridpoints/PSR/52,75/forecast`
   - Phoenix grid coordinates: PSR/52,75

2. **Implementation Location**: 
   - Backend: Add to `pcse/api.py`
   - Frontend: Update `pcse/interface/dashboard.html`

3. **Data to Display**:
   - Today's forecasted high temperature
   - Optional: Current temperature, conditions

4. **Update Frequency**: 
   - Fetch on page load
   - Refresh every 30 minutes

5. **Error Handling**:
   - If API fails, show last known temperature
   - Display error message to user if data is stale (>1 hour)

### Acceptance Criteria
- [ ] Dashboard shows actual Phoenix temperature on load
- [ ] Temperature updates every 30 minutes
- [ ] Graceful error handling if API is unavailable
- [ ] Temperature data includes timestamp
- [ ] Code includes tests for API integration

### Code Guidance
```python
# In pcse/api.py
import httpx
from datetime import datetime

@app.get("/api/weather/current")
async def get_current_weather():
    """Fetch current Phoenix weather from NOAA."""
    url = "https://api.weather.gov/gridpoints/PSR/52,75/forecast"
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, timeout=10.0)
            response.raise_for_status()
            data = response.json()
            
            # Extract today's high
            periods = data.get('properties', {}).get('periods', [])
            if periods:
                today = periods[0]
                return {
                    "temperature": today['temperature'],
                    "unit": today['temperatureUnit'],
                    "forecast": today['shortForecast'],
                    "timestamp": datetime.now().isoformat()
                }
        except Exception as e:
            # Return fallback
            return {"temperature": 85, "unit": "F", "error": str(e)}
```

```javascript
// In dashboard.html
async function updateWeather() {
    try {
        const response = await fetch('/api/weather/current');
        const data = await response.json();
        document.getElementById('temp-display').textContent = 
            `${data.temperature}°${data.unit}`;
    } catch (error) {
        console.error('Failed to fetch weather:', error);
    }
}

// Call on load and every 30 minutes
updateWeather();
setInterval(updateWeather, 30 * 60 * 1000);
```

## Testing
- [ ] Verify NOAA API returns valid data
- [ ] Test with network offline (error handling)
- [ ] Verify temperature updates after 30 minutes
- [ ] Check timestamp is current

## Notes
- NOAA API is free and doesn't require authentication
- Consider caching responses to reduce API calls
- Future enhancement: Add weather alerts/warnings

## Related
- Reference: `pcse/perception/data_fetcher.py` has NOAAWeatherFetcher class
- Documentation: https://www.weather.gov/documentation/services-web-api

---
@Claude-Code: Please implement this and comment back when complete!
