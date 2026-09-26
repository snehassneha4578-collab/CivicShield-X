from __future__ import annotations

from typing import Any

from app.core.what_if import run_what_if


def simulate_risk_timeline(
    base_simulation: dict[str, Any],
    delays: list[int] | None = None,
) -> list[dict[str, Any]]:
    if delays is None:
        delays = [0, 5, 10, 15, 20, 30, 45, 60]

    base_sensors = base_simulation["sensors"]
    base_rainfall = float(
        base_sensors.loc[
            base_sensors["sensor"] == "rainfall_mm", "value"
        ].iloc[0]
    )
    base_river = float(
        base_sensors.loc[
            base_sensors["sensor"] == "river_level_pct", "value"
        ].iloc[0]
    )

    trajectory = []

    for delay in delays:
        rainfall_growth = min(18.0, delay * 0.20)
        river_growth = min(14.0, delay * 0.16)

        scenario = run_what_if(
            base_simulation,
            rainfall=base_rainfall + rainfall_growth,
            river_level=base_river + river_growth,
            response_delay=float(delay),
            bridge_available=True,
        )

        trajectory.append({
            "delay_min": int(delay),
            "risk_score": round(float(scenario["risk_score"]), 1),
            "risk_level": str(scenario["risk_level"]),
            "rainfall": round(base_rainfall + rainfall_growth, 1),
            "river_level": round(base_river + river_growth, 1),
        })

    return trajectory


def summarize_risk_timeline(trajectory: list[dict[str, Any]]) -> dict[str, Any]:
    if not trajectory:
        return {
            "initial_risk": 0.0,
            "peak_risk": 0.0,
            "peak_delay": 0,
            "risk_change": 0.0,
        }

    first = trajectory[0]
    peak = max(trajectory, key=lambda item: item["risk_score"])

    return {
        "initial_risk": float(first["risk_score"]),
        "peak_risk": float(peak["risk_score"]),
        "peak_delay": int(peak["delay_min"]),
        "risk_change": round(
            float(peak["risk_score"]) - float(first["risk_score"]), 1
        ),
    }
