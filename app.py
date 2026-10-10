import streamlit as st


st.set_page_config(
    page_title="EcoSmart | Energy Intelligence",
    page_icon="☀️",
    layout="wide",
    initial_sidebar_state="expanded",
)


SOLAR_CAPACITY_KW = 4.2
SOLAR_PEAK_HOURS_PER_DAY = 4.5
ELECTRICITY_RATE_INR_PER_KWH = 8.5
GRID_CO2_KG_PER_KWH = 0.7
MONTH_DAYS = 30

TIME_PROFILES = {
    "Morning": {"solar_factor": 0.48, "label": "07:00–11:00"},
    "Peak Solar Afternoon (12–3 PM)": {
        "solar_factor": 1.0,
        "label": "12:00–15:00",
    },
    "Evening Peak (6–9 PM)": {"solar_factor": 0.08, "label": "18:00–21:00"},
    "Night": {"solar_factor": 0.0, "label": "21:00–07:00"},
}
WEATHER_FACTORS = {"Sunny": 1.0, "Cloudy": 0.55, "Rainy": 0.25}
APPLIANCE_LOADS_KW = {
    "AC": 1.5,
    "Washing Machine": 0.6,
    "Water Pump": 0.75,
    "EV Charger": 3.3,
    "Fridge": 0.15,
    "Lights": 0.1,
}
HEAVY_APPLIANCES = ("AC", "Washing Machine", "Water Pump", "EV Charger")
SHIFTABLE_APPLIANCES = ("Washing Machine", "Water Pump")
APPLIANCE_PRIORITIES = {
    "Washing Machine": "High",
    "Water Pump": "High",
    "AC": "Medium",
    "EV Charger": "Flexible",
}
PEAK_SOLAR_ACTIONS = (
    {
        "id": "ev_charging",
        "icon": "🚗",
        "title": "EV Charging Slot Available",
        "description": "Use up to 1.5 kW of clean solar to add an estimated 15–20 km of range per hour.",
        "load_kw": 1.5,
    },
    {
        "id": "heavy_laundry",
        "icon": "🧺",
        "title": "Run Heavy Laundry Cycle",
        "description": "Schedule a washing machine and dryer cycle using up to 0.5 kW of surplus solar.",
        "load_kw": 0.5,
    },
    {
        "id": "overhead_tank",
        "icon": "🚰",
        "title": "Fill Overhead Water Tank",
        "description": "Run the water pump with up to 1.0 kW of available clean solar power.",
        "load_kw": 1.0,
    },
    {
        "id": "home_battery",
        "icon": "🔋",
        "title": "Charge Home Battery / Powerstation",
        "description": "Store up to 1.0 kW of today's solar surplus for the evening peak (6–9 PM).",
        "load_kw": 1.0,
    },
)

for appliance in APPLIANCE_LOADS_KW:
    st.session_state.setdefault(
        f"appliance_state_{appliance}", appliance in {"Fridge", "Lights"}
    )
for action in PEAK_SOLAR_ACTIONS:
    st.session_state.setdefault(f"peak_solar_action_{action['id']}", False)


