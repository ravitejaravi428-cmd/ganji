"""
Weather Activity Advisor - Tkinter Desktop UI
A zero-dependency desktop application for the AI Expert System.
Uses Python's built-in Tkinter framework with modern ttk styling.
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
from knowledge_base import categorize_temperature, categorize_wind
from inference_engine import WeatherInferenceEngine


class WeatherAdvisorGUI(tk.Tk):
    """Modern Tkinter GUI for the Weather Activity Advisor."""

    def __init__(self):
        super().__init__()
        self.title("Weather Activity Advisor | AI Expert System")
        self.geometry("980x760")
        self.minsize(880, 680)

        # Initialize Inference Engine
        self.engine = WeatherInferenceEngine()

        # State Variables
        self.temp_var = tk.DoubleVar(value=22.0)
        self.rain_var = tk.StringVar(value="None")
        self.wind_var = tk.DoubleVar(value=12.0)
        self.time_var = tk.StringVar(value="Afternoon")

        # Styling
        self.setup_styles()
        self.create_widgets()
        
        # Initial run
        self.consult_advisor()

    def setup_styles(self):
        self.configure(bg="#f1f5f9")
        self.style = ttk.Style(self)
        self.style.theme_use("clam")

        # Colors
        bg_card = "#ffffff"
        primary_color = "#2563eb"
        text_dark = "#0f172a"

        self.style.configure(".", background="#f1f5f9", foreground=text_dark, font=("Segoe UI", 10))
        self.style.configure("Card.TFrame", background=bg_card, relief="flat")
        self.style.configure("Header.TLabel", background="#1e3a8a", foreground="#ffffff", font=("Segoe UI", 16, "bold"))
        self.style.configure("SubHeader.TLabel", background="#1e3a8a", foreground="#93c5fd", font=("Segoe UI", 9))
        self.style.configure("SectionTitle.TLabel", background=bg_card, foreground="#1e293b", font=("Segoe UI", 11, "bold"))
        self.style.configure("Value.TLabel", background=bg_card, foreground="#2563eb", font=("Segoe UI", 10, "bold"))
        self.style.configure("Primary.TButton", background=primary_color, foreground="#ffffff", font=("Segoe UI", 11, "bold"), padding=8)
        self.style.map("Primary.TButton", background=[("active", "#1d4ed8")])

    def create_widgets(self):
        # 1. Header Banner
        header_frame = tk.Frame(self, bg="#1e3a8a", height=80, padx=25, pady=15)
        header_frame.pack(fill=tk.X)

        title_lbl = tk.Label(
            header_frame,
            text="⛅ Weather Activity Advisor",
            bg="#1e3a8a",
            fg="#ffffff",
            font=("Segoe UI", 17, "bold")
        )
        title_lbl.pack(anchor="w")

        sub_lbl = tk.Label(
            header_frame,
            text="Rule-Based Expert System (IF–THEN Knowledge Base & Forward-Chaining Inference)",
            bg="#1e3a8a",
            fg="#bfdbfe",
            font=("Segoe UI", 9)
        )
        sub_lbl.pack(anchor="w")

        # 2. Main Two-Column Layout
        main_pane = tk.PanedWindow(self, orient=tk.HORIZONTAL, bg="#e2e8f0", sashwidth=4)
        main_pane.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)

        # Left Column: Inputs & Presets
        left_frame = tk.Frame(main_pane, bg="#ffffff", padx=18, pady=18, relief="ridge", bd=1)
        main_pane.add(left_frame, minsize=380)

        # Right Column: Output & Tabs
        right_frame = tk.Frame(main_pane, bg="#ffffff", padx=18, pady=18, relief="ridge", bd=1)
        main_pane.add(right_frame, minsize=520)

        # --- LEFT PANEL: INPUT CONTROLS ---
        tk.Label(left_frame, text="⚙️ Weather Inputs", font=("Segoe UI", 13, "bold"), bg="#ffffff", fg="#0f172a").pack(anchor="w", pady=(0, 10))

        # Preset Quick Buttons Frame
        preset_frame = tk.LabelFrame(left_frame, text=" Quick Presets ", font=("Segoe UI", 9, "bold"), bg="#ffffff", fg="#475569", padx=10, pady=8)
        preset_frame.pack(fill=tk.X, pady=(0, 14))

        p_row1 = tk.Frame(preset_frame, bg="#ffffff")
        p_row1.pack(fill=tk.X, pady=2)
        tk.Button(p_row1, text="☀️ Pleasant Spring", bg="#f0fdf4", fg="#166534", font=("Segoe UI", 8), command=lambda: self.load_preset(22, "None", 10)).pack(side=tk.LEFT, expand=True, fill=tk.X, padx=2)
        tk.Button(p_row1, text="🏖️ Hot Beach", bg="#eff6ff", fg="#1e40af", font=("Segoe UI", 8), command=lambda: self.load_preset(31, "None", 12)).pack(side=tk.LEFT, expand=True, fill=tk.X, padx=2)

        p_row2 = tk.Frame(preset_frame, bg="#ffffff")
        p_row2.pack(fill=tk.X, pady=2)
        tk.Button(p_row2, text="⚡ Severe Storm", bg="#fef2f2", fg="#991b1b", font=("Segoe UI", 8), command=lambda: self.load_preset(18, "Heavy Rain / Thunderstorm", 60)).pack(side=tk.LEFT, expand=True, fill=tk.X, padx=2)
        tk.Button(p_row2, text="🌧️ Cozy Rainy Café", bg="#fff7ed", fg="#9a3412", font=("Segoe UI", 8), command=lambda: self.load_preset(11, "Moderate Rain", 18)).pack(side=tk.LEFT, expand=True, fill=tk.X, padx=2)

        # 1. Temperature Control
        temp_box = tk.Frame(left_frame, bg="#ffffff")
        temp_box.pack(fill=tk.X, pady=8)

        t_lbl_frame = tk.Frame(temp_box, bg="#ffffff")
        t_lbl_frame.pack(fill=tk.X)
        tk.Label(t_lbl_frame, text="🌡️ Temperature (°C):", font=("Segoe UI", 10, "bold"), bg="#ffffff").pack(side=tk.LEFT)
        self.temp_val_lbl = tk.Label(t_lbl_frame, text="22.0°C (Mild / Pleasant)", font=("Segoe UI", 9, "bold"), bg="#ffffff", fg="#2563eb")
        self.temp_val_lbl.pack(side=tk.RIGHT)

        self.temp_scale = ttk.Scale(
            temp_box,
            from_=-10.0,
            to=50.0,
            variable=self.temp_var,
            orient=tk.HORIZONTAL,
            command=self.update_temp_label
        )
        self.temp_scale.pack(fill=tk.X, pady=4)

        # 2. Precipitation / Rain
        rain_box = tk.Frame(left_frame, bg="#ffffff")
        rain_box.pack(fill=tk.X, pady=8)
        tk.Label(rain_box, text="🌧️ Precipitation / Rain:", font=("Segoe UI", 10, "bold"), bg="#ffffff").pack(anchor="w")

        rain_combobox = ttk.Combobox(
            rain_box,
            textvariable=self.rain_var,
            values=["None", "Light Drizzle", "Moderate Rain", "Heavy Rain / Thunderstorm"],
            state="readonly"
        )
        rain_combobox.pack(fill=tk.X, pady=4)

        # 3. Wind Speed Control
        wind_box = tk.Frame(left_frame, bg="#ffffff")
        wind_box.pack(fill=tk.X, pady=8)

        w_lbl_frame = tk.Frame(wind_box, bg="#ffffff")
        w_lbl_frame.pack(fill=tk.X)
        tk.Label(w_lbl_frame, text="💨 Wind Speed (km/h):", font=("Segoe UI", 10, "bold"), bg="#ffffff").pack(side=tk.LEFT)
        self.wind_val_lbl = tk.Label(w_lbl_frame, text="12.0 km/h (Calm)", font=("Segoe UI", 9, "bold"), bg="#ffffff", fg="#2563eb")
        self.wind_val_lbl.pack(side=tk.RIGHT)

        self.wind_scale = ttk.Scale(
            wind_box,
            from_=0.0,
            to=90.0,
            variable=self.wind_var,
            orient=tk.HORIZONTAL,
            command=self.update_wind_label
        )
        self.wind_scale.pack(fill=tk.X, pady=4)

        # Consult Button
        action_btn = tk.Button(
            left_frame,
            text="🚀 Consult AI Advisor",
            bg="#2563eb",
            fg="#ffffff",
            font=("Segoe UI", 11, "bold"),
            relief="flat",
            pady=10,
            cursor="hand2",
            command=self.consult_advisor
        )
        action_btn.pack(fill=tk.X, pady=(20, 10))

        # --- RIGHT PANEL: RESULTS & EXPLANATIONS ---
        # Notebook for Tabs
        self.notebook = ttk.Notebook(right_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)

        # Tab 1: Advisory Result
        self.tab_advisory = ttk.Frame(self.notebook, padding=12)
        self.notebook.add(self.tab_advisory, text="🎯 Recommendation")

        # Tab 2: AI Inference Trace
        self.tab_trace = ttk.Frame(self.notebook, padding=12)
        self.notebook.add(self.tab_trace, text="🧠 Inference Trace (XAI)")

        # Populate Tab 1: Recommendation widgets
        self.setup_advisory_tab()

        # Populate Tab 2: Trace widgets
        self.setup_trace_tab()

    def setup_advisory_tab(self):
        # Result Header Card
        self.res_card = tk.Frame(self.tab_advisory, bg="#eff6ff", padx=15, pady=12, relief="groove", bd=1)
        self.res_card.pack(fill=tk.X, pady=(0, 10))

        top_info = tk.Frame(self.res_card, bg="#eff6ff")
        top_info.pack(fill=tk.X)
        self.category_badge = tk.Label(top_info, text="OUTDOOR", bg="#dcfce7", fg="#166534", font=("Segoe UI", 9, "bold"), padx=8, pady=2)
        self.category_badge.pack(side=tk.LEFT)

        self.suitability_badge = tk.Label(top_info, text="Suitability: 95%", bg="#eff6ff", fg="#2563eb", font=("Segoe UI", 9, "bold"))
        self.suitability_badge.pack(side=tk.RIGHT)

        self.activity_title = tk.Label(
            self.res_card,
            text="Scenic Mountain Hiking & Trail Trekking",
            font=("Segoe UI", 14, "bold"),
            bg="#eff6ff",
            fg="#0f172a",
            wraplength=480,
            justify=tk.LEFT
        )
        self.activity_title.pack(anchor="w", pady=(8, 4))

        self.explanation_lbl = tk.Label(
            self.res_card,
            text="Explanation rationale...",
            font=("Segoe UI", 9),
            bg="#eff6ff",
            fg="#334155",
            wraplength=480,
            justify=tk.LEFT
        )
        self.explanation_lbl.pack(anchor="w")

        # Details in a scrolled text
        tk.Label(self.tab_advisory, text="🎒 Recommended Gear & Checklist:", font=("Segoe UI", 10, "bold")).pack(anchor="w", pady=(8, 2))
        self.clothing_box = tk.Text(self.tab_advisory, height=4, wrap=tk.WORD, font=("Segoe UI", 9), bg="#f8fafc", relief="solid", bd=1)
        self.clothing_box.pack(fill=tk.X, pady=(0, 6))

        tk.Label(self.tab_advisory, text="⚠️ Safety Warnings & Precautions:", font=("Segoe UI", 10, "bold"), fg="#b91c1c").pack(anchor="w", pady=(4, 2))
        self.safety_box = tk.Text(self.tab_advisory, height=3, wrap=tk.WORD, font=("Segoe UI", 9), bg="#fef2f2", fg="#991b1b", relief="solid", bd=1)
        self.safety_box.pack(fill=tk.X, pady=(0, 6))

        tk.Label(self.tab_advisory, text="🔄 Backup Alternative Activities:", font=("Segoe UI", 10, "bold")).pack(anchor="w", pady=(4, 2))
        self.alts_box = tk.Text(self.tab_advisory, height=3, wrap=tk.WORD, font=("Segoe UI", 9), bg="#f8fafc", relief="solid", bd=1)
        self.alts_box.pack(fill=tk.X)

    def setup_trace_tab(self):
        tk.Label(
            self.tab_trace,
            text="Rule-Based Forward-Chaining Audit Log:",
            font=("Segoe UI", 10, "bold")
        ).pack(anchor="w", pady=(0, 6))

        self.trace_text = scrolledtext.ScrolledText(
            self.tab_trace,
            wrap=tk.WORD,
            font=("Consolas", 9),
            bg="#0f172a",
            fg="#e2e8f0",
            relief="flat"
        )
        self.trace_text.pack(fill=tk.BOTH, expand=True)

    def update_temp_label(self, val):
        temp = float(val)
        cat = categorize_temperature(temp)
        self.temp_val_lbl.config(text=f"{temp:.1f}°C ({cat})")

    def update_wind_label(self, val):
        wind = float(val)
        cat = categorize_wind(wind)
        self.wind_val_lbl.config(text=f"{wind:.1f} km/h ({cat})")

    def load_preset(self, temp, rain, wind):
        self.temp_var.set(temp)
        self.rain_var.set(rain)
        self.wind_var.set(wind)
        self.update_temp_label(temp)
        self.update_wind_label(wind)
        self.consult_advisor()

    def consult_advisor(self):
        t = round(self.temp_var.get(), 1)
        r = self.rain_var.get()
        w = round(self.wind_var.get(), 1)

        result = self.engine.run_inference(temperature=t, rain=r, wind_speed=w)

        # Update Tab 1
        self.activity_title.config(text=result.primary_activity)
        self.explanation_lbl.config(text=result.fired_rule.explanation)
        self.suitability_badge.config(text=f"Suitability: {result.suitability_score}%")

        # Category Badge styling
        cat = result.category
        if cat == "Outdoor":
            self.category_badge.config(text=f"● {cat.upper()}", bg="#dcfce7", fg="#166534")
        elif cat == "Indoor":
            self.category_badge.config(text=f"● {cat.upper()}", bg="#e0e7ff", fg="#3730a3")
        elif cat == "Water Sports":
            self.category_badge.config(text=f"● {cat.upper()}", bg="#cffafe", fg="#155e75")
        elif cat == "Safety Alert":
            self.category_badge.config(text=f"● {cat.upper()}", bg="#fee2e2", fg="#991b1b")
        else:
            self.category_badge.config(text=f"● {cat.upper()}", bg="#fef3c7", fg="#92400e")

        # Checklist
        self.clothing_box.delete("1.0", tk.END)
        for item in result.clothing_checklist:
            self.clothing_box.insert(tk.END, f" ✔ {item}\n")

        # Safety
        self.safety_box.delete("1.0", tk.END)
        if result.safety_advisories:
            for alert in result.safety_advisories:
                self.safety_box.insert(tk.END, f" ⚠ {alert}\n")
        else:
            self.safety_box.insert(tk.END, " No specific safety hazards reported for this weather.\n")

        # Alternatives
        self.alts_box.delete("1.0", tk.END)
        for i, alt in enumerate(result.alternative_activities, 1):
            self.alts_box.insert(tk.END, f" {i}. {alt}\n")

        # Tab 2: Trace text
        self.trace_text.delete("1.0", tk.END)
        trace_output = []
        trace_output.append("=== WORKING MEMORY (FACTS) ===")
        for k, v in result.working_memory.items():
            trace_output.append(f"  • {k:<15} : {v}")

        trace_output.append("\n=== CONFLICT RESOLUTION ===")
        trace_output.append(f"  • Matched candidate rules: {len(result.candidate_rules)}")
        trace_output.append(f"  • Winning rule fired     : {result.fired_rule.rule_id} (Priority {result.fired_rule.priority})")

        trace_output.append("\n=== DETAILED RULE EVALUATION TRACE ===")
        for t in result.evaluation_traces:
            status = "[MATCH]" if t.matched else "[FAIL] "
            winner = " -> (FIRED)" if t.rule_id == result.fired_rule.rule_id else ""
            trace_output.append(f"{status} {t.rule_id:<20} P={t.priority:<3} {t.rule_name}{winner}")
            for reason in t.reasons:
                trace_output.append(f"       Grounds: {reason}")

        self.trace_text.insert(tk.END, "\n".join(trace_output))


if __name__ == "__main__":
    app = WeatherAdvisorGUI()
    app.mainloop()
