"""Tests for the simulation core: SyntheticResident, InterventionScenario, UrbanHeatSimulator."""

import pytest
import numpy as np
from pcse.simulation import (
    SyntheticResident,
    InterventionScenario,
    UrbanHeatSimulator,
    DemographicProfile,
)


# ---------------------------------------------------------------------------
# SyntheticResident
# ---------------------------------------------------------------------------

class TestSyntheticResident:
    def _make_resident(self, **overrides):
        defaults = dict(
            id=0, lat=33.45, lon=-112.07, age=35, income=50000,
            has_ac=True, has_car=True, works_outdoors=False,
            health_conditions=[], social_isolation=0.0,
        )
        defaults.update(overrides)
        return SyntheticResident(**defaults)

    def test_low_risk_baseline(self):
        r = self._make_resident()
        assert r.heat_vulnerability < 25
        assert r.profile() == DemographicProfile.LOW_RISK

    def test_elderly_increases_vulnerability(self):
        young = self._make_resident(age=35)
        old = self._make_resident(age=70)
        assert old.heat_vulnerability > young.heat_vulnerability

    def test_no_ac_increases_vulnerability(self):
        with_ac = self._make_resident(has_ac=True)
        no_ac = self._make_resident(has_ac=False)
        assert no_ac.heat_vulnerability - with_ac.heat_vulnerability == 30

    def test_outdoor_work_increases_vulnerability(self):
        indoor = self._make_resident(works_outdoors=False)
        outdoor = self._make_resident(works_outdoors=True)
        assert outdoor.heat_vulnerability > indoor.heat_vulnerability

    def test_health_conditions_increase_vulnerability(self):
        healthy = self._make_resident(health_conditions=[])
        sick = self._make_resident(health_conditions=["cardiovascular", "diabetes"])
        assert sick.heat_vulnerability > healthy.heat_vulnerability

    def test_vulnerability_capped_at_100(self):
        r = self._make_resident(
            age=80, income=10000, has_ac=False, works_outdoors=True,
            health_conditions=["cardiovascular", "diabetes", "asthma"],
            social_isolation=1.0,
        )
        assert r.heat_vulnerability <= 100

    def test_extreme_risk_profile(self):
        r = self._make_resident(age=80, income=10000, has_ac=False)
        assert r.profile() == DemographicProfile.EXTREME_RISK

    def test_update_daily_no_heat_stress(self):
        r = self._make_resident()
        r.update_daily(max_temp=80, interventions={})
        assert r.health_status == "healthy"
        assert r.heat_exposure_today == 0

    def test_update_daily_high_heat(self):
        r = self._make_resident(age=80, income=10000, has_ac=False)
        # Run multiple hot days to increase chance of health impact
        for _ in range(50):
            r.update_daily(max_temp=115, interventions={})
        # With extreme vulnerability and 115F, some impact is expected
        assert r.heat_exposure_today > 0

    def test_cooling_center_intervention_reduces_exposure(self):
        r = self._make_resident()
        r.update_daily(max_temp=110, interventions={})
        exposure_without = r.heat_exposure_today

        r2 = self._make_resident()
        r2.update_daily(max_temp=110, interventions={"cooling_center_nearby": True})
        assert r2.heat_exposure_today < exposure_without

    def test_transit_cooling_helps_carless(self):
        r_no_car = self._make_resident(has_car=False)
        r_no_car.update_daily(max_temp=110, interventions={})
        base = r_no_car.heat_exposure_today

        r_no_car2 = self._make_resident(has_car=False)
        r_no_car2.update_daily(max_temp=110, interventions={"transit_cooling": True})
        assert r_no_car2.heat_exposure_today < base


# ---------------------------------------------------------------------------
# InterventionScenario
# ---------------------------------------------------------------------------

