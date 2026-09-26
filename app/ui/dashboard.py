import pandas as pd
import plotly.graph_objects as go
from app.core.city_memory import load_city_memory, save_crisis_snapshot, compare_city_memory, save_experiment, load_experiments

import streamlit as st
from app.core.simulation import run_simulation, explain_risk
from app.core.simulation import run_multi_crisis
from app.core.cascade import simulate_cascade, cascade_summary, build_crisis_replay
from app.visuals.cascade_view import build_cascade_figure
from app.core.what_if import run_what_if, autonomous_decision_engine
from app.core.experiment_engine import generate_crisis_experiments, summarize_experiments, analyze_intervention_synergy
from app.core.crisis_report import build_crisis_report
from app.core.city_health import calculate_city_health
from app.core.command_assistant import answer_command
from app.core.time_machine import simulate_risk_timeline, summarize_risk_timeline
from app.core.synthetic_city import generate_city, city_summary
from app.visuals.living_city import build_living_city_figure
from app.core.anomaly import detect_anomalies, summarize_anomalies
from app.core.robustness import run_robustness_analysis
from app.core.city_memory import save_experiment, load_experiments

st.set_page_config(
    page_title="CivicShield-X",
    page_icon="C",
    layout="wide",
)

st.markdown("""
<style>
:root { --cyan:#36d9ff; --text:#edf6ff; --muted:#8199b4; --line:rgba(112,178,230,.18); }
html, body, [data-testid="stAppViewContainer"] { background:radial-gradient(circle at 50% -10%, #102743 0%, #050b16 38%, #02050b 100%) !important; color:var(--text); }
[data-testid="stHeader"] { background:rgba(2,7,15,.72) !important; }
.block-container { max-width:1500px; padding-top:2rem; padding-bottom:4rem; }
.hero { position:relative; overflow:hidden; padding:32px 34px; border:1px solid rgba(54,217,255,.28); border-radius:24px; background:linear-gradient(135deg,rgba(12,31,55,.98),rgba(3,9,19,.98)); box-shadow:0 18px 55px rgba(0,0,0,.35),inset 0 0 35px rgba(54,217,255,.035); margin-bottom:28px; }
.hero-title { position:relative; z-index:1; font-size:46px; font-weight:950; letter-spacing:4px; color:#f6fbff; text-shadow:0 0 24px rgba(54,217,255,.16); }
.hero-sub { position:relative; z-index:1; color:#8ea8c3; font-size:15px; margin-top:7px; }
.section { font-size:20px; font-weight:900; letter-spacing:1.4px; color:#e5f2ff; margin-top:24px; margin-bottom:15px; padding-left:12px; border-left:3px solid var(--cyan); }
.city-card,.sensor-card { transition:transform .18s ease,border-color .18s ease,box-shadow .18s ease; }
.city-card { border:1px solid var(--line); border-radius:18px; padding:19px; background:linear-gradient(145deg,rgba(11,27,47,.96),rgba(4,11,23,.97)); min-height:125px; margin-bottom:14px; box-shadow:0 10px 30px rgba(0,0,0,.18); }
.city-card:hover,.sensor-card:hover { transform:translateY(-2px); border-color:rgba(54,217,255,.34); box-shadow:0 12px 35px rgba(0,0,0,.28),0 0 22px rgba(54,217,255,.055); }
.city-name { color:#f4f9ff; font-size:15px; font-weight:850; }
.city-type { color:#7189a5; font-size:12px; margin-top:5px; letter-spacing:.5px; text-transform:uppercase; }
.status { display:inline-block; margin-top:13px; padding:6px 12px; border-radius:999px; font-size:10px; font-weight:950; letter-spacing:1.1px; }
.sensor-card { border:1px solid rgba(100,160,220,.17); border-radius:16px; padding:16px; background:linear-gradient(145deg,rgba(8,20,38,.94),rgba(4,10,20,.94)); min-height:86px; }
.sensor-name { color:#829bb5; font-size:11px; text-transform:uppercase; letter-spacing:.8px; }
.sensor-value { color:#f2f8ff; font-size:25px; font-weight:900; margin-top:6px; }
[data-testid="stMetric"] { background:linear-gradient(145deg,rgba(9,24,43,.9),rgba(4,11,22,.92)); border:1px solid rgba(112,178,230,.18); padding:14px; border-radius:16px; box-shadow:0 8px 24px rgba(0,0,0,.16); }
[data-testid="stMetricValue"] { color:#f2f7ff !important; font-weight:900 !important; }
[data-testid="stSidebar"] { background:linear-gradient(180deg,#040b15,#02060d) !important; border-right:1px solid rgba(112,178,230,.12); }
[data-testid="stButton"] button { border:1px solid rgba(54,217,255,.24); border-radius:10px; background:linear-gradient(135deg,rgba(11,34,56,.96),rgba(5,15,27,.96)); color:#eaf8ff; font-weight:750; }
[data-testid="stButton"] button:hover { border-color:rgba(54,217,255,.62); box-shadow:0 0 20px rgba(54,217,255,.10); color:#fff; }
div[data-testid="stExpander"] { border:1px solid rgba(112,178,230,.15); border-radius:14px; background:rgba(5,14,27,.55); }
</style>
""", unsafe_allow_html=True)

st.sidebar.header("Crisis Control")