st.markdown(
    """
    <style>
    :root {
        --canvas: #0a1414;
        --surface: #111f20;
        --surface-raised: #172829;
        --line: rgba(174, 218, 197, .14);
        --text: #edf8f1;
        --muted: #9bb1a7;
        --green: #83f3a6;
        --green-deep: #163e31;
        --blue: #76c9ff;
        --red: #ff8a8a;
    }
    html, body, [class*="css"] { font-family: 'Trebuchet MS', 'Segoe UI', sans-serif; }
    .stApp { background: radial-gradient(ellipse at 80% -10%, #173c30 0%, var(--canvas) 48%); color: var(--text); }
    [data-testid="stHeader"] { background: rgba(10, 20, 20, .76); }
    [data-testid="stSidebar"] {
        background: linear-gradient(165deg, #123b32 0%, #0c2422 48%, #101a1d 100%);
        border-right: 1px solid rgba(131, 243, 166, .16);
    }
    [data-testid="stSidebar"] * { color: #eaf7ee; }
    [data-testid="stSidebar"] [data-testid="stCaptionContainer"] { color: #b2ccc0; }
    [data-testid="stSidebar"] [data-testid="stVerticalBlockBorderWrapper"] {
        background: rgba(255, 255, 255, .045);
        border: 1px solid rgba(198, 237, 215, .14);
        border-radius: 10px;
        box-shadow: 0 10px 28px rgba(0, 0, 0, .12);
    }
    [data-testid="stSidebar"] [data-baseweb="select"] > div,
    [data-testid="stSidebar"] [data-baseweb="popover"] > div {
        background: #18312e; border-color: rgba(198, 237, 215, .24); color: #f5fff8;
    }
    [data-testid="stSidebar"] [data-testid="stSlider"] [role="slider"] { background: var(--green); }
    [data-testid="stSidebar"] [data-testid="stWidgetLabel"] p { color: #eaf7ee; font-weight: 600; }
    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p { color: #d7e9df; }
    h1, h2, h3, h4 { color: var(--text) !important; letter-spacing: 0 !important; }
    h1 { font-family: Georgia, 'Times New Roman', serif !important; font-size: 2.55rem !important; }
    p, label, li { color: var(--text); }
    [data-testid="stMarkdownContainer"] a { color: var(--green); }
    [data-testid="stMetric"] {
        min-height: 126px; padding: 1.05rem 1.1rem;
        background: linear-gradient(145deg, rgba(25, 45, 44, .96), rgba(16, 30, 31, .96));
        border: 1px solid var(--line); border-radius: 10px;
        box-shadow: inset 0 1px rgba(255,255,255,.035), 0 8px 22px rgba(0,0,0,.12);
        transition: border-color .2s ease, transform .2s ease, box-shadow .2s ease;
    }
    [data-testid="stMetric"]:hover { border-color: rgba(131,243,166,.48); transform: translateY(-2px); box-shadow: 0 10px 30px rgba(0,0,0,.22), 0 0 16px rgba(131,243,166,.08); }
    [data-testid="stMetricLabel"] p { color: #afc3b9 !important; font-size: .83rem; font-weight: 600; }
    [data-testid="stMetricValue"] { color: var(--green) !important; font-size: 1.75rem; font-weight: 700; }
    [data-testid="stMetricDelta"] { color: #b9d8c8 !important; }
    [data-testid="stVerticalBlockBorderWrapper"] {
        background: rgba(19, 34, 35, .76); border-color: var(--line); border-radius: 10px;
    }
    [data-testid="stRadio"] label, [data-testid="stCheckbox"] label { color: #e5f2e9 !important; }
    [data-baseweb="select"] > div { background: #172829; border-color: var(--line); }
    [data-baseweb="slider"] [role="slider"] { background: var(--green); }
    [data-testid="stCaptionContainer"] { color: var(--muted); }
    .hero {
        position: relative; overflow: hidden; padding: 1.65rem 1.9rem;
        border: 1px solid rgba(185, 255, 209, .22); border-radius: 12px;
        background: linear-gradient(112deg, #143f32 0%, #176246 55%, #267858 100%);
        box-shadow: 0 18px 46px rgba(0,0,0,.22), inset 0 1px rgba(255,255,255,.08);
    }
    .hero:after { content: '☼'; position: absolute; right: 4%; top: -48px; font-size: 190px; color: #c9ff8b; opacity: .14; line-height: 1; }
    .hero-kicker { color: #c3f2c9; font-size: .75rem; font-weight: 700; letter-spacing: 1.5px; text-transform: uppercase; }
    .hero-title { margin: .35rem 0 .2rem; color: white; font-family: Georgia, 'Times New Roman', serif; font-size: 2.5rem; font-weight: 700; }
    .hero-copy { max-width: 660px; margin: 0; color: #d5eadc; font-size: .98rem; }
    .hero-chip { position: absolute; right: 1.5rem; bottom: 1.25rem; z-index: 1; color: #e8ffe9; border: 1px solid rgba(220,255,224,.25); background: rgba(8,37,26,.26); padding: .42rem .72rem; border-radius: 6px; font-size: .78rem; }
    .section-heading { margin: 1.55rem 0 .72rem; color: #eaf7ef; font-size: 1.13rem; font-weight: 700; }
    .section-caption { margin: -.35rem 0 .8rem; color: var(--muted); font-size: .87rem; }
    .status-line { margin-top: .7rem; padding: .83rem 1rem; color: #d8e9e0; background: rgba(25,44,43,.65); border-left: 3px solid var(--green); border-radius: 0 8px 8px 0; }
    .status-line strong { color: var(--green); }
    .alert-card { display: flex; gap: .85rem; align-items: flex-start; margin: .85rem 0; padding: 1rem 1.1rem; border-radius: 9px; background: rgba(17,31,32,.96); }
    .alert-icon { font-size: 1.35rem; line-height: 1.2; }
    .alert-title { margin-bottom: .2rem; color: #f4fff8; font-weight: 700; }
    .alert-copy { color: #c5d7ce; font-size: .91rem; line-height: 1.5; }
    .alert-green { border: 1px solid rgba(131,243,166,.34); box-shadow: inset 3px 0 #62e890, 0 0 22px rgba(89,226,134,.06); }
    .alert-red { border: 1px solid rgba(255,138,138,.35); box-shadow: inset 3px 0 #ff7070, 0 0 22px rgba(255,91,91,.06); }
    .alert-blue { border: 1px solid rgba(118,201,255,.35); box-shadow: inset 3px 0 #67bdff, 0 0 22px rgba(103,189,255,.06); }
    [data-testid="stVerticalBlockBorderWrapper"]:has(.recommendation-card) {
        background: linear-gradient(145deg, rgba(23, 62, 47, .98), rgba(17, 39, 34, .98));
        border: 1px solid rgba(131, 243, 166, .52);
        box-shadow: 0 10px 30px rgba(0, 0, 0, .2), 0 0 24px rgba(89, 226, 134, .1);
    }
    .recommendation-card { display:flex; gap:.85rem; align-items:flex-start; margin:.1rem 0 .65rem; }
    .recommendation-card .alert-icon { color: var(--green); }
    [data-testid="stVerticalBlockBorderWrapper"]:has(.recommendation-card) [data-testid="stButton"] button {
        min-height: 2.8rem; color: #092116; background: var(--green); border: 0; font-weight: 700;
    }
    [data-testid="stVerticalBlockBorderWrapper"]:has(.recommendation-card) [data-testid="stButton"] button:hover {
        color: #092116; background: #a2ffb8; border: 0;
    }
    [data-testid="stVerticalBlockBorderWrapper"]:has(.solar-action-card) {
        height: 100%; background: linear-gradient(150deg, rgba(22, 43, 40, .98), rgba(16, 30, 31, .98));
        border: 1px solid rgba(174, 218, 197, .2); border-radius: 9px;
    }
    .solar-action-card { min-height: 108px; }
    .solar-action-title { margin: .05rem 0 .4rem; color: #f1fff5; font-size: 1rem; font-weight: 700; }
    .solar-action-copy { min-height: 3.1rem; margin: 0; color: #bcd0c5; font-size: .87rem; line-height: 1.5; }
    .solar-action-priority { margin-bottom: .35rem; color: #83f3a6; font-size: .72rem; font-weight: 700; text-transform: uppercase; }
    [data-testid="stProgressBar"] > div > div { background: #83f3a6; }
    [data-testid="stProgressBar"] { margin: .1rem 0 .4rem; }
    .solar-action-state { color: #9bb1a7; font-size: .78rem; }
    .flow-card { padding: 1.1rem 1.2rem; background: rgba(17,31,32,.9); border: 1px solid var(--line); border-radius: 10px; }
    .flow-head { display:flex; justify-content:space-between; gap:1rem; margin-bottom:1rem; color:#eaf7ef; font-weight:700; }
    .flow-head span:last-child { color:var(--muted); font-size:.78rem; font-weight:500; }
    .flow-row { display:grid; grid-template-columns: 135px 1fr 62px; align-items:center; gap:.7rem; margin:.8rem 0; }
    .flow-label { color:#c5d8ce; font-size:.86rem; }
    .flow-track { height:10px; overflow:hidden; background:#253735; border-radius:20px; }
    .flow-fill { height:100%; min-width:2px; border-radius:20px; }
    .flow-value { color:#eef9f2; text-align:right; font-size:.84rem; font-variant-numeric:tabular-nums; }
    .flow-foot { padding-top:.8rem; margin-top:.75rem; border-top:1px solid var(--line); color:var(--muted); font-size:.8rem; }
    .roi-label { margin-bottom:.8rem; color:#e9f7ee; font-weight:700; }
    .roi-note { margin-top:.75rem; color:#9fb5aa; font-size:.8rem; line-height:1.5; }
    hr { border-color: var(--line) !important; }
    footer { visibility: hidden; }
    @media (max-width: 760px) {
        .hero { padding: 1.3rem; }
        .hero-title { font-size: 2rem; }
        .hero-chip { position: static; display: inline-block; margin-top: .8rem; }
        .flow-row { grid-template-columns: 105px 1fr 54px; gap: .45rem; }
    }
    </style>
    """,
    unsafe_allow_html=True,
)


