from __future__ import annotations

import pandas as pd


ANOMALY_THRESHOLDS = {
    "rainfall_mm": 60.0,
    "river_level_pct": 70.0,
    "traffic_pct": 75.0,
    "power_load_pct": 90.0,
    "water_pressure_pct": 55.0,
    "hospital_load_pct": 80.0,
}


def detect_anomalies(sensor_df: pd.DataFrame) -> pd.DataFrame:
    rows = []

    for _, row in sensor_df.iterrows():
        sensor = str(row["sensor"])
        value = float(row["value"])
        threshold = float(ANOMALY_THRESHOLDS.get(sensor, row["critical_threshold"]))

        if sensor == "water_pressure_pct":
            deviation = threshold - value
            anomaly = value < threshold
            direction = "LOW" if anomaly else "NORMAL"
        else:
            deviation = value - threshold
            anomaly = value > threshold
            direction = "HIGH" if anomaly else "NORMAL"

        severity = (
            "CRITICAL" if anomaly and abs(deviation) >= 20
            else "WARNING" if anomaly
            else "NORMAL"
        )

        rows.append({
            "sensor": sensor,
            "value": round(value, 2),
            "threshold": threshold,
            "deviation": round(deviation, 2),
            "direction": direction,
            "anomaly": anomaly,
            "severity": severity,
        })

    return pd.DataFrame(rows)


def summarize_anomalies(anomaly_df: pd.DataFrame) -> dict:
    active = anomaly_df[anomaly_df["anomaly"] == True]

    return {
        "total_sensors": int(len(anomaly_df)),
        "anomalies": int(len(active)),
        "critical": int((active["severity"] == "CRITICAL").sum()),
        "warnings": int((active["severity"] == "WARNING").sum()),
        "health": round(
            max(0.0, 100.0 - float(active["deviation"].abs().sum())),
            1,
        ),
    }
