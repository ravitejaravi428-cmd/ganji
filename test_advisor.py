"""
Automated Unit Tests for Weather Activity Advisor
Tests Knowledge Base, linguistic discretization, forward chaining,
and conflict resolution under diverse weather edge cases.
"""

import unittest
from knowledge_base import categorize_temperature, categorize_wind, get_all_rules
from inference_engine import WeatherInferenceEngine


class TestWeatherExpertSystem(unittest.TestCase):

    def setUp(self):
        self.engine = WeatherInferenceEngine()

    def test_temperature_categorization(self):
        self.assertEqual(categorize_temperature(-5), "Freezing / Very Cold")
        self.assertEqual(categorize_temperature(2), "Freezing / Very Cold")
        self.assertEqual(categorize_temperature(10), "Cold / Chilly")
        self.assertEqual(categorize_temperature(21), "Mild / Pleasant")
        self.assertEqual(categorize_temperature(30), "Warm / Hot")
        self.assertEqual(categorize_temperature(40), "Extreme Heat")

    def test_wind_categorization(self):
        self.assertEqual(categorize_wind(8), "Calm / Gentle Breeze")
        self.assertEqual(categorize_wind(22), "Moderate Breeze")
        self.assertEqual(categorize_wind(40), "Strong Wind")
        self.assertEqual(categorize_wind(65), "Gale / Storm Wind")

    def test_storm_safety_priority_rule(self):
        # Severe combination: Heavy rain + Gale wind must trigger storm hazard
        result = self.engine.run_inference(temperature=18.0, rain="Heavy Rain / Thunderstorm", wind_speed=60.0)
        self.assertEqual(result.fired_rule.rule_id, "R01_STORM_HAZARD")
        self.assertEqual(result.category, "Safety Alert")
        self.assertTrue(len(result.safety_advisories) > 0)

    def test_extreme_heat_rule(self):
        result = self.engine.run_inference(temperature=41.0, rain="None", wind_speed=10.0)
        self.assertEqual(result.fired_rule.rule_id, "R02_EXTREME_HEAT")
        self.assertEqual(result.category, "Indoor")

    def test_perfect_hiking_rule(self):
        # Mild 22C, No rain, Calm wind -> Hiking
        result = self.engine.run_inference(temperature=22.0, rain="None", wind_speed=10.0)
        self.assertEqual(result.fired_rule.rule_id, "R10_PERFECT_HIKING")
        self.assertEqual(result.category, "Outdoor")
        self.assertGreaterEqual(result.suitability_score, 90)

    def test_summer_beach_rule(self):
        # Warm 30C, No rain, Gentle breeze -> Beach/Swim
        result = self.engine.run_inference(temperature=30.0, rain="None", wind_speed=12.0)
        self.assertEqual(result.fired_rule.rule_id, "R12_SUMMER_BEACH_SWIM")
        self.assertEqual(result.category, "Water Sports")

    def test_conflict_resolution_and_trace(self):
        result = self.engine.run_inference(temperature=14.0, rain="Moderate Rain", wind_speed=15.0)
        self.assertIsNotNone(result.fired_rule)
        self.assertTrue(len(result.candidate_rules) >= 1)
        self.assertTrue(len(result.evaluation_traces) == len(get_all_rules()))

    def test_clothing_and_alternatives_populated(self):
        result = self.engine.run_inference(temperature=22.0, rain="None", wind_speed=10.0)
        self.assertTrue(len(result.clothing_checklist) > 0)
        self.assertTrue(len(result.alternative_activities) > 0)


if __name__ == "__main__":
    unittest.main()