crisis = st.sidebar.selectbox(
    "Select crisis scenario",
    ["normal", "flood", "power_failure", "fire"],
    index=1,
)

simulation = run_simulation(crisis)

risk_score = simulation["risk_score"]
risk_level = simulation["risk_level"]
sensors = simulation["sensors"]
nodes = simulation["city_nodes"]

cascade = simulate_cascade(risk_score, crisis)
summary = cascade_summary(cascade)
synthetic_city = generate_city(42)
synthetic_city_summary = city_summary(synthetic_city)
living_city_figure = build_living_city_figure(synthetic_city, cascade)
city_health = calculate_city_health(
    simulation["sensors"],
    summary,
    risk_score,
)



st.markdown("""
<div class="hero">
    <div class="hero-title">CIVICSHIELD-X</div>
    <div class="hero-sub">
        AI Autonomous Urban Crisis Digital Twin & Response Intelligence Platform
    </div>
</div>
""", unsafe_allow_html=True)

st.markdown(
    '<div class="section">CITY SITUATION</div>',
    unsafe_allow_html=True
)

c1, c2, c3, c4 = st.columns(4)

c1.metric("City Risk", f"{risk_score}/100")
c2.metric("Risk Level", risk_level)
c3.metric("Affected Nodes", summary["affected_nodes"])
c4.metric("Population Risk", f"{summary['population_risk']:.1f}")

st.divider()

st.markdown(
    '<div class="section">SYNTHETIC CITY DIGITAL TWIN</div>',
    unsafe_allow_html=True,
)

ct1, ct2, ct3, ct4 = st.columns(4)

with ct1:
    st.metric("DISTRICTS", synthetic_city_summary["districts"])

with ct2:
    st.metric(
        "POPULATION",
        f"{synthetic_city_summary['population']:,}",
    )

with ct3:
    st.metric(
        "INFRASTRUCTURE",
        synthetic_city_summary["infrastructure"],
    )

with ct4:
    st.metric(
        "DEPENDENCIES",
        synthetic_city_summary["dependencies"],
    )

st.caption(
    f"Generated city model: {synthetic_city_summary['city_id']} | "
    f"Deterministic seed: {synthetic_city['seed']}"
)

st.markdown(
    '<div class="section">LIVING CITY 2.0</div>',
    unsafe_allow_html=True,
)

st.caption(
    "Interactive synthetic city digital twin showing districts, "
    "infrastructure and modeled dependency propagation."
)

st.plotly_chart(
    living_city_figure,
    width='stretch',
    config={"displayModeBar": False},
)

st.markdown('<div class="section">CITY HEALTH</div>', unsafe_allow_html=True)

ch1, ch2, ch3, ch4 = st.columns(4)

with ch1:
    st.metric("CITY HEALTH", f"{city_health['health_score']:.1f}/100")

with ch2:
    st.metric("CITY STATE", city_health["state"])

with ch3:
    st.metric("RISK PRESSURE", f"{city_health['risk_pressure']:.1f}")

with ch4:
    st.metric("CASCADE PRESSURE", f"{city_health['cascade_pressure']:.1f}")

st.caption(
    "City Health combines modeled risk, anomaly pressure, and cascade impact. "
    "It is a synthetic digital-twin health indicator, not a real-world city metric."
)

st.markdown(
    '<div class="section">ANOMALY DETECTION ENGINE</div>',
    unsafe_allow_html=True
)

anomaly_df = detect_anomalies(sensors)
anomaly_summary = summarize_anomalies(anomaly_df)

an1, an2, an3, an4 = st.columns(4)

with an1:
    st.metric("SENSORS ANALYZED", anomaly_summary["total_sensors"])

with an2:
    st.metric("ANOMALIES DETECTED", anomaly_summary["anomalies"])

with an3:
    st.metric("CRITICAL", anomaly_summary["critical"])

with an4:
    st.metric("WARNINGS", anomaly_summary["warnings"])

active_anomalies = anomaly_df[anomaly_df["anomaly"] == True].copy()

if not active_anomalies.empty:
    st.dataframe(
        active_anomalies[
            ["sensor", "value", "threshold", "deviation", "direction", "severity"]
        ],
        width='stretch',
        hide_index=True,
    )
else:
    st.success("No modeled sensor anomalies detected.")

st.caption(
    "Anomalies are detected using CivicShield-X modeled sensor thresholds; "
    "they are synthetic prototype signals, not real-world alerts."
)

st.markdown(
    '<div class="section">MULTI-SENSOR INTELLIGENCE</div>',
    unsafe_allow_html=True
)

sensor_labels = {
    "rainfall_mm": ("Rainfall", "mm"),
    "river_level_pct": ("River Level", "%"),
    "traffic_pct": ("Traffic", "%"),
    "power_load_pct": ("Power Load", "%"),
    "water_pressure_pct": ("Water Pressure", "%"),
    "hospital_load_pct": ("Hospital Load", "%"),
}

sensor_cols = st.columns(6)

for col, (_, row) in zip(sensor_cols, sensors.iterrows()):

    key = str(row["sensor"])
    value = float(row["value"])

    label, unit = sensor_labels.get(
        key,
        (key, "")
    )

    col.markdown(f"""
    <div class="sensor-card">
        <div class="sensor-name">{label}</div>
        <div class="sensor-value">{value:.1f}{unit}</div>
    </div>
    """, unsafe_allow_html=True)

st.divider()

