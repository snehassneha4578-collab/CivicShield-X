from __future__ import annotations

import pandas as pd


def calculate_city_health(
    sensor_df: pd.DataFrame,
    cascade_summary: dict,
    risk_score: float,
) -> dict:
    anomaly_pressure = 0.0

    for _, row in sensor_df.iterrows():
        value = float(row["value"])
        threshold = float(row["critical_threshold"])
        sensor = str(row["sensor"])

        if sensor == "water_pressure_pct":
            deviation = max(0.0, threshold - value)
        else:
            deviation = max(0.0, value - threshold)

        anomaly_pressure += min(25.0, deviation)

    cascade_pressure = min(
        30.0,
        float(cascade_summary.get("average_impact", 0.0)) * 0.30,
    )

    risk_pressure = min(40.0, float(risk_score) * 0.40)
    anomaly_pressure = min(30.0, anomaly_pressure * 0.30)

    health = max(
        0.0,
        min(100.0, 100.0 - risk_pressure - anomaly_pressure - cascade_pressure),
    )

    if health >= 75:
        state = "STABLE"
    elif health >= 50:
        state = "STRESSED"
    elif health >= 25:
        state = "DEGRADED"
    else:
        state = "CRITICAL"

    return {
        "health_score": round(health, 1),
        "state": state,
        "risk_pressure": round(risk_pressure, 1),
        "anomaly_pressure": round(anomaly_pressure, 1),
        "cascade_pressure": round(cascade_pressure, 1),
    }