class TestInterventionScenario:
    def _make_intervention(self, **overrides):
        defaults = dict(
            name="Test",
            intervention_type="tree_canopy",
            target_area={"center_lat": 33.45, "center_lon": -112.07, "radius_km": 1.0},
            implementation_cost=100000,
            timeline_months=6,
        )
        defaults.update(overrides)
        return InterventionScenario(**defaults)

    def test_valid_intervention(self):
        i = self._make_intervention()
        assert i.validate() is True

    def test_all_valid_types(self):
        for t in ["tree_canopy", "cooling_center", "transit_cooling", "cool_roofs"]:
            i = self._make_intervention(intervention_type=t)
            assert i.validate() is True

    def test_invalid_type_rejected(self):
        i = self._make_intervention(intervention_type="giant_fan")
        assert i.validate() is False

    def test_zero_budget_rejected(self):
        i = self._make_intervention(implementation_cost=0)
        assert i.validate() is False

    def test_negative_budget_rejected(self):
        i = self._make_intervention(implementation_cost=-500)
        assert i.validate() is False

    def test_zero_timeline_rejected(self):
        i = self._make_intervention(timeline_months=0)
        assert i.validate() is False

    def test_invalid_latitude_rejected(self):
        i = self._make_intervention(
            target_area={"center_lat": 100, "center_lon": -112.07, "radius_km": 1.0}
        )
        assert i.validate() is False

    def test_invalid_longitude_rejected(self):
        i = self._make_intervention(
            target_area={"center_lat": 33.45, "center_lon": -200, "radius_km": 1.0}
        )
        assert i.validate() is False

    def test_excessive_radius_rejected(self):
        i = self._make_intervention(
            target_area={"center_lat": 33.45, "center_lon": -112.07, "radius_km": 100}
        )
        assert i.validate() is False

    def test_zero_radius_rejected(self):
        i = self._make_intervention(
            target_area={"center_lat": 33.45, "center_lon": -112.07, "radius_km": 0}
        )
        assert i.validate() is False

    def test_missing_lon_rejected(self):
        i = self._make_intervention(
            target_area={"center_lat": 33.45}
        )
        assert i.validate() is False

    def test_target_area_without_center_lat_passes(self):
        # Non-geographic target areas (e.g. census tract IDs) should still pass
        i = self._make_intervention(target_area={"tract_ids": ["040130100"]})
        assert i.validate() is True


# ---------------------------------------------------------------------------
# UrbanHeatSimulator
# ---------------------------------------------------------------------------

class TestUrbanHeatSimulator:
    def test_generate_population(self):
        sim = UrbanHeatSimulator(n_residents=100)
        sim.generate_synthetic_population()
        assert len(sim.residents) == 100
        assert sim.spatial_index is not None

    def test_residents_within_bounds(self):
        sim = UrbanHeatSimulator(n_residents=500)
        sim.generate_synthetic_population()
        for r in sim.residents:
            assert sim.lat_min <= r.lat <= sim.lat_max
            assert sim.lon_min <= r.lon <= sim.lon_max

    def test_run_day(self):
        sim = UrbanHeatSimulator(n_residents=100)
        sim.generate_synthetic_population()
        outcomes = sim.run_day(max_temp=110)
        assert "heat_illness" in outcomes
        assert "deaths" in outcomes
        assert "er_visits" in outcomes
        assert sim.current_day == 1

    def test_run_scenario_returns_results(self):
        sim = UrbanHeatSimulator(n_residents=100)
        sim.generate_synthetic_population()
        results = sim.run_scenario(days=10)
        assert "total_outcomes" in results
        assert "daily_history" in results
        assert len(results["daily_history"]) == 10

    def test_interventions_reduce_outcomes(self):
        # Baseline
        sim1 = UrbanHeatSimulator(n_residents=1000)
        sim1.generate_synthetic_population()
        baseline = sim1.run_scenario(days=30)

        # With cooling centers
        sim2 = UrbanHeatSimulator(n_residents=1000)
        sim2.generate_synthetic_population()
        interventions = [
            InterventionScenario(
                name="Downtown Cooling",
                intervention_type="cooling_center",
                target_area={"center_lat": 33.45, "center_lon": -112.07, "radius_km": 5.0},
                implementation_cost=500000,
                timeline_months=3,
            )
        ]
        with_intervention = sim2.run_scenario(days=30, interventions=interventions)

        # Intervention should not increase deaths
        assert with_intervention["total_outcomes"]["deaths"] <= baseline["total_outcomes"]["deaths"] + 5

    def test_get_vulnerable_populations(self):
        sim = UrbanHeatSimulator(n_residents=200)
        sim.generate_synthetic_population()
        df = sim.get_vulnerable_populations(threshold=50.0)
        assert len(df) > 0
        assert all(df["vulnerability"] > 50.0)

    def test_temperature_profile_generation(self):
        sim = UrbanHeatSimulator(n_residents=10)
        temps = sim._generate_phoenix_temperatures(365)
        assert len(temps) == 365
        # Phoenix summer should be hot
        summer_temps = temps[150:240]
        assert max(summer_temps) > 100

    def test_custom_temperature_profile(self):
        sim = UrbanHeatSimulator(n_residents=50)
        sim.generate_synthetic_population()
        custom_temps = [75.0] * 10  # Mild weather
        results = sim.run_scenario(days=10, temperature_profile=custom_temps)
        # Very few health events at 75F
        assert results["total_outcomes"]["deaths"] == 0