st.markdown(
    '<div class="section">FUTURE RISK HORIZON</div>',
    unsafe_allow_html=True
)

base_risk = float(risk_score)
horizon = [
    ("15 MIN", min(100, round(base_risk + 8, 1))),
    ("30 MIN", min(100, round(base_risk + 16, 1))),
    ("60 MIN", min(100, round(base_risk + 24, 1))),
]

hc1, hc2, hc3 = st.columns(3)

for col, (label, projected) in zip((hc1, hc2, hc3), horizon):
    if projected >= 75:
        future_level = "CRITICAL"
        future_color = "#ff1744"
    elif projected >= 50:
        future_level = "HIGH"
        future_color = "#ff9100"
    elif projected >= 25:
        future_level = "MODERATE"
        future_color = "#ffd600"
    else:
        future_level = "LOW"
        future_color = "#00e676"

    with col:
        st.markdown(
            f"""
            <div class="city-card">
                <div class="city-type">{label} FORECAST</div>
                <div class="city-name">
                    <span style="color:{future_color};font-size:28px;">{projected:.0f}</span>
                    <span style="font-size:14px;"> / 100 RISK</span>
                </div>
                <div class="status"
                     style="color:{future_color};
                            background:rgba(255,255,255,.04);
                            border:1px solid {future_color};">
                    {future_level}
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

st.markdown(
    '<div class="section">AI SITUATION ROOM</div>',
    unsafe_allow_html=True
)

primary_threat = "Flood propagation through water and transport infrastructure"
_risk_explanations = explain_risk(simulation["sensors"])
risk_drivers = []
for item in _risk_explanations[:3]:
    if item["active"]:
        driver_color = "#ff1744" if item["contribution"] >= 25 else "#ff9100"
    else:
        driver_color = "#00e676"
    risk_drivers.append(
        (
            item["driver"],
            f"{item['value']:.1f}",
            driver_color,
            item["contribution"],
            item["reason"],
        )
    )

sc1, sc2 = st.columns([1.25, 1])

with sc1:
    st.markdown(
        f"""
        <div class="city-card">
            <div class="city-type">PRIMARY THREAT</div>
            <div class="city-name">⚠ {primary_threat}</div>
            <div class="city-type">
                The current cascade indicates rising pressure on water,
                bridge, road and emergency-response dependencies.
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

with sc2:
    st.markdown(
        '<div class="city-card"><div class="city-type">TOP RISK DRIVERS</div>',
        unsafe_allow_html=True
    )

    _driver_explanations = {
        "River level": "Drives overflow pressure and increases water-system stress.",
        "Rainfall": "Adds inflow pressure and increases the probability of flood escalation.",
        "Traffic stress": "Raises emergency-response delay across transport dependencies.",
    }

    for name, value, color, contribution, explanation in risk_drivers:
        try:
            _bar_value = min(100.0, max(0.0, float(value)))
        except ValueError:
            _bar_value = 0.0

        st.markdown(
            f"""
            <div style="margin:12px 0 16px 0;">
                <div style="display:flex;justify-content:space-between;align-items:center;">
                    <span>{name}</span>
                    <strong style="color:{color};">{value}</strong>
                </div>
                <div style="height:6px;margin-top:6px;background:rgba(255,255,255,.08);border-radius:6px;overflow:hidden;">
                    <div style="height:6px;width:{_bar_value:.1f}%;background:{color};border-radius:6px;box-shadow:0 0 10px {color};"></div>
                </div>
                <div style="font-size:.76rem;color:rgba(255,255,255,.58);margin-top:5px;">
                    {explanation} | risk contribution {contribution} points
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

    st.markdown(
        '<div style="font-size:.72rem;color:rgba(255,255,255,.45);margin-top:8px;">EXPLAINABILITY • Bars represent normalized sensor pressure; explanations describe CivicShield-X model logic.</div>',
        unsafe_allow_html=True
    )
    st.markdown("</div>", unsafe_allow_html=True)

st.markdown('<div class="section">CRISIS INTELLIGENCE REPORT</div>', unsafe_allow_html=True)

crisis_report = build_crisis_report(
    simulation,
    cascade,
    summary,
    explain_risk(simulation["sensors"]),
)

st.download_button(
    "Download Crisis Report",
    data=crisis_report,
    file_name=f"civicshield_{crisis.lower()}_crisis_report.md",
    mime="text/markdown",
    width='stretch',
)

st.markdown(
    '<div class="section">RECOMMENDED RESPONSE</div>',
    unsafe_allow_html=True
)

r1, r2, r3 = st.columns(3)

recommendations = [
    ("01", "Protect Riverside Zone", "Prepare evacuation and emergency-access routes."),
    ("02", "Monitor River Bridge", "Track bridge stress and restrict access if thresholds rise."),
    ("03", "Protect Emergency Response", "Prioritize ambulance and fire-station routing."),
]

for col, (num, title, text) in zip((r1, r2, r3), recommendations):
    with col:
        st.markdown(
            f"""
            <div class="city-card">
                <div class="city-type">ACTION {num}</div>
                <div class="city-name">{title}</div>
                <div class="city-type">{text}</div>
            </div>
            """,
            unsafe_allow_html=True
        )

st.markdown(
    '<div class="section">AI COMMAND ASSISTANT</div>',
    unsafe_allow_html=True,
)

st.caption(
    "Ask CivicShield-X about risk, anomalies, cascade propagation, "
    "city health, scenarios, or modeled response actions."
)

command_input = st.text_input(
    "Command",
    placeholder="Example: Why is the city at high risk?",
    key="civicshield_command",
)

if command_input:
    command_result = answer_command(
        command_input,
        simulation,
        summary,
        anomaly_summary,
    )

    st.markdown(f"**{command_result['title']}**")
    st.info(command_result["response"])

    st.caption(
        f"Intent detected: {command_result['intent']} | "
        "Response generated from CivicShield-X modeled system state."
    )

st.markdown(
    '<div class="section">WHAT-IF CRISIS LAB</div>',
    unsafe_allow_html=True
)

st.caption("Change conditions and observe how the crisis model responds.")

wf1, wf2, wf3, wf4 = st.columns(4)

with wf1:
    wf_rainfall = st.slider("Rainfall (mm)", 0, 150, 94, 1)

with wf2:
    wf_river = st.slider("River Level (%)", 0, 100, 81, 1)

with wf3:
    wf_delay = st.slider("Response Delay (min)", 0, 30, 5, 1)

with wf4:
    wf_bridge = st.checkbox("Bridge Available", value=True)

what_if = run_what_if(
    simulation,
    wf_rainfall,
    wf_river,
    wf_delay,
    wf_bridge
)

wc1, wc2, wc3 = st.columns(3)

wc1.metric(
    "Scenario Risk",
    f"{what_if['risk_score']}/100",
    delta=f"{what_if['risk_score'] - risk_score:+.1f}"
)

wc2.metric(
    "Scenario Level",
    what_if["risk_level"]
)

risk_change = what_if["risk_score"] - risk_score

if risk_change < 0:
    interpretation = "Risk decreases under this scenario."
elif risk_change > 0:
    interpretation = "Risk increases under this scenario."
else:
    interpretation = "Risk remains unchanged."

wc3.metric("Risk Change", f"{risk_change:+.1f}")

st.markdown(
    f"""
    <div class="city-card">
        <div class="city-type">SCENARIO INTERPRETATION</div>
        <div class="city-name">{interpretation}</div>
        <div class="city-type">
            Rainfall: {wf_rainfall} mm &nbsp;|&nbsp;
            River: {wf_river}% &nbsp;|&nbsp;
            Response delay: {wf_delay} min &nbsp;|&nbsp;
            Bridge: {"AVAILABLE" if wf_bridge else "UNAVAILABLE"}
        </div>
    </div>
    """,
    unsafe_allow_html=True
)

st.markdown(
    '<div class="section">RESPONSE PLAN BATTLE</div>',
    unsafe_allow_html=True
)

st.caption("Compare modeled response strategies using the current crisis state.")

plan_defs = [
    (
        "PLAN A",
        "Rapid Evacuation",
        -8,
        2,
        True,
        "Protects the Riverside zone by reducing modeled river pressure and response delay."
    ),
    (
        "PLAN B",
        "Emergency Routing",
        0,
        0,
        True,
        "Reduces modeled emergency response delay while keeping the bridge available."
    ),
    (
        "PLAN C",
        "Infrastructure Isolation",
        0,
        5,
        False,
        "Tests the counterfactual effect of isolating an unsafe bridge from the network."
    ),
]

plan_cols = st.columns(3)

for col, (plan_id, plan_name, river_adjustment, response_delay, bridge_available, description) in zip(plan_cols, plan_defs):
    plan_scenario = run_what_if(
        simulation,
        float(sensors.loc[sensors["sensor"] == "rainfall_mm", "value"].iloc[0]),
        float(sensors.loc[sensors["sensor"] == "river_level_pct", "value"].iloc[0]) + river_adjustment,
        response_delay,
        bridge_available,
    )

    modeled_risk = float(plan_scenario["risk_score"])
    plan_level = plan_scenario["risk_level"]
    risk_change = round(modeled_risk - float(risk_score), 1)

    plan_cascade = simulate_cascade(
        modeled_risk,
        crisis
    )
    plan_summary = cascade_summary(plan_cascade)

    affected_est = int(plan_summary["affected_nodes"])
    population_est = round(float(plan_summary["population_risk"]), 2)
    maximum_impact = round(float(plan_summary["maximum_impact"]), 2)
    average_impact = round(float(plan_summary["average_impact"]), 2)

    recovery_est = max(
        10,
        round(
            30
            + average_impact * 0.35
            + affected_est * 2
        )
    )

    if modeled_risk >= 75:
        plan_color = "#ff1744"
    elif modeled_risk >= 50:
        plan_color = "#ff9100"
    elif modeled_risk >= 25:
        plan_color = "#ffd600"
    else:
        plan_color = "#00e676"

    with col:
        st.markdown(
            f"""
            <div class="city-card">
                <div class="city-type">{plan_id}</div>
                <div class="city-name">{plan_name}</div>
                <div class="status"
                     style="color:{plan_color};
                            background:rgba(255,255,255,.04);
                            border:1px solid {plan_color};">
                    MODELED RISK {modeled_risk:.1f}/100 • {plan_level}
                </div>
                <div class="city-type">
                    {description}
                </div>
                <hr style="border-color:rgba(255,255,255,.10);">
                <div class="city-type">
                    Risk change: <b>{risk_change:+.1f}</b><br>
                    Cascade nodes: <b>{affected_est}</b><br>
                    Population risk: <b>{population_est}%</b><br>
                    Maximum impact: <b>{maximum_impact}</b><br>
                    Average impact: <b>{average_impact}</b><br>
                    Estimated recovery: <b>{recovery_est} min</b>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )


st.caption(
    "Plan metrics are modeled estimates from CivicShield-X rules, not real-world emergency forecasts."
)

st.markdown(
    '<div class="section">MULTI-CRISIS FUSION</div>',
    unsafe_allow_html=True
)

st.caption("Model simultaneous urban disruptions and observe their combined system-level effect.")

crisis_options = ["flood", "power_failure", "fire"]

selected_crises = st.multiselect(
    "Active crises",
    crisis_options,
    default=["flood"],
    format_func=lambda x: x.replace("_", " ").upper(),
    key="multi_crisis_selector"
)

if selected_crises:
    multi_result = run_multi_crisis(
        crises=selected_crises,
        seed=42
    )

    multi_risk = multi_result["risk_score"]
    multi_level = multi_result["risk_level"]

    if multi_level == "CRITICAL":
        multi_color = "#ff1744"
    elif multi_level == "HIGH":
        multi_color = "#ff9100"
    elif multi_level == "MODERATE":
        multi_color = "#ffd600"
    else:
        multi_color = "#00e676"

    mc1, mc2, mc3 = st.columns(3)

    with mc1:
        st.metric("Combined Risk", f"{multi_risk}/100")

    with mc2:
        st.metric("Risk Level", multi_level)

    with mc3:
        st.metric("Active Crises", len(selected_crises))

    st.markdown(
        f"""
        <div class="city-card">
            <div class="city-type">CRISIS FUSION STATE</div>
            <div class="city-name">
                <span style="color:{multi_color};">●</span>
                {" + ".join(c.upper() for c in selected_crises)}
            </div>
            <div class="city-type">
                Combined modeled risk: {multi_risk}/100
                &nbsp;•&nbsp;
                System state: {multi_level}
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    fusion_df = multi_result["sensors"].copy()

    st.dataframe(
        fusion_df,
        width='stretch',
        hide_index=True
    )

else:
    st.info("Select at least one crisis to activate the fusion model.")

st.markdown(
    '<div class="section">CRISIS TIME MACHINE</div>',
    unsafe_allow_html=True,
)

timeline = simulate_risk_timeline(simulation)
timeline_summary = summarize_risk_timeline(timeline)

tm1, tm2, tm3 = st.columns(3)

with tm1:
    st.metric(
        "INITIAL RISK",
        f"{timeline_summary['initial_risk']:.1f}/100",
    )

with tm2:
    st.metric(
        "PEAK MODELED RISK",
        f"{timeline_summary['peak_risk']:.1f}/100",
    )

with tm3:
    st.metric(
        "PEAK AT",
        f"{timeline_summary['peak_delay']} MIN",
    )

timeline_df = pd.DataFrame(timeline)

st.line_chart(
    timeline_df,
    x="delay_min",
    y="risk_score",
    width='stretch',
)

st.dataframe(
    timeline_df[
        ["delay_min", "risk_score", "risk_level", "rainfall", "river_level"]
    ],
    width='stretch',
    hide_index=True,
)

st.caption(
    "The Time Machine generates modeled counterfactual trajectories "
    "from the current synthetic crisis state. It is not a real-world forecast."
)


st.markdown(
    f"""
    <div class="city-card">
        <div class="city-type">TIMELINE ANALYSIS</div>
        <div class="city-name">
            Longer response delay increases the modeled crisis trajectory.
        </div>
        <div class="city-type">
            Baseline risk: {risk_score}/100 &nbsp;•&nbsp;
            Current cascade nodes: {summary["affected_nodes"]} &nbsp;•&nbsp;
            Population risk: {summary["population_risk"]:.1f}
        </div>
    </div>
    """,
    unsafe_allow_html=True
)

st.markdown(
    '<div class="section">INFRASTRUCTURE DEPENDENCY EXPLORER</div>',
    unsafe_allow_html=True
)

st.caption("Trace how failure in one infrastructure system can propagate through connected city services.")

dependency_map = {
    "WATER-01": [
        ("BRIDGE-01", "River overflow", 85),
        ("HOSP-01", "Water dependency", 55),
    ],
    "BRIDGE-01": [
        ("ROAD-01", "Bridge stress", 90),
    ],
    "ROAD-01": [
        ("FIRE-01", "Emergency response delay", 75),
        ("HOSP-01", "Ambulance delay", 80),
        ("RES-01", "Mobility disruption", 65),
    ],
    "POWER-01": [
        ("HOSP-01", "Power dependency", 70),
    ],
    "FIRE-01": [],
    "HOSP-01": [],
    "RES-01": [],
}

node_names = {
    row["id"]: row["name"]
    for _, row in simulation["city_nodes"].iterrows()
}

selected_node = st.selectbox(
    "Select infrastructure",
    list(node_names.keys()),
    index=list(node_names.keys()).index("WATER-01"),
    format_func=lambda x: f"{node_names.get(x, x)} ({x})",
    key="dependency_node"
)

dependencies = dependency_map.get(selected_node, [])

if dependencies:
    dep_cols = st.columns(min(3, len(dependencies)))

    for col, (target, cause, strength) in zip(dep_cols, dependencies):
        if strength >= 80:
            dep_status = "HIGH DEPENDENCY"
            dep_color = "#ff1744"
        elif strength >= 65:
            dep_status = "MODERATE DEPENDENCY"
            dep_color = "#ff9100"
        else:
            dep_status = "LOWER DEPENDENCY"
            dep_color = "#ffd600"

        with col:
            st.markdown(
                f"""
                <div class="city-card">
                    <div class="city-type">DEPENDENCY TARGET</div>
                    <div class="city-name">{node_names.get(target, target)}</div>
                    <div class="city-type">{target}</div>
                    <div class="status"
                         style="color:{dep_color};
                                background:rgba(255,255,255,.04);
                                border:1px solid {dep_color};">
                        {dep_status}
                    </div>
                    <div class="city-type">
                        {cause}<br>
                        Dependency strength: {strength}%
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )
else:
    st.info("No downstream dependencies are currently modeled for this infrastructure node.")

st.markdown(
    f"""
    <div class="city-card">
        <div class="city-type">DEPENDENCY ANALYSIS</div>
        <div class="city-name">
            {node_names.get(selected_node, selected_node)}
        </div>
        <div class="city-type">
            Direct downstream systems: {len(dependencies)}
            &nbsp;•&nbsp;
            Dependency paths are based on the CivicShield-X infrastructure model.
        </div>
    </div>
    """,
    unsafe_allow_html=True
)

st.markdown(
    '<div class="section">AUTONOMOUS RESPONSE LOOP</div>',
    unsafe_allow_html=True
)

st.caption("Evaluate → Simulate → Verify → Select")

decision_result = autonomous_decision_engine(simulation)
decision = decision_result["decision"]
evaluations = decision_result["evaluations"]

dc1, dc2, dc3 = st.columns(3)

with dc1:
    st.metric("Baseline Risk", f"{decision_result['baseline_risk']:.1f}/100")

with dc2:
    st.metric(
        "Verified Reduction",
        f"{decision_result['verification']['risk_reduced']:.1f}"
    )

with dc3:
    st.metric(
        "Verification",
        decision_result["verification"]["status"]
    )

st.markdown(
    f"""
    <div class="city-card">
        <div class="city-type">SELECTED RESPONSE</div>
        <div class="city-name">{decision["action"]}</div>
        <div class="city-type">
            Modeled risk after action:
            <strong>{decision["simulated_risk"]:.1f}/100</strong>
            &nbsp;•&nbsp;
            Risk reduction:
            <strong>{decision["risk_reduction"]:.1f}</strong>
        </div>
    </div>
    """,
    unsafe_allow_html=True
)

st.markdown(
    '<div class="city-type">RESPONSE CANDIDATES</div>',
    unsafe_allow_html=True
)

for item in evaluations:
    if item["verified"]:
        status_text = "VERIFIED EFFECT"
        status_color = "#00e676"
    else:
        status_text = "NO VERIFIED REDUCTION"
        status_color = "#ff9100"

    st.markdown(
        f"""
        <div class="city-card">
            <div class="city-name">{item["action"]}</div>
            <div class="city-type">
                Baseline: {item["baseline_risk"]:.1f}
                &nbsp;→&nbsp;
                Simulated: {item["simulated_risk"]:.1f}
                &nbsp;•&nbsp;
                Reduction: {item["risk_reduction"]:.1f}
            </div>
            <div class="status"
                 style="color:{status_color};
                        background:rgba(255,255,255,.04);
                        border:1px solid {status_color};">
                {status_text}
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

st.caption(
    "Decision outputs are modeled simulations for the CivicShield-X prototype; "
    "they are not real-world emergency forecasts."
)

st.markdown(
    '<div class="section">CRISIS REPLAY TIMELINE</div>',
    unsafe_allow_html=True
)

replay_events = build_crisis_replay(cascade, risk_score)

if replay_events:
    replay_index = st.slider(
        "Replay crisis progression",
        min_value=0,
        max_value=len(replay_events) - 1,
        value=0,
        step=1,
        key="crisis_replay_slider"
    )

    current_event = replay_events[replay_index]

    if current_event["status"] in ("CRITICAL", "PEAK"):
        replay_color = "#ff1744"
    elif current_event["status"] in ("STRESSED", "DEGRADED", "AT RISK"):
        replay_color = "#ff9100"
    else:
        replay_color = "#00e676"

    rc1, rc2, rc3 = st.columns(3)

    with rc1:
        st.metric("Timeline", current_event["time"])

    with rc2:
        st.metric("Stage", current_event["stage"])

    with rc3:
        st.metric("Impact", f"{current_event['impact']:.1f}")

    st.markdown(
        f"""
        <div class="city-card">
            <div class="city-type">REPLAY EVENT</div>
            <div class="city-name">
                <span style="color:{replay_color};">●</span>
                {current_event["event"]}
            </div>
            <div class="city-type">
                Infrastructure: {current_event["node"]}
                &nbsp;•&nbsp;
                Status: {current_event["status"]}
                &nbsp;•&nbsp;
                Modeled impact: {current_event["impact"]:.1f}
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="city-type">FULL INCIDENT TIMELINE</div>',
        unsafe_allow_html=True
    )

    replay_table = pd.DataFrame(replay_events)

    st.dataframe(
        replay_table,
        width='stretch',
        hide_index=True
    )

    st.caption(
        "Replay reconstructs the modeled cascade sequence; "
        "it is not a historical real-world incident record."
    )
else:
    st.info("No replay events are available for the current crisis.")


# ============================================================
# CRISIS EXPERIMENT LAB
# ============================================================

st.markdown(
    '<div class="section">CRISIS EXPERIMENT LAB</div>',
    unsafe_allow_html=True
)

st.caption(
    "Run controlled crisis experiments, verify the modeled outcome, "
    "and store the scenario in City Memory."
)

el1, el2 = st.columns(2)

with el1:
    exp_name = st.text_input(
        "Experiment name",
        value="Flood Response Experiment",
        key="experiment_name"
    )

    exp_rainfall = st.slider(
        "Rainfall intensity (mm)",
        min_value=0,
        max_value=150,
        value=94,
        step=1,
        key="experiment_rainfall"
    )

    exp_river = st.slider(
        "River level (%)",
        min_value=0,
        max_value=100,
        value=81,
        step=1,
        key="experiment_river"
    )

with el2:
    exp_delay = st.slider(
        "Response delay (minutes)",
        min_value=0,
        max_value=30,
        value=5,
        step=1,
        key="experiment_delay"
    )

    exp_bridge = st.checkbox(
        "River bridge available",
        value=True,
        key="experiment_bridge"
    )

    run_experiment = st.button(
        "RUN CRISIS EXPERIMENT",
        width='stretch',
        key="run_crisis_experiment"
    )

if run_experiment:
    experiment_result = run_what_if(
        simulation,
        exp_rainfall,
        exp_river,
        exp_delay,
        exp_bridge
    )

    experiment_risk = float(experiment_result["risk_score"])
    experiment_level = experiment_result["risk_level"]
    risk_delta = round(experiment_risk - float(risk_score), 1)

    if experiment_level == "CRITICAL":
        experiment_color = "#ff1744"
    elif experiment_level == "HIGH":
        experiment_color = "#ff9100"
    elif experiment_level == "MODERATE":
        experiment_color = "#ffd600"
    else:
        experiment_color = "#00e676"

    if risk_delta < 0:
        delta_text = f"RISK REDUCED BY {abs(risk_delta):.1f}"
        delta_color = "#00e676"
    elif risk_delta > 0:
        delta_text = f"RISK INCREASED BY {risk_delta:.1f}"
        delta_color = "#ff1744"
    else:
        delta_text = "NO RISK CHANGE"
        delta_color = "#ffd600"

    st.markdown(
        f"""
        <div class="city-card" style="
            border:1px solid {experiment_color};
            box-shadow:0 0 24px rgba(255,255,255,.04);
        ">
            <div class="city-type">EXPERIMENT RESULT</div>
            <div class="city-name">
                <span style="color:{experiment_color};">●</span>
                {experiment_level}
            </div>
            <div class="city-type">
                Modeled risk:
                <strong>{experiment_risk:.1f}</strong>
                &nbsp;•&nbsp;
                Baseline:
                <strong>{float(risk_score):.1f}</strong>
            </div>
            <div class="status"
                 style="color:{delta_color};
                        background:rgba(255,255,255,.04);
                        border:1px solid {delta_color};">
                {delta_text}
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    saved = save_experiment(
        name=exp_name,
        rainfall=exp_rainfall,
        river_level=exp_river,
        response_delay=exp_delay,
        bridge_available=exp_bridge,
        risk_score=experiment_risk,
        risk_level=experiment_level,
    )

    st.success(
        f"Experiment {saved['id']} saved to City Memory."
    )

experiments = load_experiments()

if experiments:
    st.markdown(
        '<div class="city-type">EXPERIMENT MEMORY</div>',
        unsafe_allow_html=True
    )

    experiment_table = pd.DataFrame(experiments)

    st.dataframe(
        experiment_table[
            [
                "id",
                "name",
                "rainfall",
                "river_level",
                "response_delay",
                "bridge_available",
                "risk_score",
                "risk_level",
            ]
        ],
        width='stretch',
        hide_index=True,
    )

    st.caption(
        "Stored experiments are modeled scenarios generated by "
        "the CivicShield-X simulation engine."
    )
else:
    st.info(
        "No experiments stored yet. Run a scenario to create the "
        "first City Memory experiment."
    )


st.markdown(
    '<div class="section">CRISIS PROPAGATION NETWORK</div>',
    unsafe_allow_html=True
)

fig = build_cascade_figure(cascade)

st.plotly_chart(
    fig,
    width="stretch"
)

st.markdown(
    '<div class="section">CASCADE INTELLIGENCE</div>',
    unsafe_allow_html=True
)

st.dataframe(
    cascade[
        ["stage", "node", "name", "cause", "impact", "status"]
    ],
    width="stretch",
    hide_index=True,
)

st.caption(
    "CivicShield-X simulation engine | "
    "Current risk and cascade outputs are simulated/rule-based."
)





# --- CIVICSHIELD_EXPERIMENT_MATRIX ---
st.markdown("## CRISIS EXPERIMENT MATRIX")
st.caption(
    "Evidence-driven intervention experimentation using the CivicShield-X "
    "simulation engine. Results are modeled scenarios, not real-world forecasts."
)

experiment_results = generate_crisis_experiments(
    simulation,
    include_combinations=True,
)

experiment_summary = summarize_experiments(experiment_results)
synergy_results = analyze_intervention_synergy(experiment_results)

m1, m2, m3, m4 = st.columns(4)

with m1:
    st.metric("EXPERIMENTS", experiment_summary["count"])

with m2:
    st.metric("VERIFIED EFFECTS", experiment_summary["verified_count"])

with m3:
    st.metric(
        "MAX RISK REDUCTION",
        f"{experiment_summary['best_reduction']:.1f}",
    )

with m4:
    st.metric(
        "BEST MODELED ACTION",
        experiment_summary["best_experiment"],
    )

experiment_df = pd.DataFrame(experiment_results)

st.dataframe(
    experiment_df[
        [
            "experiment",
            "simulated_risk",
            "risk_reduction",
            "risk_level",
            "verified_reduction",
        ]
    ].rename(
        columns={
            "experiment": "Intervention",
            "simulated_risk": "Modeled Risk",
            "risk_reduction": "Risk Reduction",
            "risk_level": "Risk Level",
            "verified_reduction": "Verified Effect",
        }
    ),
    width='stretch',
    hide_index=True,
)

if synergy_results:
    st.markdown("### INTERVENTION SYNERGY")

    synergy_df = pd.DataFrame(synergy_results)

    st.dataframe(
        synergy_df[
            [
                "combination",
                "expected_reduction",
                "actual_reduction",
                "synergy",
                "classification",
            ]
        ].rename(
            columns={
                "combination": "Combination",
                "expected_reduction": "Expected Reduction",
                "actual_reduction": "Actual Reduction",
                "synergy": "Synergy",
                "classification": "Modeled Interaction",
            }
        ),
        width='stretch',
        hide_index=True,
    )

    fig_experiment = go.Figure()

    fig_experiment.add_trace(
        go.Bar(
            name="Modeled Risk",
            x=experiment_df["experiment"],
            y=experiment_df["simulated_risk"],
        )
    )

    fig_experiment.add_trace(
        go.Bar(
            name="Risk Reduction",
            x=experiment_df["experiment"],
            y=experiment_df["risk_reduction"],
        )
    )

    fig_experiment.update_layout(
        title="Intervention Experiment Surface",
        barmode="group",
        template="plotly_dark",
        height=430,
        margin=dict(l=20, r=20, t=55, b=120),
        xaxis=dict(tickangle=-35),
        yaxis_title="Modeled Risk / Reduction",
        legend_title="Experiment Signal",
    )

    st.plotly_chart(
        fig_experiment,
        width='stretch',
        key="civicshield_experiment_matrix",
    )

st.caption(
    "CivicShield-X evaluates interventions through its modeled "
    "counterfactual engine. 'Verified' means the modeled scenario "
    "produced a measurable reduction relative to the simulation baseline."
)


# --- CIVICSHIELD_DECISION_ROBUSTNESS ---
st.markdown("## DECISION ROBUSTNESS LAB")
st.caption(
    "Stress-test response interventions across varied modeled conditions. "
    "Robustness describes stability inside the CivicShield-X simulation space, "
    "not real-world emergency effectiveness."
)

robustness_analysis = run_robustness_analysis(simulation)
robustness_summary = robustness_analysis["summary"]

rb1, rb2, rb3, rb4 = st.columns(4)

with rb1:
    st.metric(
        "ACTIONS TESTED",
        len(robustness_summary),
    )

with rb2:
    st.metric(
        "SCENARIOS / ACTION",
        robustness_analysis["scenarios_per_action"],
    )

with rb3:
    st.metric(
        "BASELINE RISK",
        f"{robustness_analysis['baseline_risk']:.1f}/100",
    )

with rb4:
    robust_count = int(
        (robustness_summary["stability"] == "ROBUST").sum()
    )
    st.metric(
        "ROBUST ACTIONS",
        robust_count,
    )

st.markdown("### ROBUSTNESS COMPARISON")

display_cols = [
    "action",
    "robustness_score",
    "average_reduction",
    "minimum_reduction",
    "worst_case_risk",
    "stability",
]

st.dataframe(
    robustness_summary[display_cols],
    width='stretch',
    hide_index=True,
)

fig_robustness = go.Figure()

fig_robustness.add_trace(
    go.Bar(
        x=robustness_summary["action"],
        y=robustness_summary["robustness_score"],
        name="Robustness",
        text=robustness_summary["robustness_score"].map(
            lambda value: f"{value:.1f}"
        ),
        textposition="outside",
    )
)

fig_robustness.update_layout(
    title="Decision Robustness Across Modeled Conditions",
    yaxis_title="Robustness Score",
    xaxis_title="Intervention",
    yaxis=dict(range=[0, 100]),
    height=420,
    template="plotly_dark",
)

st.plotly_chart(
    fig_robustness,
    width='stretch',
)

st.markdown("### STRESS-TEST INTERPRETATION")

for _, row in robustness_summary.iterrows():
    st.write(
        f"**{row['action']}** — "
        f"{row['stability']} · "
        f"robustness {row['robustness_score']:.1f}/100 · "
        f"average reduction {row['average_reduction']:.1f} · "
        f"worst-case modeled risk {row['worst_case_risk']:.1f}"
    )

st.caption(
    "The stress test varies rainfall, river level, response delay and bridge "
    "availability. Results are modeled counterfactuals and should not be "
    "interpreted as operational emergency guidance."
)
