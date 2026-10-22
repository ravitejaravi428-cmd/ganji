"""
Weather Activity Advisor - Streamlit Web Application
A modern AI Expert System dashboard featuring:
- Interactive weather parameter controls & preset scenarios
- Forward-chaining inference engine execution
- Explainable AI (XAI) audit trace and rule conflict resolution
- Clothing checklist, safety alerts, and alternative activity suggestions
- Knowledge Base rule inspector and downloadable advisory report
"""

import streamlit as st
import json
from datetime import datetime
from knowledge_base import get_all_rules, categorize_temperature, categorize_wind
from inference_engine import WeatherInferenceEngine

# Page configuration
st.set_page_config(
    page_title="Weather Activity Advisor | AI Expert System",
    page_icon="⛅",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Styling (Vanilla CSS for visual appeal)
st.markdown("""
<style>
    /* Main container and font */
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', sans-serif;
    }
    
    /* Header hero styling */
    .hero-container {
        background: linear-gradient(135deg, #1e3a8a 0%, #3b82f6 50%, #06b6d4 100%);
        padding: 2.2rem 2.4rem;
        border-radius: 18px;
        color: white;
        margin-bottom: 2rem;
        box-shadow: 0 10px 25px -5px rgba(59, 130, 246, 0.3);
    }
    .hero-title {
        font-size: 2.3rem;
        font-weight: 800;
        margin: 0;
        letter-spacing: -0.02em;
    }
    .hero-subtitle {
        font-size: 1.05rem;
        opacity: 0.92;
        margin-top: 0.4rem;
        font-weight: 400;
    }
    
    /* Recommendation Card */
    .rec-card {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 16px;
        padding: 1.8rem;
        box-shadow: 0 4px 20px -2px rgba(0, 0, 0, 0.05);
        margin-bottom: 1.5rem;
        border-left: 6px solid #2563eb;
    }
    
    .badge-chip {
        display: inline-block;
        padding: 0.35rem 0.9rem;
        border-radius: 9999px;
        font-size: 0.82rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin-right: 0.5rem;
        margin-bottom: 0.5rem;
    }
    .badge-outdoor { background-color: #dcfce7; color: #166534; }
    .badge-indoor { background-color: #e0e7ff; color: #3730a3; }
    .badge-watersports { background-color: #cffafe; color: #155e75; }
    .badge-safety { background-color: #fee2e2; color: #991b1b; }
    .badge-hybrid { background-color: #fef3c7; color: #92400e; }
    
    /* Fact pill */
    .fact-pill {
        display: inline-block;
        background: #f1f5f9;
        border: 1px solid #cbd5e1;
        padding: 0.35rem 0.75rem;
        border-radius: 8px;
        font-size: 0.88rem;
        font-weight: 600;
        color: #334155;
        margin: 0.2rem;
    }

    /* Safety Alert Box */
    .safety-box {
        background-color: #fff1f2;
        border: 1px solid #fecdd3;
        border-left: 5px solid #e11d48;
        padding: 1rem 1.2rem;
        border-radius: 10px;
        color: #9f1239;
        font-size: 0.95rem;
        margin-top: 0.8rem;
    }
    
    /* Checklist box */
    .checklist-box {
        background: #f8fafc;
        border: 1px solid #e2e8f0;
        border-radius: 10px;
        padding: 1rem;
    }
    
    /* Metric Card */
    .stat-card {
        background: #f8fafc;
        border: 1px solid #e2e8f0;
        border-radius: 12px;
        padding: 1rem;
        text-align: center;
    }
    .stat-val {
        font-size: 1.6rem;
        font-weight: 800;
        color: #1e293b;
    }
    .stat-lbl {
        font-size: 0.8rem;
        color: #64748b;
        text-transform: uppercase;
        font-weight: 600;
    }
</style>
""", unsafe_allow_html=True)


@st.cache_resource
def get_engine():
    return WeatherInferenceEngine()


engine = get_engine()

# Presets configuration
PRESETS = {
    "Custom Selection": None,
    "☀️ Pleasant Spring Hike (22°C, Calm, Clear)": {"temp": 22.0, "rain": "None", "wind": 10.0, "time": "Afternoon"},
    "🏖️ Hot Summer Beach Day (31°C, Gentle Breeze, Dry)": {"temp": 31.0, "rain": "None", "wind": 14.0, "time": "Afternoon"},
    "⚡ Violent Storm Alert (18°C, Heavy Rain, Gale Wind)": {"temp": 18.0, "rain": "Heavy Rain / Thunderstorm", "wind": 58.0, "time": "Evening"},
    "🔥 Scorching Heatwave (39°C, Dry, Calm)": {"temp": 39.0, "rain": "None", "wind": 8.0, "time": "Afternoon"},
    "🌧️ Cozy Rainy Café Day (11°C, Moderate Rain, Breezy)": {"temp": 11.0, "rain": "Moderate Rain", "wind": 18.0, "time": "Morning"},
    "🪁 Breezy Coastal Kite Day (23°C, Strong Wind, Clear)": {"temp": 23.0, "rain": "None", "wind": 38.0, "time": "Afternoon"},
    "❄️ Crisp Freezing Winter (2°C, Calm, Dry)": {"temp": 2.0, "rain": "None", "wind": 8.0, "time": "Morning"},
    "🌧️ Warm Drizzle Market Walk (24°C, Light Drizzle, Breezy)": {"temp": 24.0, "rain": "Light Drizzle", "wind": 12.0, "time": "Morning"}
}

# ----------------- SIDEBAR: INPUT CONTROLS -----------------
with st.sidebar:
    st.markdown("### ⚙️ Weather Controls")
    
    # Preset Selector
    selected_preset = st.selectbox(
        "⚡ Quick Weather Preset",
        options=list(PRESETS.keys()),
        index=0,
        help="Quickly load realistic weather combinations"
    )
    
    preset_data = PRESETS.get(selected_preset)
    
    default_temp = preset_data["temp"] if preset_data else 22.0
    default_rain = preset_data["rain"] if preset_data else "None"
    default_wind = preset_data["wind"] if preset_data else 12.0
    default_time = preset_data["time"] if preset_data else "Afternoon"

    st.markdown("---")
    
    # 1. Temperature Input
    temp_input = st.slider(
        "🌡️ Temperature (°C)",
        min_value=-10.0,
        max_value=50.0,
        value=float(default_temp),
        step=0.5,
        help="Ambient temperature in degrees Celsius"
    )
    
    temp_category_label = categorize_temperature(temp_input)
    st.caption(f"Categorized as: **{temp_category_label}**")
    
    st.markdown("---")

    # 2. Rain Condition
    rain_options = [
        "None",
        "Light Drizzle",
        "Moderate Rain",
        "Heavy Rain / Thunderstorm"
    ]
    rain_index = rain_options.index(default_rain) if default_rain in rain_options else 0
    rain_input = st.selectbox(
        "🌧️ Precipitation / Rain",
        options=rain_options,
        index=rain_index,
        help="Current precipitation intensity"
    )
    
    st.markdown("---")

    # 3. Wind Speed
    wind_input = st.slider(
        "💨 Wind Speed (km/h)",
        min_value=0.0,
        max_value=100.0,
        value=float(default_wind),
        step=1.0,
        help="Current sustained wind speed in km/h"
    )
    wind_category_label = categorize_wind(wind_input)
    st.caption(f"Categorized as: **{wind_category_label}**")
    
    st.markdown("---")

    # Optional context factors
    with st.expander("🕒 Additional Context (Optional)"):
        time_options = ["Morning", "Afternoon", "Evening", "Night"]
        time_index = time_options.index(default_time) if default_time in time_options else 1
        time_input = st.selectbox("Time of Day", options=time_options, index=time_index)
        humidity_input = st.slider("Relative Humidity (%)", 10, 100, 55, step=5)

    st.markdown("---")
    st.markdown(
        "<div style='font-size:0.78rem; color:#64748b; text-align:center;'>"
        "AI Mini Project: Knowledge Base & Inference System<br/>"
        "Weather Activity Advisor v1.0"
        "</div>",
        unsafe_allow_html=True
    )

# ----------------- MAIN CONTENT & INFERENCE EXECUTION -----------------

# Execute Inference Engine
inference_result = engine.run_inference(
    temperature=temp_input,
    rain=rain_input,
    wind_speed=wind_input,
    time_of_day=time_input,
    humidity=humidity_input
)

fired_rule = inference_result.fired_rule
wm = inference_result.working_memory

# Category Badge Helper
badge_class_map = {
    "Outdoor": "badge-outdoor",
    "Indoor": "badge-indoor",
    "Water Sports": "badge-watersports",
    "Safety Alert": "badge-safety",
    "Hybrid": "badge-hybrid"
}
badge_class = badge_class_map.get(inference_result.category, "badge-outdoor")

# Header Hero
st.markdown(f"""
<div class="hero-container">
    <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap;">
        <div>
            <h1 class="hero-title">⛅ Weather Activity Advisor</h1>
            <p class="hero-subtitle">Rule-Based Expert System for Intelligent Activity Planning & Safety Guidance</p>
        </div>
        <div style="text-align:right;">
            <span class="badge-chip {badge_class}" style="font-size: 0.95rem; padding: 0.5rem 1.2rem; background: rgba(255,255,255,0.22); color:#ffffff; border:1px solid rgba(255,255,255,0.4);">
                ● {inference_result.category.upper()}
            </span>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# Top Metrics Row: Weather Snapshot
col_m1, col_m2, col_m3, col_m4 = st.columns(4)
with col_m1:
    st.markdown(f"""
    <div class="stat-card">
        <div class="stat-val">{wm['temperature']}°C</div>
        <div class="stat-lbl">{wm['temp_category']}</div>
    </div>
    """, unsafe_allow_html=True)
with col_m2:
    st.markdown(f"""
    <div class="stat-card">
        <div class="stat-val">{wm['rain']}</div>
        <div class="stat-lbl">Precipitation</div>
    </div>
    """, unsafe_allow_html=True)
with col_m3:
    st.markdown(f"""
    <div class="stat-card">
        <div class="stat-val">{wm['wind_speed']} km/h</div>
        <div class="stat-lbl">{wm['wind_category']}</div>
    </div>
    """, unsafe_allow_html=True)
with col_m4:
    score_color = "#16a34a" if inference_result.suitability_score >= 75 else "#ea580c" if inference_result.suitability_score >= 50 else "#dc2626"
    st.markdown(f"""
    <div class="stat-card">
        <div class="stat-val" style="color: {score_color};">{inference_result.suitability_score}%</div>
        <div class="stat-lbl">Suitability Index</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<br/>", unsafe_allow_html=True)

# Hero Recommendation Card
with st.container():
    st.markdown(f"""
    <div class="rec-card">
        <div style="display:flex; justify-content:space-between; align-items:flex-start;">
            <div>
                <span class="badge-chip {badge_class}">{inference_result.category}</span>
                <span style="font-size: 0.85rem; font-weight: 600; color: #64748b;">Triggered Rule: {fired_rule.rule_id}</span>
            </div>
            <div>
                <span style="font-size:0.85rem; color:#475569; font-weight:600;">Priority: {fired_rule.priority}/100</span>
            </div>
        </div>
        <h2 style="color: #0f172a; margin-top: 0.8rem; margin-bottom: 0.5rem; font-weight: 800; font-size: 1.85rem;">
            🎯 {inference_result.primary_activity}
        </h2>
        <p style="color: #475569; font-size: 1.05rem; line-height: 1.5; margin-bottom: 0.5rem;">
            {fired_rule.explanation}
        </p>
    </div>
    """, unsafe_allow_html=True)

# ----------------- TABS SECTION -----------------
tab_rec, tab_xai, tab_kb, tab_export = st.tabs([
    "📋 Plan & Checklist",
    "🧠 AI Inference Engine Trace",
    "📚 Knowledge Base (Rules)",
    "💾 Export Advisory"
])

# TAB 1: Plan & Checklist
with tab_rec:
    col_left, col_right = st.columns([1.1, 0.9])
    
    with col_left:
        # Clothing & Packing Checklist
        st.subheader("🎒 Recommended Attire & Equipment")
        if inference_result.clothing_checklist:
            for item in inference_result.clothing_checklist:
                st.checkbox(f"**{item}**", value=True, key=f"pack_{item}")
        else:
            st.info("No special clothing gear required.")

        # Safety Advisories
        if inference_result.safety_advisories:
            st.subheader("⚠️ Safety Warnings & Precautions")
            for warning in inference_result.safety_advisories:
                st.markdown(f"""
                <div class="safety-box">
                    <strong>Notice:</strong> {warning}
                </div>
                """, unsafe_allow_html=True)
                
    with col_right:
        st.subheader("🔄 Alternative Activities")
        if inference_result.alternative_activities:
            for i, alt in enumerate(inference_result.alternative_activities, 1):
                st.markdown(f"""
                <div style="background:#ffffff; border:1px solid #e2e8f0; border-radius:10px; padding:0.85rem 1.1rem; margin-bottom:0.6rem; display:flex; align-items:center;">
                    <div style="font-size:1.3rem; margin-right:0.8rem;">✨</div>
                    <div>
                        <strong style="color:#1e293b; font-size:0.95rem;">{alt}</strong>
                        <div style="font-size:0.75rem; color:#64748b;">Alternative Option #{i}</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.write("No alternatives designated.")

# TAB 2: AI Inference Engine Trace (Explainable AI)
with tab_xai:
    st.subheader("🔍 Forward Chaining & Explainable AI (XAI) Trace")
    st.write(
        "This trace illustrates how the **Inference Engine** processed input facts through the "
        "Knowledge Base pattern-matcher, applied conflict resolution, and produced the final recommendation."
    )
    
    # Step 1: Working Memory Facts
    st.markdown("#### 1. Working Memory (Fact Assertion)")
    wm_cols = st.columns(3)
    with wm_cols[0]:
        st.json({
            "temperature": f"{wm['temperature']} °C",
            "temp_category": wm['temp_category']
        })
    with wm_cols[1]:
        st.json({
            "precipitation": wm['rain'],
            "wind_speed": f"{wm['wind_speed']} km/h"
        })
    with wm_cols[2]:
        st.json({
            "wind_category": wm['wind_category'],
            "time_of_day": wm['time_of_day']
        })

    # Step 2: Conflict Resolution
    st.markdown("#### 2. Pattern Matching & Conflict Resolution")
    num_candidates = len(inference_result.candidate_rules)
    st.info(
        f"**{num_candidates} rule(s)** satisfied all IF-conditions. "
        f"The conflict resolver selected **{fired_rule.rule_id}** due to highest priority ({fired_rule.priority}) "
        f"and condition specificity."
    )
    
    # Step 3: Fired Rule Summary
    st.markdown(f"""
    <div style="background:#eff6ff; border:1px solid #bfdbfe; border-radius:12px; padding:1.2rem; margin-bottom:1.5rem;">
        <h4 style="margin:0; color:#1e40af;">🎯 Fired Winning Rule: {fired_rule.name} ({fired_rule.rule_id})</h4>
        <p style="margin:0.5rem 0 0 0; color:#1e3a8a; font-size:0.95rem;">{inference_result.explanation_summary}</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Step 4: Full Rule Evaluation Audit Table
    st.markdown("#### 3. Complete Rule Base Audit Log")
    eval_data = []
    for t in inference_result.evaluation_traces:
        status_symbol = "✅ MATCHED" if t.matched else "❌ MISMATCH"
        is_winner = "🏆 FIRED" if t.rule_id == fired_rule.rule_id else status_symbol
        eval_data.append({
            "Status": is_winner,
            "Rule ID": t.rule_id,
            "Rule Name": t.rule_name,
            "Priority": t.priority,
            "Evaluation Reason": "; ".join(t.reasons),
            "Associated Recommendation": t.recommendation
        })
    
    st.dataframe(eval_data, width=1200)

# TAB 3: Knowledge Base Inspector
with tab_kb:
    st.subheader("📚 Knowledge Base Architecture")
    st.write(
        "The Knowledge Base consists of modular declarative IF-THEN production rules. "
        "Each rule defines antecedents (conditions on temperature, rain, and wind) and consequents (actions, gear, warnings)."
    )
    
    all_rules = get_all_rules()
    kb_records = []
    for r in all_rules:
        kb_records.append({
            "Rule ID": r.rule_id,
            "Name": r.name,
            "Priority": r.priority,
            "Temp Condition": ", ".join(r.temp_categories) if r.temp_categories else "ANY",
            "Rain Condition": ", ".join(r.rain_conditions) if r.rain_conditions else "ANY",
            "Wind Condition": ", ".join(r.wind_categories) if r.wind_categories else "ANY",
            "Category": r.category,
            "Recommendation": r.recommendation,
            "Suitability": f"{r.suitability_score}%"
        })
    st.dataframe(kb_records, width=1200)

# TAB 4: Export Session
with tab_export:
    st.subheader("💾 Export Weather Advisory")
    st.write("Generate and download a structured text or JSON advisory report for your records.")
    
    report_dict = {
        "timestamp": datetime.now().isoformat(),
        "input_weather": wm,
        "recommendation": {
            "primary_activity": inference_result.primary_activity,
            "category": inference_result.category,
            "suitability_score": f"{inference_result.suitability_score}%",
            "fired_rule_id": fired_rule.rule_id,
            "fired_rule_name": fired_rule.name,
            "rule_priority": fired_rule.priority,
            "explanation": fired_rule.explanation
        },
        "clothing_checklist": inference_result.clothing_checklist,
        "safety_warnings": inference_result.safety_advisories,
        "alternative_activities": inference_result.alternative_activities
    }
    
    json_str = json.dumps(report_dict, indent=2)
    
    col_d1, col_d2 = st.columns(2)
    with col_d1:
        st.download_button(
            label="📥 Download Advisory Report (JSON)",
            data=json_str,
            file_name=f"weather_activity_advisory_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            mime="application/json"
        )
    with col_d2:
        plain_text = f"""==================================================
WEATHER ACTIVITY ADVISOR - EXPERT SYSTEM REPORT
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
==================================================

WEATHER CONDITIONS:
- Temperature: {wm['temperature']}°C ({wm['temp_category']})
- Precipitation: {wm['rain']}
- Wind Speed: {wm['wind_speed']} km/h ({wm['wind_category']})
- Time of Day: {wm['time_of_day']}

PRIMARY RECOMMENDATION:
- Activity: {inference_result.primary_activity}
- Category: {inference_result.category}
- Suitability Score: {inference_result.suitability_score}%
- Fired Rule: {fired_rule.name} ({fired_rule.rule_id})

REASONING / EXPLANATION:
{fired_rule.explanation}

RECOMMENDED CLOTHING & GEAR:
{chr(10).join(['- ' + c for c in inference_result.clothing_checklist])}

SAFETY ADVISORIES:
{chr(10).join(['- ' + w for w in inference_result.safety_advisories])}

ALTERNATIVE ACTIVITIES:
{chr(10).join(['- ' + a for a in inference_result.alternative_activities])}
==================================================
"""
        st.download_button(
            label="📄 Download Advisory Summary (TXT)",
            data=plain_text,
            file_name=f"weather_advisory_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
            mime="text/plain"
        )
    
    st.code(json_str, language="json")