with st.sidebar:
    st.markdown("## ☀️ EcoSmart")
    st.caption("HOME ENERGY INTELLIGENCE")
    st.markdown("---")

    with st.container(border=True):
        st.markdown("### 🕒 &nbsp; Live conditions")
        selected_time = st.selectbox("Time of day", list(TIME_PROFILES))
        selected_weather = st.radio("Weather outlook", list(WEATHER_FACTORS), horizontal=True)

    with st.container(border=True):
        st.markdown("### ⚡ &nbsp; Appliance state")
        active_appliances = {
            appliance: st.checkbox(
                appliance,
                key=f"appliance_state_{appliance}",
            )
            for appliance in APPLIANCE_LOADS_KW
        }

    with st.container(border=True):
        st.markdown("### 🎚️ &nbsp; Household demand")
        household_load_kw = st.slider(
            "Current consumption (kW)",
            min_value=0.0,
            max_value=10.0,
            value=2.4,
            step=0.1,
            help="Baseline household demand. Peak-solar automations are added only when surplus is available.",
        )

    st.markdown("<div style='height:.5rem'></div>", unsafe_allow_html=True)
    st.caption("DEMO MODE  ·  Simulated household data")


solar_factor = TIME_PROFILES[selected_time]["solar_factor"] * WEATHER_FACTORS[selected_weather]
solar_available_kw = SOLAR_CAPACITY_KW * solar_factor
base_household_load_kw = household_load_kw
available_solar_surplus_kw = max(solar_available_kw - base_household_load_kw, 0.0)
remaining_solar_surplus_kw = available_solar_surplus_kw
solar_action_results = {}
for action in PEAK_SOLAR_ACTIONS:
    is_enabled = st.session_state[f"peak_solar_action_{action['id']}"]
    allocated_kw = (
        min(action["load_kw"], remaining_solar_surplus_kw) if is_enabled else 0.0
    )
    remaining_solar_surplus_kw -= allocated_kw
    solar_action_results[action["id"]] = {
        "enabled": is_enabled,
        "allocated_kw": allocated_kw,
        "coverage": allocated_kw / action["load_kw"],
    }

