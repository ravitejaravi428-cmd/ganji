"""
Weather Activity Advisor - Knowledge Base (KB)
Defines the facts, data models, rules, and semantic categorization
for the Expert System.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional


@dataclass
class Rule:
    """Represents a single IF-THEN rule in the expert system knowledge base."""
    rule_id: str
    name: str
    priority: int  # Higher priority rules take precedence (e.g. safety rules = 90-100)
    
    # IF Conditions (evaluated against extracted Working Memory facts)
    # None indicates 'Any' (wildcard)
    temp_categories: Optional[List[str]] = None
    rain_conditions: Optional[List[str]] = None
    wind_categories: Optional[List[str]] = None
    
    # Optional continuous constraint bounds
    min_temp: Optional[float] = None
    max_temp: Optional[float] = None
    max_wind: Optional[float] = None
    min_wind: Optional[float] = None
    
    # THEN Actions / Conclusions
    recommendation: str = ""
    category: str = "Outdoor"  # 'Outdoor', 'Indoor', 'Water Sports', 'Safety Alert'
    suitability_score: int = 80  # 0 to 100%
    clothing: List[str] = field(default_factory=list)
    safety_warnings: List[str] = field(default_factory=list)
    alternative_activities: List[str] = field(default_factory=list)
    explanation: str = ""

    def matches(self, facts: Dict[str, Any]) -> tuple[bool, List[str]]:
        """
        Evaluates rule conditions against working memory facts.
        Returns (matches: bool, matched_reasons: List[str]).
        """
        reasons = []
        
        # 1. Temperature Category Match
        if self.temp_categories is not None:
            if facts.get("temp_category") in self.temp_categories:
                reasons.append(f"Temperature '{facts.get('temp_category')}' matches rule criteria ({', '.join(self.temp_categories)})")
            else:
                return False, []
                
        # 2. Rain Condition Match
        if self.rain_conditions is not None:
            if facts.get("rain") in self.rain_conditions:
                reasons.append(f"Precipitation '{facts.get('rain')}' matches rule criteria ({', '.join(self.rain_conditions)})")
            else:
                return False, []
                
        # 3. Wind Category Match
        if self.wind_categories is not None:
            if facts.get("wind_category") in self.wind_categories:
                reasons.append(f"Wind speed '{facts.get('wind_category')}' matches rule criteria ({', '.join(self.wind_categories)})")
            else:
                return False, []
                
        # 4. Numerical Temperature Bounds
        temp = facts.get("temperature", 20.0)
        if self.min_temp is not None and temp < self.min_temp:
            return False, []
        if self.max_temp is not None and temp > self.max_temp:
            return False, []
            
        # 5. Numerical Wind Bounds
        wind = facts.get("wind_speed", 10.0)
        if self.min_wind is not None and wind < self.min_wind:
            return False, []
        if self.max_wind is not None and wind > self.max_wind:
            return False, []

        return True, reasons


# =====================================================================
# Semantic Categorization (Fuzzy / Discretization functions)
# =====================================================================

def categorize_temperature(temp_c: float) -> str:
    """Classifies numerical Celsius temperature into semantic qualitative bands."""
    if temp_c < 5.0:
        return "Freezing / Very Cold"
    elif 5.0 <= temp_c < 16.0:
        return "Cold / Chilly"
    elif 16.0 <= temp_c < 26.0:
        return "Mild / Pleasant"
    elif 26.0 <= temp_c < 35.0:
        return "Warm / Hot"
    else:
        return "Extreme Heat"


def categorize_wind(wind_kmh: float) -> str:
    """Classifies numerical wind speed (km/h) into Beaufort-inspired categories."""
    if wind_kmh < 15.0:
        return "Calm / Gentle Breeze"
    elif 15.0 <= wind_kmh < 30.0:
        return "Moderate Breeze"
    elif 30.0 <= wind_kmh < 50.0:
        return "Strong Wind"
    else:
        return "Gale / Storm Wind"


# =====================================================================
# Built-In Knowledge Base Rules
# =====================================================================

RULES_DATABASE: List[Rule] = [
    # --- CRITICAL SAFETY & EXTREME WEATHER RULES (Priority 90-100) ---
    Rule(
        rule_id="R01_STORM_HAZARD",
        name="Severe Storm & Gale Danger Alert",
        priority=100,
        rain_conditions=["Heavy Rain / Thunderstorm"],
        wind_categories=["Strong Wind", "Gale / Storm Wind"],
        recommendation="Stay Safely Indoors & Avoid Travel (Storm Warning)",
        category="Safety Alert",
        suitability_score=15,
        clothing=["Cozy indoor loungewear", "Keep flashlights & emergency kit ready"],
        safety_warnings=[
            "Severe gale warning: Flying debris and fallen tree branches hazard.",
            "Lightning hazard: Disconnect sensitive electronics and stay away from open windows.",
            "Flash flood risk on roads: Do NOT attempt to drive through waterlogged paths."
        ],
        alternative_activities=[
            "Home movie marathon",
            "Board games with family",
            "Podcast listening or reading books",
            "Cooking a warm soup/stew"
        ],
        explanation="Severe combination of torrential rain and gale-force winds poses significant hazards outdoors."
    ),

    Rule(
        rule_id="R02_EXTREME_HEAT",
        name="Heatwave & Heat Exhaustion Advisory",
        priority=95,
        temp_categories=["Extreme Heat"],
        recommendation="Air-Conditioned Indoor Activities (Cinema, Mall, or Museum)",
        category="Indoor",
        suitability_score=35,
        clothing=["Ultra-light breathable linen/cotton", "UV400 sunglasses", "Wide-brim hat if stepping out"],
        safety_warnings=[
            "Heat stroke & dehydration risk: Drink at least 3-4 liters of water.",
            "Avoid strenuous outdoor workouts between 11:00 AM and 4:30 PM.",
            "Apply SPF 50+ sunscreen if brief outdoor exposure is unavoidable."
        ],
        alternative_activities=[
            "Indoor shopping mall walk",
            "IMAX Cinema screening",
            "Contemporary art gallery or aquarium visit",
            "Air-conditioned indoor ice rink"
        ],
        explanation="Temperatures exceeding 35°C trigger the heat mitigation protocol to prevent heat exhaustion."
    ),

    Rule(
        rule_id="R03_FREEZING_STORM",
        name="Freezing Temperatures & Rain Sleet Alert",
        priority=90,
        temp_categories=["Freezing / Very Cold"],
        rain_conditions=["Moderate Rain", "Heavy Rain / Thunderstorm"],
        recommendation="Cozy Fireplace Relaxation or Indoor Heated Wellness Spa",
        category="Indoor",
        suitability_score=25,
        clothing=["Thermal base layers", "Fleece pullover", "Wool socks", "Insulated slippers"],
        safety_warnings=[
            "High hypothermia risk if clothes get wet in freezing temperatures.",
            "Black ice hazard on roads and pedestrian walkways."
        ],
        alternative_activities=[
            "Heated spa or sauna retreat",
            "Hot cocoa and mystery novel reading",
            "Baking homemade bread or cookies",
            "Indoor puzzle solving or video gaming"
        ],
        explanation="Near-freezing temperatures coupled with rainfall create severe wet-chill and black ice hazards."
    ),

    # --- RAINY WEATHER PROTOCOLS (Priority 65-80) ---
    Rule(
        rule_id="R04_HEAVY_RAIN_INDOOR",
        name="Heavy Downpour Indoor Recreation",
        priority=80,
        rain_conditions=["Heavy Rain / Thunderstorm"],
        recommendation="Indoor Sports Arena (Bowling, Trampoline Park, or Rock Climbing)",
        category="Indoor",
        suitability_score=50,
        clothing=["Waterproof trench coat / Gore-Tex rain jacket", "Water-resistant sneakers or boots", "Sturdy windproof umbrella"],
        safety_warnings=[
            "Waterlogged roads and reduced driving visibility.",
            "Slippery tile steps and pavement."
        ],
        alternative_activities=[
            "Ten-pin bowling with friends",
            "Indoor bouldering / rock climbing gym",
            "Escape room challenge",
            "Visiting an indoor science discovery center"
        ],
        explanation="Heavy downpour suppresses all outdoor activities; redirecting to active indoor sports facilities."
    ),

    Rule(
        rule_id="R05_MODERATE_RAIN_CULTURE",
        name="Moderate Rain Cultural & Leisure Exploration",
        priority=70,
        rain_conditions=["Moderate Rain"],
        wind_categories=["Calm / Gentle Breeze", "Moderate Breeze"],
        recommendation="Museum, Public Library, or Art Exhibition Tour",
        category="Indoor",
        suitability_score=75,
        clothing=["Water-repellent jacket", "Foldable umbrella", "Comfortable walking shoes"],
        safety_warnings=["Puddles on sidewalks; carry a waterproof bag sleeve for tech gadgets."],
        alternative_activities=[
            "Exploring a city museum",
            "Art gallery stroll & guided tour",
            "Browsing a multi-story bookstore or library",
            "Specialty coffee cupping workshop"
        ],
        explanation="Consistent moderate rain is ideal for cultural, educational, and relaxed indoor venues."
    ),

    Rule(
        rule_id="R06_LIGHT_DRIZZLE_ROMANTIC",
        name="Light Drizzle Botanic Greenhouse or Covered Bazaar",
        priority=65,
        rain_conditions=["Light Drizzle"],
        temp_categories=["Mild / Pleasant", "Warm / Hot"],
        recommendation="Botanical Conservatory / Covered Food Market Walk",
        category="Hybrid",
        suitability_score=80,
        clothing=["Light waterproof windbreaker", "Water-resistant sneakers", "Compact umbrella"],
        safety_warnings=["Slightly slippery cobblestones or wood bridges."],
        alternative_activities=[
            "Walk through covered botanic greenhouse",
            "Artisan covered farmer's market",
            "Cozy veranda café with garden views",
            "Scenic light-drizzle photography"
        ],
        explanation="Gentle drizzle with mild temperature creates a refreshing aesthetic for covered gardens and markets."
    ),

    Rule(
        rule_id="R07_COLD_DRIZZLE_COFFEE",
        name="Chilly Drizzle Café & Comfort Day",
        priority=68,
        rain_conditions=["Light Drizzle", "Moderate Rain"],
        temp_categories=["Cold / Chilly"],
        recommendation="Artisan Coffee Roastery & Cozy Reading Lounge",
        category="Indoor",
        suitability_score=85,
        clothing=["Wool overcoat or down jacket", "Warm scarf", "Waterproof boots"],
        safety_warnings=["Damp chill can induce colds; keep core warm."],
        alternative_activities=[
            "Independent bookstore browsing",
            "Pottery painting or ceramic workshop",
            "Acoustic café music listening",
            "Cooking comforting hot pot at home"
        ],
        explanation="Cold, wet air calls for warm beverages, sensory comfort, and indoor communal warmth."
    ),

    # --- WIND-SPECIFIC RULES (Priority 60-75) ---
    Rule(
        rule_id="R08_STRONG_WIND_ADVENTURE",
        name="Strong Wind Action Sports (Kite / Windsurfing)",
        priority=72,
        rain_conditions=["None"],
        temp_categories=["Mild / Pleasant", "Warm / Hot"],
        wind_categories=["Strong Wind"],
        recommendation="Kite Buggying, Windsurfing, or Power Kite Flying",
        category="Outdoor",
        suitability_score=90,
        clothing=["Windproof shell jacket", "Wrap-around sports sunglasses", "Sturdy grip sneakers"],
        safety_warnings=[
            "High gusts: Anchor ground equipment firmly.",
            "Wear helmet and safety gear for action sports."
        ],
        alternative_activities=[
            "Coastal bluff photography",
            "Power kiting at an open airfield or park",
            "Windsurfing at designated bay waters",
            "Visiting an observation tower or scenic bluff"
        ],
        explanation="High steady winds with zero rain offer peak aerodynamic conditions for wind-powered sports."
    ),

    Rule(
        rule_id="R09_GALE_DRY_CAUTION",
        name="High Dry Wind Warning - Avoid Forest Trails",
        priority=78,
        rain_conditions=["None"],
        wind_categories=["Gale / Storm Wind"],
        recommendation="Indoor Fitness Gym & Table Tennis / Squash",
        category="Indoor",
        suitability_score=40,
        clothing=["Casual sportswear", "Eye protection against airborne dust/sand"],
        safety_warnings=[
            "Risk of falling tree branches and roof tiles in wooded or urban areas.",
            "High crosswinds make highway cycling and lightweight vehicles unstable."
        ],
        alternative_activities=[
            "Indoor squash or badminton court",
            "Weight training at gym",
            "Indoor laser tag",
            "Home organization project"
        ],
        explanation="Gale-force winds even without rain create serious airborne hazards, prohibiting outdoor trails."
    ),

    # --- IDEAL OUTDOOR & SUNNY RULES (Priority 50-65) ---
    Rule(
        rule_id="R10_PERFECT_HIKING",
        name="Optimal Scenic Hiking & Trail Trekking",
        priority=60,
        rain_conditions=["None"],
        temp_categories=["Mild / Pleasant"],
        wind_categories=["Calm / Gentle Breeze"],
        recommendation="Scenic Mountain Hiking, Forest Trail Walk, or Nature Trek",
        category="Outdoor",
        suitability_score=98,
        clothing=["Breathable moisture-wicking t-shirt", "Hiking shorts or cargo pants", "Trail running shoes / hiking boots", "Sun visor / cap"],
        safety_warnings=["Carry a 1-liter water flask and light trail snacks."],
        alternative_activities=[
            "Cross-country cycling / gravel biking",
            "Landscape photography session",
            "Botanical garden exploration",
            "Outdoor yoga or tai chi session"
        ],
        explanation="Mild temperature (16-25°C), zero rain, and gentle breeze represent the gold standard for hiking."
    ),

    Rule(
        rule_id="R11_PICNIC_KITE",
        name="Park Picnic & Recreational Kite Flying",
        priority=58,
        rain_conditions=["None"],
        temp_categories=["Mild / Pleasant"],
        wind_categories=["Moderate Breeze"],
        recommendation="Public Park Picnic, Frisbee, & Dual-Line Kite Flying",
        category="Outdoor",
        suitability_score=95,
        clothing=["Comfortable cotton shirt", "Light denim or chinos", "Sunglasses", "Picnic mat"],
        safety_warnings=["Apply light sunscreen for extended open-field exposure."],
        alternative_activities=[
            "Open-air farmers market shopping",
            "Casual lake kayaking",
            "Dog park play and agility training",
            "Outdoor sketching or painting"
        ],
        explanation="A steady moderate breeze combined with pleasant mild temps provides lift for kites and keeps picnics cool."
    ),

    Rule(
        rule_id="R12_SUMMER_BEACH_SWIM",
        name="Beach Day, Ocean Swim & Paddleboarding",
        priority=62,
        rain_conditions=["None"],
        temp_categories=["Warm / Hot"],
        wind_categories=["Calm / Gentle Breeze", "Moderate Breeze"],
        recommendation="Beach Day, Swimming, Snorkeling, or Stand-Up Paddleboarding (SUP)",
        category="Water Sports",
        suitability_score=96,
        clothing=["UV-protective swimwear / rash guard", "Flip flops or water shoes", "Polarized sunglasses", "Sunscreen SPF 50+"],
        safety_warnings=[
            "High solar UV radiation: Reapply water-resistant sunscreen every 90 minutes.",
            "Stay within lifeguard-monitored swimming zones."
        ],
        alternative_activities=[
            "Lakeside swimming or sunbathing",
            "Open-air water park slides",
            "Beach volleyball tournament",
            "Sunset boat cruise or kayak rental"
        ],
        explanation="Warm temperatures (26-34°C) with dry sunny skies and mild water currents are prime for water activities."
    ),

    Rule(
        rule_id="R13_WARM_CYCLING",
        name="Early Morning Road Cycling & Distance Running",
        priority=56,
        rain_conditions=["None"],
        temp_categories=["Warm / Hot"],
        wind_categories=["Calm / Gentle Breeze"],
        recommendation="Road Cycling, Long-Distance Running, or Tennis",
        category="Outdoor",
        suitability_score=88,
        clothing=["Performance quick-dry jersey", "Padded cycling shorts", "Ventilated sports cap", "Sunglasses"],
        safety_warnings=[
            "Hydrate frequently with electrolyte beverages to offset sweat loss.",
            "Opt for early morning or late afternoon to avoid midday heat peak."
        ],
        alternative_activities=[
            "Outdoor tennis / pickleball match",
            "Open-air skatepark session",
            "Outdoor basketball pickup game",
            "Kayaking on calm river waters"
        ],
        explanation="Dry warm weather with low wind enables excellent tire grip and optimal aerobic pacing."
    ),

    Rule(
        rule_id="R14_CRISP_AUTUMN_WALK",
        name="Crisp Cool Day Brisk Walking & Urban Exploration",
        priority=52,
        rain_conditions=["None"],
        temp_categories=["Cold / Chilly"],
        wind_categories=["Calm / Gentle Breeze", "Moderate Breeze"],
        recommendation="Brisk Historical City Walk, Architecture Tour, or Forest Trail",
        category="Outdoor",
        suitability_score=90,
        clothing=["Mid-weight fleece or denim jacket", "Thermal undershirt", "Comfortable walking shoes", "Beanie or knit cap"],
        safety_warnings=["Low temperatures can tighten muscles; perform light warm-up stretches first."],
        alternative_activities=[
            "Visiting an open-air historical village",
            "City architecture photography walk",
            "Mountain biking on dry packed trails",
            "Outdoor flea market hunting"
        ],
        explanation="Dry cool air between 5-15°C prevents sweating during vigorous walking and keeps energy high."
    ),

    Rule(
        rule_id="R15_WINTER_ICE_SKATE",
        name="Crisp Winter Outdoor Ice Skating & Snowshoeing",
        priority=55,
        rain_conditions=["None"],
        temp_categories=["Freezing / Very Cold"],
        wind_categories=["Calm / Gentle Breeze"],
        recommendation="Outdoor Ice Skating Rink, Snowshoeing, or Winter Photography",
        category="Outdoor",
        suitability_score=85,
        clothing=["Insulated down parka", "Thermal leggings", "Touchscreen winter gloves", "Knit beanie & neck gaiter"],
        safety_warnings=[
            "Dress in wind-resistant layers to prevent wind-chill and frostbite.",
            "Wear helmet when ice skating on natural frozen lakes."
        ],
        alternative_activities=[
            "Visiting a winter wonderland light festival",
            "Scenic winter photography walk",
            "Snowman building and sledding",
            "Cozy thermal sauna after outdoor activity"
        ],
        explanation="Sub-zero or near-freezing temperatures under calm dry conditions offer crisp, magical winter sports."
    ),

    # --- FALLBACK GENERAL RULES (Priority 10-20) ---
    Rule(
        rule_id="R16_DEFAULT_INDOOR",
        name="General Indoor Activity (Rain / Unfavorable Conditions)",
        priority=20,
        rain_conditions=["Moderate Rain", "Heavy Rain / Thunderstorm"],
        recommendation="Indoor Recreation: Bowling, Cinema, or Gym Workout",
        category="Indoor",
        suitability_score=70,
        clothing=["Casual layers", "Umbrella", "Waterproof footwear"],
        safety_warnings=["Watch out for wet pedestrian floors."],
        alternative_activities=[
            "Fitness gym workout",
            "Movie theater",
            "Cooking or baking at home",
            "Board games with friends"
        ],
        explanation="Unfavorable outdoor precipitation calls for enjoyable indoor pastimes."
    ),

    Rule(
        rule_id="R17_DEFAULT_OUTDOOR",
        name="General Pleasant Outdoor Leisure",
        priority=15,
        rain_conditions=["None", "Light Drizzle"],
        recommendation="Neighborhood Walk, Local Park Visit, or Outdoor Café",
        category="Outdoor",
        suitability_score=75,
        clothing=["Casual weather-appropriate clothing", "Comfortable walking shoes"],
        safety_warnings=["Check local weather forecast before heading out on long trips."],
        alternative_activities=[
            "Casual stroll in the local neighborhood",
            "Outdoor dining on a covered terrace",
            "Visiting a local garden nursery",
            "Photography"
        ],
        explanation="Mild environmental factors support general outdoor leisure."
    )
]


def get_all_rules() -> List[Rule]:
    """Returns the full knowledge base ruleset."""
    return RULES_DATABASE
