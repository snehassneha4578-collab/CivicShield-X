import numpy as np
import pandas as pd

CITY_NODES = [
    {"id": "HOSP-01", "name": "Central Hospital", "type": "hospital", "population": 8500},
    {"id": "POWER-01", "name": "North Power Substation", "type": "power", "population": 0},
    {"id": "WATER-01", "name": "City Water Plant", "type": "water", "population": 0},
    {"id": "ROAD-01", "name": "North Highway", "type": "road", "population": 12000},
    {"id": "BRIDGE-01", "name": "River Bridge", "type": "bridge", "population": 18000},
    {"id": "FIRE-01", "name": "Central Fire Station", "type": "emergency", "population": 0},
    {"id": "RES-01", "name": "Riverside Residential Zone", "type": "residential", "population": 25000},
]

def generate_sensor_state(crisis="normal", seed=42):
    rng = np.random.default_rng(seed)

    rainfall = rng.normal(18, 4)
    river_level = rng.normal(42, 3)
    traffic = rng.normal(48, 7)
    power_load = rng.normal(62, 5)
    water_pressure = rng.normal(78, 4)
    hospital_load = rng.normal(54, 5)

    if crisis == "flood":
        rainfall += 75
        river_level += 42
        traffic += 25
        water_pressure -= 18
        hospital_load += 12

    elif crisis == "power_failure":
        power_load += 28
        hospital_load += 20
        traffic += 8
        water_pressure -= 8

    elif crisis == "fire":
        traffic += 28
        hospital_load += 25
        power_load += 12

    return pd.DataFrame([
        ["rainfall_mm", max(0, rainfall), 100, "weather"],
        ["river_level_pct", np.clip(river_level, 0, 100), 100, "water"],
        ["traffic_pct", np.clip(traffic, 0, 100), 100, "transport"],
        ["power_load_pct", np.clip(power_load, 0, 120), 100, "energy"],
        ["water_pressure_pct", np.clip(water_pressure, 0, 100), 100, "water"],
        ["hospital_load_pct", np.clip(hospital_load, 0, 120), 100, "health"],
    ], columns=["sensor", "value", "critical_threshold", "domain"])

def run_multi_crisis(crises=None, seed=42):
    """Combine multiple crisis scenarios into one modeled city state."""
    if not crises:
        crises = ["flood"]

    crises = list(dict.fromkeys(crises))

    base = generate_sensor_state("normal", seed=seed).copy()

    for crisis in crises:
        crisis_df = generate_sensor_state(crisis, seed=seed).copy()

        for _, row in crisis_df.iterrows():
            sensor = row["sensor"]
            value = float(row["value"])

            base.loc[
                base["sensor"] == sensor,
                "value"
            ] = (
                base.loc[
                    base["sensor"] == sensor,
                    "value"
                ].iloc[0]
                + (value - float(
                    generate_sensor_state("normal", seed=seed)
                    .loc[
                        lambda df: df["sensor"] == sensor,
                        "value"
                    ].iloc[0]
                ))
            )

    base["value"] = base["value"].clip(lower=0, upper=150)

    risk_result = calculate_risk(base)

    if isinstance(risk_result, tuple):
        risk = float(risk_result[0])
    else:
        risk = float(risk_result)

    return {
        "crises": crises,
        "risk_score": risk,
        "risk_level": (
            "CRITICAL" if risk >= 75
            else "HIGH" if risk >= 50
            else "MODERATE" if risk >= 25
            else "LOW"
        ),
        "sensors": base,
        "city_nodes": pd.DataFrame(CITY_NODES),
    }


def calculate_risk(sensor_df):
    risk = 0

    rainfall = sensor_df.loc[sensor_df.sensor == "rainfall_mm", "value"].iloc[0]
    river = sensor_df.loc[sensor_df.sensor == "river_level_pct", "value"].iloc[0]
    traffic = sensor_df.loc[sensor_df.sensor == "traffic_pct", "value"].iloc[0]
    power = sensor_df.loc[sensor_df.sensor == "power_load_pct", "value"].iloc[0]
    hospital = sensor_df.loc[sensor_df.sensor == "hospital_load_pct", "value"].iloc[0]

    if rainfall > 60:
        risk += 25
    if river > 70:
        risk += 25
    if traffic > 75:
        risk += 15
    if power > 90:
        risk += 15
    if hospital > 80:
        risk += 20

    risk = min(100, risk)

    if risk >= 75:
        level = "CRITICAL"
    elif risk >= 50:
        level = "HIGH"
    elif risk >= 25:
        level = "MODERATE"
    else:
        level = "LOW"

    return risk, level


def explain_risk(sensor_df):
    rules = [
        ("Rainfall", "rainfall_mm", 60, 25, "rainfall exceeds the modeled flood threshold"),
        ("River level", "river_level_pct", 70, 25, "river level exceeds the modeled overflow threshold"),
        ("Traffic stress", "traffic_pct", 75, 15, "traffic stress exceeds the modeled transport threshold"),
        ("Power load", "power_load_pct", 90, 15, "power load exceeds the modeled infrastructure threshold"),
        ("Hospital load", "hospital_load_pct", 80, 20, "hospital load exceeds the modeled health threshold"),
    ]

    explanations = []
    for name, sensor, threshold, contribution, reason in rules:
        value = float(sensor_df.loc[sensor_df.sensor == sensor, "value"].iloc[0])
        active = value > threshold
        explanations.append({
            "driver": name,
            "sensor": sensor,
            "value": round(value, 2),
            "threshold": threshold,
            "contribution": contribution if active else 0,
            "active": active,
            "reason": reason if active else f"{name.lower()} remains below the modeled threshold",
        })

    return sorted(
        explanations,
        key=lambda item: (item["active"], item["contribution"], item["value"]),
        reverse=True,
    )



def run_simulation(crisis="normal", seed=42):
    sensors = generate_sensor_state(crisis, seed)
    risk, level = calculate_risk(sensors)

    return {
        "crisis": crisis,
        "risk_score": risk,
        "risk_level": level,
        "sensors": sensors,
        "city_nodes": pd.DataFrame(CITY_NODES),
    }

if __name__ == "__main__":
    result = run_simulation("flood")
    print("CivicShield-X Simulation")
    print("=" * 40)
    print("Crisis:", result["crisis"])
    print("Risk:", result["risk_score"])
    print("Level:", result["risk_level"])
    print("\nSensor State:")
    print(result["sensors"].to_string(index=False))