automated_solar_load_kw = sum(
    result["allocated_kw"] for result in solar_action_results.values()
)
household_load_kw = base_household_load_kw + automated_solar_load_kw
grid_import_kw = max(household_load_kw - solar_available_kw, 0.0)
solar_surplus_kw = max(solar_available_kw - household_load_kw, 0.0)
solar_serving_load_kw = min(solar_available_kw, household_load_kw)

# Monthly estimates use 4.5 peak-sun hours/day, 72% self-consumption, and a flat demo tariff.
estimated_monthly_solar_kwh = (
    SOLAR_CAPACITY_KW
    * SOLAR_PEAK_HOURS_PER_DAY
    * WEATHER_FACTORS[selected_weather]
    * 0.72
    * MONTH_DAYS
)
estimated_monthly_savings_inr = estimated_monthly_solar_kwh * ELECTRICITY_RATE_INR_PER_KWH


def auto_schedule_heavy_loads(appliances_to_schedule, available_solar_surplus_kw):
    for appliance in appliances_to_schedule:
        st.session_state[f"appliance_state_{appliance}"] = True

    scheduled_load_kw = sum(
        APPLIANCE_LOADS_KW[appliance] for appliance in appliances_to_schedule
    )
    solar_energy_used_kwh = min(scheduled_load_kw, available_solar_surplus_kw)
    st.session_state["last_auto_scheduled_appliances"] = list(appliances_to_schedule)
    st.session_state["last_auto_schedule_saved_kwh"] = solar_energy_used_kwh
    st.session_state["last_auto_schedule_savings_inr"] = (
        solar_energy_used_kwh * ELECTRICITY_RATE_INR_PER_KWH
    )


