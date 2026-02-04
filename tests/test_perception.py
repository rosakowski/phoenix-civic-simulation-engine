"""Tests for the perception layer: data fetchers and ingestion pipeline."""

import pytest
import pandas as pd
from pcse.perception import PhoenixDataPortal, DataIngestionPipeline, DataSource
from pcse.perception.data_fetcher import (
    ASUDataFetcher,
    NOAAWeatherFetcher,
    PhoenixDataFetcher,
)


# ---------------------------------------------------------------------------
# PhoenixDataPortal synthetic data
# ---------------------------------------------------------------------------

class TestPhoenixDataPortal:
    @pytest.fixture
    def portal(self):
        return PhoenixDataPortal()

    @pytest.mark.asyncio
    async def test_synthetic_hvi(self, portal):
        df = portal._generate_synthetic_hvi()
        assert isinstance(df, pd.DataFrame)
        assert len(df) == 358  # Phoenix census tracts
        assert "census_tract_id" in df.columns
        assert "heat_vulnerability_score" in df.columns
        assert "lat" in df.columns
        assert "lon" in df.columns
        assert df["heat_vulnerability_score"].min() >= 0
        assert df["heat_vulnerability_score"].max() <= 100

    @pytest.mark.asyncio
    async def test_synthetic_transit_data(self, portal):
        df = portal._generate_synthetic_transit_data()
        assert isinstance(df, pd.DataFrame)
        assert len(df) == 150
        assert "has_cooling_bus" in df.columns

    @pytest.mark.asyncio
    async def test_synthetic_canopy_data(self, portal):
        df = portal._generate_synthetic_canopy_data()
        assert isinstance(df, pd.DataFrame)
        assert len(df) == 200
        assert "canopy_coverage_percent" in df.columns
        assert df["canopy_coverage_percent"].max() <= 100

    @pytest.mark.asyncio
    async def test_synthetic_er_data(self, portal):
        df = portal._generate_synthetic_er_data()
        assert isinstance(df, pd.DataFrame)
        assert len(df) == 366  # 2024 is a leap year
        assert "heat_er_visits" in df.columns
        assert "heat_deaths" in df.columns

    @pytest.mark.asyncio
    async def test_ingest_all(self, portal):
        data = await portal.ingest_all()
        assert len(data) == 4
        assert "heat_vulnerability" in data
        assert "transit_heat_relief" in data
        assert "tree_canopy" in data
        assert "er_heat_visits" in data


# ---------------------------------------------------------------------------
# NOAAWeatherFetcher synthetic fallback
# ---------------------------------------------------------------------------

class TestNOAAWeatherFetcher:
    def test_synthetic_historical(self):
        noaa = NOAAWeatherFetcher()
        df = noaa._generate_synthetic_historical("2024-06-01", "2024-08-31")
        assert isinstance(df, pd.DataFrame)
        assert "date" in df.columns
        assert "max_temp_f" in df.columns
        assert "min_temp_f" in df.columns
        assert len(df) == 92  # June 1 to Aug 31

    @pytest.mark.asyncio
    async def test_historical_without_token_returns_synthetic(self):
        noaa = NOAAWeatherFetcher(cdo_token=None)
        df = await noaa.fetch_historical("2024-06-01", "2024-08-31")
        assert df is not None
        assert len(df) > 0

    def test_synthetic_temps_are_realistic(self):
        noaa = NOAAWeatherFetcher()
        df = noaa._generate_synthetic_historical("2024-01-01", "2024-12-31")
        # Summer temps should be higher than winter
        summer = df[(df["date"].dt.month >= 6) & (df["date"].dt.month <= 8)]
        winter = df[(df["date"].dt.month == 12) | (df["date"].dt.month <= 2)]
        assert summer["max_temp_f"].mean() > winter["max_temp_f"].mean()


# ---------------------------------------------------------------------------
# DataSource and DataIngestionPipeline
# ---------------------------------------------------------------------------

class TestDataSource:
    def test_data_source_creation(self):
        ds = DataSource(
            name="test", url="https://example.com", format="json",
            update_frequency="daily"
        )
        assert ds.name == "test"
        assert ds.last_ingested is None


class TestDataIngestionPipeline:
    def test_pipeline_setup(self):
        pipeline = DataIngestionPipeline()
        assert len(pipeline.sources) >= 2
        assert pipeline.phoenix is not None
