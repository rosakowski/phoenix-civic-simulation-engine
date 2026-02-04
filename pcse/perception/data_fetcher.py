"""
Real data connections for Phoenix Open Data Portal and other sources.
"""

import asyncio
import json
import logging
from pathlib import Path
from typing import Dict, List, Optional
import httpx
import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)


class PhoenixDataFetcher:
    """Fetches real data from Phoenix Open Data Portal."""

    BASE_URL = "https://www.phoenixopendata.com/api/views"

    # Dataset IDs from Phoenix Open Data
    DATASETS = {
        'transit_heat_relief': 'transit-heat-relief',
        'cooling_centers': 'cooling-centers',
        'tree_inventory': 'tree-inventory',
        'building_permits': 'building-permits',
    }

    async def fetch_dataset(self, dataset_id: str) -> Optional[pd.DataFrame]:
        """Fetch a specific dataset by ID."""
        url = f"{self.BASE_URL}/{dataset_id}/rows.json"

        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(url, timeout=30.0)
                response.raise_for_status()
                data = response.json()

                # Convert SODA API response to DataFrame
                if 'data' in data:
                    return pd.DataFrame(data['data'])
                return None
            except Exception as e:
                logger.error(f"Failed to fetch {dataset_id}: {e}")
                return None

    async def fetch_all(self) -> Dict[str, pd.DataFrame]:
        """Fetch all available datasets."""
        results = {}

        for name, dataset_id in self.DATASETS.items():
            logger.info(f"Fetching {name}...")
            df = await self.fetch_dataset(dataset_id)
            if df is not None:
                results[name] = df
                logger.info(f"  ✓ {name}: {len(df)} records")
            else:
                logger.warning(f"  ✗ {name}: Failed to fetch")

        return results


class ASUDataFetcher:
    """Fetches academic research data from ASU.

    Connects to ASU's CAP LTER data portal for the Heat Vulnerability
    Index (HVI) dataset. Falls back to synthetic data if the API is
    unreachable or returns an unexpected format.
    """

    # EDI Data Portal API for CAP LTER HVI dataset
    EDI_PACKAGE_URL = "https://pasta.lternet.edu/package/data/eml/knb-lter-cap/665/2"

    async def fetch_heat_vulnerability(self) -> Optional[pd.DataFrame]:
        """Fetch ASU's Heat Vulnerability Index data.

        Attempts to fetch from the EDI Data Portal (PASTA API).
        Returns None on failure so callers can fall back to synthetic data.
        """
        logger.info("Fetching Heat Vulnerability Index from ASU EDI portal...")

        async with httpx.AsyncClient() as client:
            try:
                # First, list the data entities in this package
                response = await client.get(self.EDI_PACKAGE_URL, timeout=15.0)
                response.raise_for_status()

                # The response contains entity IDs (one per line)
                entity_ids = response.text.strip().split("\n")
                if not entity_ids:
                    logger.warning("No data entities found in ASU HVI package")
                    return None

                # Fetch the first data entity (the main CSV)
                entity_url = entity_ids[0].strip()
                logger.info(f"Fetching HVI data entity: {entity_url}")
                data_response = await client.get(entity_url, timeout=30.0)
                data_response.raise_for_status()

                # Parse CSV content
                from io import StringIO
                df = pd.read_csv(StringIO(data_response.text))
                logger.info(f"✓ Fetched ASU HVI data: {len(df)} records, columns: {list(df.columns)}")
                return df

            except httpx.TimeoutException:
                logger.warning("ASU EDI portal request timed out - using synthetic data")
                return None
            except httpx.HTTPStatusError as e:
                logger.warning(f"ASU EDI portal returned {e.response.status_code} - using synthetic data")
                return None
            except Exception as e:
                logger.warning(f"Failed to fetch ASU HVI data: {e} - using synthetic data")
                return None