st.markdown(
    f"""
    <div class="hero">
      <div class="hero-kicker">Renewables · demand response · intelligent control</div>
      <div class="hero-title">EcoSmart</div>
      <p class="hero-copy">A clearer view of your home's energy. Balance clean generation, household demand, and grid reliance in real time.</p>
      <div class="hero-chip">● &nbsp; SIMULATION LIVE</div>
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown('<div class="section-heading">⚡ &nbsp; Live energy overview</div>', unsafe_allow_html=True)
solar_col, load_col, grid_col, surplus_col = st.columns(4)
solar_col.metric("Solar available", f"{solar_available_kw:.1f} kW", selected_weather)
load_col.metric("Household demand", f"{household_load_kw:.1f} kW", TIME_PROFILES[selected_time]["label"])
grid_col.metric("Grid import", f"{grid_import_kw:.1f} kW")
surplus_col.metric("Available surplus", f"{solar_surplus_kw:.1f} kW")

st.markdown(
    f'<div class="status-line">☀️ &nbsp; <strong>{selected_time}</strong> · {selected_weather} conditions '
    f'&nbsp; / &nbsp; Solar is covering <strong>{solar_serving_load_kw:.1f} kW</strong> of current demand.</div>',
    unsafe_allow_html=True,
)

active_heavy_appliances = [
    appliance for appliance in HEAVY_APPLIANCES if active_appliances[appliance]
]
off_heavy_appliances = [
    appliance for appliance in HEAVY_APPLIANCES if not active_appliances[appliance]
]
shiftable_loads_active = any(active_appliances[name] for name in SHIFTABLE_APPLIANCES)

st.markdown('<div class="section-heading">✦ &nbsp; EcoSmart recommendations</div>', unsafe_allow_html=True)
if selected_time == "Evening Peak (6–9 PM)" and len(active_heavy_appliances) >= 2:
    st.markdown(
        '<div class="alert-card alert-red"><div class="alert-icon">⚠️</div><div>'
        '<div class="alert-title">Peak Load Warning</div>'
        '<div class="alert-copy">High energy pricing and grid strain expected. Turn off non-critical appliances to reduce your evening peak demand.</div>'
        '</div></div>',
        unsafe_allow_html=True,
    )
elif solar_available_kw > 2.0:
    with st.container(border=True):
        st.markdown(
            '<div class="recommendation-card"><div class="alert-icon">☀️</div><div>'
            '<div class="alert-title">High Solar Energy Surplus Detected! Optimal time to schedule heavy loads.</div>'
            '<div class="alert-copy">Use available solar generation to run heavy appliances before relying on grid power. Savings below estimate one hour of surplus solar used at the demo tariff.</div>'
            '</div></div>',
            unsafe_allow_html=True,
        )
        st.button(
            "⚡ Auto-Schedule Heavy Loads Now",
            key="auto_schedule_heavy_loads",
            type="primary",
            width="stretch",
            disabled=not off_heavy_appliances,
            on_click=auto_schedule_heavy_loads,
            args=(tuple(off_heavy_appliances), solar_surplus_kw),
        )
        if not off_heavy_appliances:
            st.caption("All heavy appliances are already on.")
        if st.session_state.get("last_auto_scheduled_appliances"):
            scheduled_names = ", ".join(
                st.session_state["last_auto_scheduled_appliances"]
            )
            st.success(
                f"Scheduled {scheduled_names}. Estimated immediate savings: "
                f"₹{st.session_state['last_auto_schedule_savings_inr']:.2f} per hour "
                f"({st.session_state['last_auto_schedule_saved_kwh']:.2f} kWh of solar used)."
            )
elif solar_available_kw >= 1.5 and not shiftable_loads_active:
    st.markdown(
        '<div class="alert-card alert-green"><div class="alert-icon">☀️</div><div>'
        '<div class="alert-title">Solar Surplus Opportunity</div>'
        '<div class="alert-copy">Shift heavy loads now to utilize free solar energy! Run the washing machine or water pump while clean generation is available.</div>'
        '</div></div>',
        unsafe_allow_html=True,
    )
elif solar_surplus_kw > 0.15:
    st.markdown(
        f'<div class="alert-card alert-blue"><div class="alert-icon">↗️</div><div>'
        f'<div class="alert-title">Grid Export Available</div>'
        f'<div class="alert-copy">About {solar_surplus_kw:.1f} kW of solar generation is above current demand. Export it if your system and utility plan support net metering.</div>'
        '</div></div>',
        unsafe_allow_html=True,
    )
else:
    st.markdown(
        '<div class="alert-card alert-blue"><div class="alert-icon">◉</div><div>'
        '<div class="alert-title">Balanced operating mode</div>'
        '<div class="alert-copy">No immediate demand-response action is needed. EcoSmart will update its guidance as the simulated conditions change.</div>'
        '</div></div>',
        unsafe_allow_html=True,
    )

if selected_time == "Peak Solar Afternoon (12–3 PM)" and solar_available_kw > 2.0:
    st.markdown(
        '<div class="section-heading">☀️ Peak Solar Utilization Suggestions (12:30 PM - 2:00 PM)</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        f'<div class="section-caption">{available_solar_surplus_kw:.1f} kW of solar surplus is available before automations. '
        f'Enabled actions are prioritized in order and will not increase grid import.</div>',
        unsafe_allow_html=True,
    )

    for row_start in range(0, len(PEAK_SOLAR_ACTIONS), 2):
        action_columns = st.columns(2, gap="medium")
        for action_index, (column, action) in enumerate(
            zip(action_columns, PEAK_SOLAR_ACTIONS[row_start : row_start + 2]),
            start=row_start + 1,
        ):
            result = solar_action_results[action["id"]]
            allocated_kw = result["allocated_kw"]
            covered_energy_kwh = allocated_kw
            savings_inr = covered_energy_kwh * ELECTRICITY_RATE_INR_PER_KWH
            avoided_co2_kg = covered_energy_kwh * GRID_CO2_KG_PER_KWH
            coverage_percent = round(result["coverage"] * 100)
            action_key = f"peak_solar_action_{action['id']}"

            with column:
                with st.container(border=True):
                    st.markdown(
                        f'<div class="solar-action-card">'
                        f'<div class="solar-action-priority">Priority {action_index}</div>'
                        f'<div class="solar-action-title">{action["icon"]} &nbsp; {action["title"]}</div>'
                        f'<p class="solar-action-copy">{action["description"]}</p>'
                        f'</div>',
                        unsafe_allow_html=True,
                    )
                    st.progress(
                        result["coverage"],
                        text=f"Solar capacity coverage · {coverage_percent}% "
                        f"({allocated_kw:.1f} / {action['load_kw']:.1f} kW)",
                    )
                    saving_col, co2_col = st.columns(2)
                    saving_col.metric("Estimated bill savings / h", f"₹{savings_inr:.2f}")
                    co2_col.metric("CO₂ avoided / h", f"{avoided_co2_kg:.2f} kg")
                    st.button(
                        "Disable Automation" if result["enabled"] else "Enable Automation",
                        key=f"toggle_{action_key}",
                        type="primary" if result["enabled"] else "secondary",
                        width="stretch",
                        on_click=lambda key=action_key: st.session_state.__setitem__(
                            key, not st.session_state[key]
                        ),
                    )
                    if result["enabled"] and allocated_kw == 0:
                        st.caption("Automation is queued until solar surplus is available.")
                    elif result["enabled"] and coverage_percent < 100:
                        st.caption("Partially powered by solar; waiting for more surplus to reach full capacity.")
                    elif result["enabled"]:
                        st.caption("Automation active · fully supplied by solar surplus.")

st.markdown(
    '<div class="section-heading">⚙️ &nbsp; Automated Appliance Schedule Engine</div>',
    unsafe_allow_html=True,
)
schedule_rows = []
for appliance in HEAVY_APPLIANCES:
    appliance_load_kw = APPLIANCE_LOADS_KW[appliance]
    if solar_available_kw > 2.0:
        solar_for_appliance_kw = min(appliance_load_kw, solar_surplus_kw)
        if solar_for_appliance_kw >= appliance_load_kw:
            suggested_runtime = "12:30 PM - 2:00 PM (100% Free Solar)"
        elif solar_for_appliance_kw > 0:
            suggested_runtime = "12:30 PM - 2:00 PM (Solar-first)"
        else:
            suggested_runtime = "12:30 PM - 2:00 PM (Grid-assisted)"
    else:
        suggested_runtime = "12:30 PM - 2:00 PM (Next solar window)"

    if (
        appliance in st.session_state.get("last_auto_scheduled_appliances", [])
        and active_appliances[appliance]
    ):
        action_status = "Auto-Scheduled"
    elif selected_time == "Evening Peak (6–9 PM)" and not active_appliances[appliance]:
        action_status = "Deferred to Avoid Grid Peak"
    else:
        action_status = "Standby"

    schedule_rows.append(
        {
            "Appliance Name": appliance,
            "Priority Level": APPLIANCE_PRIORITIES[appliance],
            "Auto-Suggested Run Time": suggested_runtime,
            "Action Status": action_status,
        }
    )
st.dataframe(schedule_rows, width="stretch", hide_index=True)

st.markdown('<div class="section-heading">〽️ &nbsp; Power flow</div>', unsafe_allow_html=True)
flow_scale_kw = max(SOLAR_CAPACITY_KW, household_load_kw, 0.1)
flow_rows = (
    ("Solar generation", solar_available_kw, "#83f3a6"),
    ("Home demand", household_load_kw, "#e8f3ed"),
    ("Grid import", grid_import_kw, "#ffbd70"),
    ("Solar export", solar_surplus_kw, "#76c9ff"),
)
flow_markup = "".join(
    f'<div class="flow-row"><div class="flow-label">{label}</div>'
    f'<div class="flow-track"><div class="flow-fill" style="width:{value / flow_scale_kw * 100:.1f}%;background:{color}"></div></div>'
    f'<div class="flow-value">{value:.1f} kW</div></div>'
    for label, value, color in flow_rows
)
st.markdown(
    f'<div class="flow-card"><div class="flow-head"><span>Household power balance</span>'
    f'<span>LIVE SIMULATED FLOW</span></div>{flow_markup}'
    f'<div class="flow-foot">Solar serves {solar_serving_load_kw:.1f} kW of demand · '
    f'{grid_import_kw:.1f} kW imported from grid · {solar_surplus_kw:.1f} kW potential export</div></div>',
    unsafe_allow_html=True,
)

st.markdown('<div class="section-heading">◎ &nbsp; What-if savings simulator</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="section-caption">Model a household efficiency action and compare its estimated monthly impact.</div>',
    unsafe_allow_html=True,
)
scenario_controls, roi_column = st.columns([1, 1.35], gap="large")
with scenario_controls:
    with st.container(border=True):
        st.markdown("### 🧪 &nbsp; Scenario setup")
        scenario = st.selectbox(
            "Efficiency action",
            ("Replace normal bulbs with LEDs", "Reduce AC usage"),
        )
        if scenario == "Replace normal bulbs with LEDs":
            bulb_count = st.slider("Bulbs replaced", min_value=1, max_value=20, value=5)
            daily_hours = st.slider("Hours used per day", min_value=1, max_value=12, value=5)
            # Assumes each 60 W incandescent bulb is replaced by a 9 W LED.
            monthly_scenario_kwh = bulb_count * (60 - 9) / 1000 * daily_hours * MONTH_DAYS
            scenario_detail = f"{bulb_count} bulbs · 51 W reduction each · {daily_hours} h/day"
        else:
            ac_hours_reduced = st.slider(
                "AC hours reduced per day", min_value=1, max_value=4, value=1
            )
            ac_power_kw = APPLIANCE_LOADS_KW["AC"]
            monthly_scenario_kwh = ac_power_kw * ac_hours_reduced * MONTH_DAYS
            scenario_detail = f"1.5 kW AC · {ac_hours_reduced} fewer h/day"

monthly_scenario_cost = monthly_scenario_kwh * ELECTRICITY_RATE_INR_PER_KWH
monthly_co2_avoided_kg = monthly_scenario_kwh * GRID_CO2_KG_PER_KWH

with roi_column:
    with st.container(border=True):
        st.markdown('<div class="roi-label">📈 &nbsp; Executive ROI summary · monthly</div>', unsafe_allow_html=True)
        roi_kwh, roi_inr, roi_co2 = st.columns(3)
        roi_kwh.metric("Energy saved", f"{monthly_scenario_kwh:,.1f} kWh")
        roi_inr.metric("Bill reduction", f"₹{monthly_scenario_cost:,.0f}")
        roi_co2.metric("CO₂ avoided", f"{monthly_co2_avoided_kg:,.1f} kg")
        st.markdown(
            f'<div class="roi-note">{scenario_detail}. Cost uses an illustrative flat tariff of '
            f'₹{ELECTRICITY_RATE_INR_PER_KWH:.2f}/kWh; CO₂ uses an assumed grid factor of '
            f'{GRID_CO2_KG_PER_KWH:.2f} kg/kWh.</div>',
            unsafe_allow_html=True,
        )

st.markdown('<div class="section-heading">🌿 &nbsp; Solar savings baseline</div>', unsafe_allow_html=True)
baseline_kwh, baseline_inr, baseline_note = st.columns([1, 1, 2])
baseline_kwh.metric("Monthly solar utilized", f"{estimated_monthly_solar_kwh:,.0f} kWh")
baseline_inr.metric("Estimated bill savings", f"₹{estimated_monthly_savings_inr:,.0f}")
with baseline_note:
    st.markdown(
        '<div class="flow-card" style="height:100%;color:#adbfb5">'
        '<div class="flow-head"><span>Projection assumptions</span></div>'
        '<div class="flow-foot" style="border:0;margin:0;padding:0;color:#b2c4ba">'
        '4.5 equivalent peak-sun hours/day · 72% self-consumption · 30-day month. '
        'Weather selection scales the monthly estimate; actual output varies by location and season.</div></div>',
        unsafe_allow_html=True,
    )

st.markdown("---")
st.caption(
    "EcoSmart is a software-only demo. All readings and financial or emissions values are illustrative estimates, not live meter data or a utility tariff quote."
)