"""
Weather Activity Advisor - Web Application Server
A zero-dependency HTTP web server powered by Python's standard library.
Serves a modern, responsive single-page web application on http://localhost:5000
and provides a REST API (/api/recommend) connected to the AI Expert System.
"""

import json
import urllib.parse
import webbrowser
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from inference_engine import WeatherInferenceEngine
from knowledge_base import get_all_rules

engine = WeatherInferenceEngine()

HTML_PAGE = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Weather Activity Advisor | AI Expert System</title>
    <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap" rel="stylesheet">
    <style>
        :root {
            --primary: #2563eb;
            --primary-dark: #1d4ed8;
            --bg: #f8fafc;
            --card-bg: #ffffff;
            --text-main: #0f172a;
            --text-muted: #64748b;
            --border: #e2e8f0;
        }
        * {
            box-sizing: border-box;
            margin: 0;
            padding: 0;
            font-family: 'Plus Jakarta Sans', -apple-system, sans-serif;
        }
        body {
            background-color: var(--bg);
            color: var(--text-main);
            line-height: 1.5;
            padding-bottom: 3rem;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 1.5rem;
        }
        /* Hero Header */
        .hero {
            background: linear-gradient(135deg, #1e3a8a 0%, #3b82f6 50%, #06b6d4 100%);
            padding: 2.2rem 2.4rem;
            border-radius: 20px;
            color: white;
            margin-bottom: 2rem;
            box-shadow: 0 10px 25px -5px rgba(59, 130, 246, 0.35);
            display: flex;
            justify-content: space-between;
            align-items: center;
            flex-wrap: wrap;
            gap: 1rem;
        }
        .hero h1 {
            font-size: 2.2rem;
            font-weight: 800;
            letter-spacing: -0.02em;
        }
        .hero p {
            font-size: 1.05rem;
            opacity: 0.92;
            margin-top: 0.3rem;
        }
        .status-chip {
            background: rgba(255, 255, 255, 0.2);
            backdrop-filter: blur(8px);
            border: 1px solid rgba(255, 255, 255, 0.3);
            padding: 0.5rem 1.2rem;
            border-radius: 9999px;
            font-size: 0.88rem;
            font-weight: 700;
            letter-spacing: 0.05em;
            text-transform: uppercase;
        }

        /* Layout Grid */
        .grid {
            display: grid;
            grid-template-columns: 380px 1fr;
            gap: 1.8rem;
        }
        @media (max-width: 900px) {
            .grid { grid-template-columns: 1fr; }
        }

        /* Cards */
        .card {
            background: var(--card-bg);
            border: 1px solid var(--border);
            border-radius: 16px;
            padding: 1.6rem;
            box-shadow: 0 4px 20px -2px rgba(0, 0, 0, 0.04);
            margin-bottom: 1.5rem;
        }
        .card-title {
            font-size: 1.15rem;
            font-weight: 700;
            margin-bottom: 1.2rem;
            display: flex;
            align-items: center;
            gap: 0.5rem;
            color: var(--text-main);
        }

        /* Preset Buttons */
        .preset-grid {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 0.5rem;
            margin-bottom: 1.5rem;
        }
        .btn-preset {
            background: #f1f5f9;
            border: 1px solid #cbd5e1;
            padding: 0.6rem 0.75rem;
            border-radius: 10px;
            font-size: 0.8rem;
            font-weight: 600;
            color: #334155;
            cursor: pointer;
            text-align: left;
            transition: all 0.15s ease;
        }
        .btn-preset:hover {
            background: #e2e8f0;
            border-color: #94a3b8;
            transform: translateY(-1px);
        }

        /* Input Controls */
        .input-group {
            margin-bottom: 1.4rem;
        }
        .input-label-row {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 0.4rem;
            font-size: 0.92rem;
            font-weight: 600;
        }
        .input-val-badge {
            color: var(--primary);
            font-weight: 700;
        }
        input[type="range"] {
            width: 100%;
            height: 6px;
            border-radius: 5px;
            background: #e2e8f0;
            outline: none;
            -webkit-appearance: none;
            cursor: pointer;
        }
        input[type="range"]::-webkit-slider-thumb {
            -webkit-appearance: none;
            width: 18px;
            height: 18px;
            border-radius: 50%;
            background: var(--primary);
            cursor: pointer;
            box-shadow: 0 2px 6px rgba(37, 99, 235, 0.4);
        }
        select {
            width: 100%;
            padding: 0.75rem;
            border-radius: 10px;
            border: 1px solid var(--border);
            font-size: 0.95rem;
            font-weight: 500;
            background-color: #fff;
            color: var(--text-main);
            outline: none;
            cursor: pointer;
        }
        select:focus {
            border-color: var(--primary);
        }

        /* Hero Recommendation */
        .rec-hero {
            background: #ffffff;
            border: 1px solid #e2e8f0;
            border-left: 6px solid var(--primary);
            border-radius: 16px;
            padding: 1.8rem;
            box-shadow: 0 4px 20px -2px rgba(0, 0, 0, 0.05);
            margin-bottom: 1.5rem;
        }
        .badge {
            display: inline-block;
            padding: 0.35rem 0.9rem;
            border-radius: 9999px;
            font-size: 0.8rem;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            margin-right: 0.5rem;
        }
        .badge-outdoor { background: #dcfce7; color: #166534; }
        .badge-indoor { background: #e0e7ff; color: #3730a3; }
        .badge-watersports { background: #cffafe; color: #155e75; }
        .badge-safety { background: #fee2e2; color: #991b1b; }
        .badge-hybrid { background: #fef3c7; color: #92400e; }

        .rec-activity {
            font-size: 1.8rem;
            font-weight: 800;
            color: var(--text-main);
            margin: 0.8rem 0 0.4rem 0;
        }
        .rec-rationale {
            color: #475569;
            font-size: 1.05rem;
        }

        /* Metrics Grid */
        .metrics-grid {
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 1rem;
            margin-bottom: 1.5rem;
        }
        @media (max-width: 650px) {
            .metrics-grid { grid-template-columns: 1fr 1fr; }
        }
        .metric-card {
            background: #ffffff;
            border: 1px solid var(--border);
            border-radius: 12px;
            padding: 1rem;
            text-align: center;
        }
        .metric-val {
            font-size: 1.5rem;
            font-weight: 800;
            color: var(--text-main);
        }
        .metric-lbl {
            font-size: 0.78rem;
            font-weight: 600;
            color: var(--text-muted);
            text-transform: uppercase;
        }

        /* Tabs */
        .tabs {
            display: flex;
            gap: 0.5rem;
            border-bottom: 2px solid var(--border);
            margin-bottom: 1.2rem;
        }
        .tab-btn {
            background: none;
            border: none;
            padding: 0.75rem 1.2rem;
            font-size: 0.95rem;
            font-weight: 600;
            color: var(--text-muted);
            cursor: pointer;
            border-bottom: 3px solid transparent;
            margin-bottom: -2px;
            transition: all 0.15s ease;
        }
        .tab-btn.active {
            color: var(--primary);
            border-bottom-color: var(--primary);
        }
        .tab-content { display: none; }
        .tab-content.active { display: block; }

        /* Checklist & Safety Box */
        .check-item {
            display: flex;
            align-items: center;
            gap: 0.6rem;
            padding: 0.6rem 0;
            border-bottom: 1px solid #f1f5f9;
            font-size: 0.95rem;
            font-weight: 500;
        }
        .safety-box {
            background: #fff1f2;
            border: 1px solid #fecdd3;
            border-left: 5px solid #e11d48;
            padding: 0.9rem 1.1rem;
            border-radius: 10px;
            color: #9f1239;
            font-size: 0.92rem;
            margin-top: 0.6rem;
        }
        .alt-chip {
            background: #f8fafc;
            border: 1px solid #e2e8f0;
            border-radius: 10px;
            padding: 0.8rem 1rem;
            margin-bottom: 0.5rem;
            font-weight: 600;
            color: #1e293b;
            display: flex;
            align-items: center;
            gap: 0.6rem;
        }

        /* Trace log */
        .trace-pre {
            background: #0f172a;
            color: #e2e8f0;
            padding: 1.2rem;
            border-radius: 12px;
            font-family: 'Consolas', monospace;
            font-size: 0.85rem;
            line-height: 1.6;
            overflow-x: auto;
            max-height: 420px;
        }
        table {
            width: 100%;
            border-collapse: collapse;
            font-size: 0.88rem;
        }
        th, td {
            text-align: left;
            padding: 0.75rem 0.9rem;
            border-bottom: 1px solid var(--border);
        }
        th {
            background: #f8fafc;
            color: var(--text-muted);
            font-weight: 600;
            text-transform: uppercase;
            font-size: 0.75rem;
        }
    </style>
</head>
<body>
    <div class="container">
        <!-- Hero Header -->
        <div class="hero">
            <div>
                <h1>⛅ Weather Activity Advisor</h1>
                <p>AI Expert System: Temperature + Rain + Wind &rarr; Suitable Activity Recommendation</p>
            </div>
            <div id="hero-badge" class="status-chip">
                AI Inference Ready
            </div>
        </div>

        <!-- Metrics Snapshot -->
        <div class="metrics-grid">
            <div class="metric-card">
                <div id="m-temp" class="metric-val">22.0°C</div>
                <div id="m-temp-cat" class="metric-lbl">Mild / Pleasant</div>
            </div>
            <div class="metric-card">
                <div id="m-rain" class="metric-val">None</div>
                <div class="metric-lbl">Precipitation</div>
            </div>
            <div class="metric-card">
                <div id="m-wind" class="metric-val">12.0 km/h</div>
                <div id="m-wind-cat" class="metric-lbl">Calm Breeze</div>
            </div>
            <div class="metric-card">
                <div id="m-score" class="metric-val" style="color: #16a34a;">95%</div>
                <div class="metric-lbl">Suitability Score</div>
            </div>
        </div>

        <div class="grid">
            <!-- Left Column: Controls -->
            <div>
                <div class="card">
                    <div class="card-title">⚡ Quick Weather Presets</div>
                    <div class="preset-grid">
                        <button class="btn-preset" onclick="setPreset(22, 'None', 10)">☀️ Pleasant Spring</button>
                        <button class="btn-preset" onclick="setPreset(31, 'None', 12)">🏖️ Summer Beach</button>
                        <button class="btn-preset" onclick="setPreset(18, 'Heavy Rain / Thunderstorm', 60)">⚡ Violent Storm</button>
                        <button class="btn-preset" onclick="setPreset(39, 'None', 8)">🔥 Extreme Heat</button>
                        <button class="btn-preset" onclick="setPreset(11, 'Moderate Rain', 18)">🌧️ Cozy Rainy Café</button>
                        <button class="btn-preset" onclick="setPreset(23, 'None', 38)">🪁 Coastal Wind</button>
                        <button class="btn-preset" onclick="setPreset(2, 'None', 8)">❄️ Crisp Winter</button>
                        <button class="btn-preset" onclick="setPreset(24, 'Light Drizzle', 12)">🌧️ Light Drizzle</button>
                    </div>

                    <div class="card-title">⚙️ Weather Parameters</div>

                    <!-- Temperature -->
                    <div class="input-group">
                        <div class="input-label-row">
                            <span>🌡️ Temperature</span>
                            <span id="temp-val-text" class="input-val-badge">22.0°C</span>
                        </div>
                        <input type="range" id="temp-slider" min="-10" max="50" step="0.5" value="22" oninput="onInputChanged()">
                    </div>

                    <!-- Rain -->
                    <div class="input-group">
                        <div class="input-label-row">
                            <span>🌧️ Precipitation</span>
                        </div>
                        <select id="rain-select" onchange="onInputChanged()">
                            <option value="None">None (Dry)</option>
                            <option value="Light Drizzle">Light Drizzle</option>
                            <option value="Moderate Rain">Moderate Rain</option>
                            <option value="Heavy Rain / Thunderstorm">Heavy Rain / Thunderstorm</option>
                        </select>
                    </div>

                    <!-- Wind Speed -->
                    <div class="input-group">
                        <div class="input-label-row">
                            <span>💨 Wind Speed</span>
                            <span id="wind-val-text" class="input-val-badge">12.0 km/h</span>
                        </div>
                        <input type="range" id="wind-slider" min="0" max="90" step="1" value="12" oninput="onInputChanged()">
                    </div>
                </div>
            </div>

            <!-- Right Column: Outputs -->
            <div>
                <!-- Primary Hero Card -->
                <div class="rec-hero">
                    <div style="display:flex; justify-content:space-between; align-items:center;">
                        <span id="cat-badge" class="badge badge-outdoor">Outdoor</span>
                        <span id="rule-badge" style="font-size:0.85rem; font-weight:600; color:var(--text-muted);">Rule: R10</span>
                    </div>
                    <div id="primary-activity" class="rec-activity">
                        Scenic Mountain Hiking & Nature Trek
                    </div>
                    <p id="rec-rationale" class="rec-rationale">
                        Mild temperature, dry weather, and gentle breeze offer optimal hiking conditions.
                    </p>
                </div>

                <!-- Tabs -->
                <div class="card">
                    <div class="tabs">
                        <button class="tab-btn active" onclick="switchTab('tab-plan', this)">📋 Attire & Checklist</button>
                        <button class="tab-btn" onclick="switchTab('tab-xai', this)">🧠 AI Inference Trace (XAI)</button>
                        <button class="tab-btn" onclick="switchTab('tab-kb', this)">📚 Knowledge Base</button>
                    </div>

                    <!-- Tab 1: Attire & Safety -->
                    <div id="tab-plan" class="tab-content active">
                        <h4 style="margin-bottom:0.6rem; color:#1e293b;">🎒 Recommended Gear & Checklist</h4>
                        <div id="checklist-container"></div>

                        <h4 style="margin-top:1.2rem; margin-bottom:0.6rem; color:#b91c1c;">⚠️ Health & Safety Advisories</h4>
                        <div id="safety-container"></div>

                        <h4 style="margin-top:1.2rem; margin-bottom:0.6rem; color:#1e293b;">🔄 Alternative Activities</h4>
                        <div id="alternatives-container"></div>
                    </div>

                    <!-- Tab 2: XAI Trace -->
                    <div id="tab-xai" class="tab-content">
                        <p style="font-size:0.9rem; color:var(--text-muted); margin-bottom:1rem;">
                            Live forward-chaining execution trace showing Working Memory fact assertion, condition evaluations, and conflict resolution:
                        </p>
                        <pre id="trace-box" class="trace-pre"></pre>
                    </div>

                    <!-- Tab 3: Knowledge Base Table -->
                    <div id="tab-kb" class="tab-content">
                        <p style="font-size:0.9rem; color:var(--text-muted); margin-bottom:1rem;">
                            The expert system Knowledge Base contains declarative IF-THEN rules with assigned priorities:
                        </p>
                        <div style="overflow-x:auto;">
                            <table id="kb-table">
                                <thead>
                                    <tr>
                                        <th>Rule ID</th>
                                        <th>Priority</th>
                                        <th>Conditions</th>
                                        <th>Recommendation</th>
                                    </tr>
                                </thead>
                                <tbody id="kb-tbody"></tbody>
                            </table>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <script>
        function setPreset(temp, rain, wind) {
            document.getElementById('temp-slider').value = temp;
            document.getElementById('rain-select').value = rain;
            document.getElementById('wind-slider').value = wind;
            onInputChanged();
        }

        function switchTab(tabId, btn) {
            document.querySelectorAll('.tab-content').forEach(el => el.classList.remove('active'));
            document.querySelectorAll('.tab-btn').forEach(el => el.classList.remove('active'));
            document.getElementById(tabId).classList.add('active');
            btn.classList.add('active');
        }

        async function onInputChanged() {
            const temp = parseFloat(document.getElementById('temp-slider').value);
            const rain = document.getElementById('rain-select').value;
            const wind = parseFloat(document.getElementById('wind-slider').value);

            document.getElementById('temp-val-text').textContent = temp.toFixed(1) + '°C';
            document.getElementById('wind-val-text').textContent = wind.toFixed(1) + ' km/h';

            try {
                const res = await fetch(`/api/recommend?temp=${temp}&rain=${encodeURIComponent(rain)}&wind=${wind}`);
                const data = await res.json();
                renderResult(data);
            } catch (err) {
                console.error("API error:", err);
            }
        }

        function renderResult(data) {
            // Metrics
            document.getElementById('m-temp').textContent = data.working_memory.temperature + '°C';
            document.getElementById('m-temp-cat').textContent = data.working_memory.temp_category;
            document.getElementById('m-rain').textContent = data.working_memory.rain;
            document.getElementById('m-wind').textContent = data.working_memory.wind_speed + ' km/h';
            document.getElementById('m-wind-cat').textContent = data.working_memory.wind_category;
            
            const scoreEl = document.getElementById('m-score');
            scoreEl.textContent = data.suitability_score + '%';
            scoreEl.style.color = data.suitability_score >= 75 ? '#16a34a' : data.suitability_score >= 50 ? '#ea580c' : '#dc2626';

            // Primary Activity
            document.getElementById('primary-activity').textContent = data.primary_activity;
            document.getElementById('rec-rationale').textContent = data.fired_rule.explanation;
            document.getElementById('rule-badge').textContent = `Rule: ${data.fired_rule.rule_id} (Priority: ${data.fired_rule.priority}/100)`;

            // Category Badge
            const catBadge = document.getElementById('cat-badge');
            catBadge.textContent = data.category;
            catBadge.className = 'badge';
            if (data.category === 'Outdoor') catBadge.classList.add('badge-outdoor');
            else if (data.category === 'Indoor') catBadge.classList.add('badge-indoor');
            else if (data.category === 'Water Sports') catBadge.classList.add('badge-watersports');
            else if (data.category === 'Safety Alert') catBadge.classList.add('badge-safety');
            else catBadge.classList.add('badge-hybrid');

            // Attire Checklist
            const checkContainer = document.getElementById('checklist-container');
            checkContainer.innerHTML = '';
            data.clothing_checklist.forEach(item => {
                const div = document.createElement('div');
                div.className = 'check-item';
                div.innerHTML = `<span style="color:#16a34a; font-size:1.1rem;">✔</span> <span>${item}</span>`;
                checkContainer.appendChild(div);
            });

            // Safety Advisories
            const safetyContainer = document.getElementById('safety-container');
            safetyContainer.innerHTML = '';
            if (data.safety_advisories && data.safety_advisories.length > 0) {
                data.safety_advisories.forEach(warning => {
                    const div = document.createElement('div');
                    div.className = 'safety-box';
                    div.innerHTML = `<strong>Notice:</strong> ${warning}`;
                    safetyContainer.appendChild(div);
                });
            } else {
                safetyContainer.innerHTML = '<div style="color:#64748b; font-size:0.9rem; padding:0.5rem 0;">No severe hazards detected for this weather.</div>';
            }

            // Alternatives
            const altContainer = document.getElementById('alternatives-container');
            altContainer.innerHTML = '';
            data.alternative_activities.forEach((alt, idx) => {
                const div = document.createElement('div');
                div.className = 'alt-chip';
                div.innerHTML = `<span>✨</span> <div><strong>${alt}</strong> <div style="font-size:0.75rem; color:#64748b;">Alternative #${idx+1}</div></div>`;
                altContainer.appendChild(div);
            });

            // Trace box
            let traceText = '=== WORKING MEMORY (ASSERTED FACTS) ===\\n';
            for (const [k, v] of Object.entries(data.working_memory)) {
                traceText += `  • ${k.padEnd(16)} : ${v}\\n`;
            }
            traceText += '\\n=== CONFLICT RESOLUTION ===\\n';
            traceText += `  • Candidate rules satisfied: ${data.candidate_rules_count}\\n`;
            traceText += `  • Winning rule fired       : ${data.fired_rule.rule_id} (Priority: ${data.fired_rule.priority})\\n`;
            traceText += `  • Rule Justification       : ${data.fired_rule.explanation}\\n\\n`;
            traceText += '=== COMPLETE RULE BASE AUDIT LOG ===\\n';
            data.evaluation_traces.forEach(t => {
                const tag = t.rule_id === data.fired_rule.rule_id ? '🏆 [FIRED]   ' : (t.matched ? '✅ [MATCH]   ' : '❌ [MISMATCH]');
                traceText += `${tag} ${t.rule_id.padEnd(20)} P=${String(t.priority).padEnd(3)} ${t.rule_name}\\n`;
                t.reasons.forEach(r => {
                    traceText += `       Grounds: ${r}\\n`;
                });
            });
            document.getElementById('trace-box').textContent = traceText;
        }

        async function loadKB() {
            try {
                const res = await fetch('/api/rules');
                const rules = await res.json();
                const tbody = document.getElementById('kb-tbody');
                tbody.innerHTML = '';
                rules.forEach(r => {
                    const tr = document.createElement('tr');
                    tr.innerHTML = `
                        <td><strong>${r.rule_id}</strong></td>
                        <td><span style="font-weight:700; color:#2563eb;">${r.priority}</span></td>
                        <td style="font-size:0.8rem; color:#475569;">
                            ${r.temp_categories ? 'Temp: ' + r.temp_categories.join(', ') : 'Temp: ANY'}<br/>
                            ${r.rain_conditions ? 'Rain: ' + r.rain_conditions.join(', ') : 'Rain: ANY'}<br/>
                            ${r.wind_categories ? 'Wind: ' + r.wind_categories.join(', ') : 'Wind: ANY'}
                        </td>
                        <td>${r.recommendation}</td>
                    `;
                    tbody.appendChild(tr);
                });
            } catch (e) {
                console.error("Failed to load KB:", e);
            }
        }

        // Initialize on page load
        window.onload = () => {
            onInputChanged();
            loadKB();
        };
    </script>
</body>
</html>
"""


class WeatherAppRequestHandler(BaseHTTPRequestHandler):
    """Handles HTTP requests for web UI and API."""

    def log_message(self, format, *args):
        # Suppress noisy standard request logging
        return

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path

        if path == "/" or path == "/index.html":
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(HTML_PAGE.encode("utf-8"))

        elif path == "/api/recommend":
            query = urllib.parse.parse_qs(parsed.query)
            temp = float(query.get("temp", [22.0])[0])
            rain = query.get("rain", ["None"])[0]
            wind = float(query.get("wind", [12.0])[0])

            result = engine.run_inference(temperature=temp, rain=rain, wind_speed=wind)

            response_data = {
                "working_memory": result.working_memory,
                "primary_activity": result.primary_activity,
                "category": result.category,
                "suitability_score": result.suitability_score,
                "clothing_checklist": result.clothing_checklist,
                "safety_advisories": result.safety_advisories,
                "alternative_activities": result.alternative_activities,
                "fired_rule": {
                    "rule_id": result.fired_rule.rule_id,
                    "name": result.fired_rule.name,
                    "priority": result.fired_rule.priority,
                    "explanation": result.fired_rule.explanation
                },
                "candidate_rules_count": len(result.candidate_rules),
                "evaluation_traces": [
                    {
                        "rule_id": t.rule_id,
                        "rule_name": t.rule_name,
                        "priority": t.priority,
                        "matched": t.matched,
                        "reasons": t.reasons,
                        "recommendation": t.recommendation
                    }
                    for t in result.evaluation_traces
                ]
            }

            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(json.dumps(response_data).encode("utf-8"))

        elif path == "/api/rules":
            rules = get_all_rules()
            data = [
                {
                    "rule_id": r.rule_id,
                    "name": r.name,
                    "priority": r.priority,
                    "temp_categories": r.temp_categories,
                    "rain_conditions": r.rain_conditions,
                    "wind_categories": r.wind_categories,
                    "recommendation": r.recommendation,
                    "category": r.category,
                    "suitability_score": r.suitability_score
                }
                for r in rules
            ]
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(json.dumps(data).encode("utf-8"))

        else:
            self.send_response(404)
            self.end_headers()


def run_server(port=5000, auto_open=True):
    import sys
    if hasattr(sys.stdout, 'reconfigure'):
        try:
            sys.stdout.reconfigure(encoding='utf-8')
        except Exception:
            pass

    server_address = ("127.0.0.1", port)
    httpd = HTTPServer(server_address, WeatherAppRequestHandler)
    print("=" * 65)
    print(f"WEATHER ACTIVITY ADVISOR WEB APP IS RUNNING!")
    print(f"Localhost Link: http://localhost:{port}")
    print("=" * 65)

    if auto_open:
        threading.Timer(0.8, lambda: webbrowser.open(f"http://localhost:{port}")).start()

    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping server...")
        httpd.server_close()


if __name__ == "__main__":
    run_server(port=5000, auto_open=True)
