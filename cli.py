"""
Weather Activity Advisor - Interactive CLI
Quick command-line tool to query the expert system directly from the terminal.
"""

import sys
from inference_engine import WeatherInferenceEngine


def main():
    print("=" * 60)
    print("      ⛅ WEATHER ACTIVITY ADVISOR (CLI EXPERT SYSTEM)     ")
    print("=" * 60)
    print("Knowledge-Base Rule Engine: Temperature + Rain + Wind -> Activity\n")

    engine = WeatherInferenceEngine()

    try:
        temp_str = input("Enter Temperature in °C (e.g. 24.5) [Default: 22.0]: ").strip()
        temp = float(temp_str) if temp_str else 22.0

        print("\nPrecipitation Options:")
        print("  1. None")
        print("  2. Light Drizzle")
        print("  3. Moderate Rain")
        print("  4. Heavy Rain / Thunderstorm")
        rain_choice = input("Select Precipitation (1-4) [Default: 1]: ").strip()
        rain_map = {
            "1": "None",
            "2": "Light Drizzle",
            "3": "Moderate Rain",
            "4": "Heavy Rain / Thunderstorm"
        }
        rain = rain_map.get(rain_choice, "None")

        wind_str = input("\nEnter Wind Speed in km/h (e.g. 15.0) [Default: 12.0]: ").strip()
        wind = float(wind_str) if wind_str else 12.0

    except ValueError:
        print("Invalid input format. Using standard defaults.")
        temp, rain, wind = 22.0, "None", 12.0

    print("\nRunning Forward-Chaining Inference...\n" + "-" * 60)
    result = engine.run_inference(temperature=temp, rain=rain, wind_speed=wind)

    print(f"🎯 RECOMMENDED ACTIVITY: {result.primary_activity}")
    print(f"📌 CATEGORY:             {result.category}")
    print(f"📊 SUITABILITY INDEX:    {result.suitability_score}%")
    print(f"⚙️ FIRED RULE:           {result.fired_rule.name} ({result.fired_rule.rule_id})")
    print(f"\n💡 EXPERT JUSTIFICATION:\n  {result.fired_rule.explanation}")

    print("\n🎒 RECOMMENDED GEAR / ATTIRE:")
    for c in result.clothing_checklist:
        print(f"  ✔ {c}")

    if result.safety_advisories:
        print("\n⚠️ SAFETY ADVISORIES:")
        for s in result.safety_advisories:
            print(f"  ⚠ {s}")

    print("\n🔄 ALTERNATIVE SUGGESTIONS:")
    for i, a in enumerate(result.alternative_activities, 1):
        print(f"  {i}. {a}")

    print("-" * 60)
    print("Forward-Chaining completed successfully.")


if __name__ == "__main__":
    main()