class NOAAWeatherFetcher:
    """Fetches weather data from NOAA.

    Uses the weather.gov API for forecasts and the NCDC Climate Data
    Online (CDO) API for historical observations.
    """

    API_BASE = "https://api.weather.gov"
    CDO_BASE = "https://www.ncdc.noaa.gov/cdo-web/api/v2"
    PHOENIX_GRIDPOINT = "52,75"  # Grid coordinates for Phoenix
    PHOENIX_STATION_ID = "GHCND:USW00023183"  # Phoenix Sky Harbor

    def __init__(self, cdo_token: Optional[str] = None):
        self.cdo_token = cdo_token

    async def fetch_forecast(self) -> Optional[Dict]:
        """Fetch 7-day forecast for Phoenix."""
        url = f"{self.API_BASE}/gridpoints/PSR/{self.PHOENIX_GRIDPOINT}/forecast"

        async with httpx.AsyncClient() as client:
            try:
                headers = {"User-Agent": "PhoenixCivicSimulationEngine/0.1"}
                response = await client.get(url, headers=headers, timeout=10.0)
                response.raise_for_status()
                return response.json()
            except Exception as e:
                logger.error(f"Failed to fetch weather forecast: {e}")
                return None

    async def fetch_historical(self, start_date: str, end_date: str) -> Optional[pd.DataFrame]:
        """Fetch historical temperature data from NOAA CDO.

        Args:
            start_date: Start date in YYYY-MM-DD format.
            end_date: End date in YYYY-MM-DD format.

        Returns:
            DataFrame with date, max_temp_f, min_temp_f columns, or None on failure.
        """
        if not self.cdo_token:
            logger.info("No NOAA CDO token configured - generating synthetic historical data")
            return self._generate_synthetic_historical(start_date, end_date)

        logger.info(f"Fetching NOAA historical data: {start_date} to {end_date}")

        async with httpx.AsyncClient() as client:
            try:
                headers = {"token": self.cdo_token}
                params = {
                    "datasetid": "GHCND",
                    "stationid": self.PHOENIX_STATION_ID,
                    "startdate": start_date,
                    "enddate": end_date,
                    "datatypeid": "TMAX,TMIN",
                    "units": "standard",
                    "limit": 1000,
                }
                response = await client.get(
                    f"{self.CDO_BASE}/data",
                    headers=headers,
                    params=params,
                    timeout=15.0,
                )
                response.raise_for_status()
                data = response.json()

                if "results" not in data or not data["results"]:
                    logger.warning("No historical data returned from NOAA CDO")
                    return self._generate_synthetic_historical(start_date, end_date)

                # Pivot from long to wide format
                records = data["results"]
                df = pd.DataFrame(records)
                df["date"] = pd.to_datetime(df["date"]).dt.date
                pivot = df.pivot_table(
                    index="date", columns="datatype", values="value"
                ).reset_index()
                pivot.columns = ["date", "max_temp_f", "min_temp_f"]

                logger.info(f"✓ Fetched {len(pivot)} days of NOAA historical data")
                return pivot

            except httpx.TimeoutException:
                logger.warning("NOAA CDO request timed out - using synthetic data")
                return self._generate_synthetic_historical(start_date, end_date)
            except httpx.HTTPStatusError as e:
                logger.warning(f"NOAA CDO returned {e.response.status_code} - using synthetic data")
                return self._generate_synthetic_historical(start_date, end_date)
            except Exception as e:
                logger.warning(f"Failed to fetch NOAA historical data: {e} - using synthetic data")
                return self._generate_synthetic_historical(start_date, end_date)

    def _generate_synthetic_historical(
        self, start_date: str, end_date: str
    ) -> pd.DataFrame:
        """Generate realistic synthetic historical temperature data for Phoenix."""
        dates = pd.date_range(start_date, end_date, freq="D")
        n_days = len(dates)

        day_offsets = np.arange(n_days)
        # Seasonal cycle: peaks around July, lows around January
        base_max = 75 + 30 * np.sin(2 * np.pi * day_offsets / 365 - np.pi / 2)
        max_temps = base_max + np.random.normal(0, 4, n_days)
        min_temps = max_temps - np.random.uniform(15, 30, n_days)

        return pd.DataFrame({
            "date": dates,
            "max_temp_f": np.round(max_temps, 1),
            "min_temp_f": np.round(min_temps, 1),
        })


async def main():
    """Test data fetching."""
    logging.basicConfig(level=logging.INFO)

    phoenix = PhoenixDataFetcher()
    data = await phoenix.fetch_all()

    print(f"\nFetched {len(data)} datasets")
    for name, df in data.items():
        print(f"  {name}: {len(df)} records")

    # Test ASU fetcher
    asu = ASUDataFetcher()
    hvi = await asu.fetch_heat_vulnerability()
    if hvi is not None:
        print(f"\nASU HVI: {len(hvi)} records")
    else:
        print("\nASU HVI: Fell back to synthetic (None returned)")

    # Test NOAA fetcher
    noaa = NOAAWeatherFetcher()
    forecast = await noaa.fetch_forecast()
    print(f"\nNOAA forecast: {'received' if forecast else 'failed'}")

    historical = await noaa.fetch_historical("2024-06-01", "2024-08-31")
    if historical is not None:
        print(f"NOAA historical: {len(historical)} days")


if __name__ == "__main__":
    asyncio.run(main())
