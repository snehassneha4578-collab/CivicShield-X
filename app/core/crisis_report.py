from pathlib import Path
from datetime import datetime


def build_crisis_report(
    simulation: dict,
    cascade_df,
    summary: dict,
    risk_explanations: list[dict] | None = None,
) -> str:
    risk_explanations = risk_explanations or []

    crisis = str(simulation.get("crisis", "unknown")).upper()
    risk_score = float(simulation.get("risk_score", 0))
    risk_level = str(simulation.get("risk_level", "UNKNOWN"))

    sensors = simulation.get("sensors")
    sensor_lines = []

    if sensors is not None:
        for _, row in sensors.iterrows():
            sensor_lines.append(
                f"- {row['sensor']}: {float(row['value']):.2f} "
                f"(threshold {float(row['critical_threshold']):.2f})"
            )

    active_drivers = [
        item for item in risk_explanations
        if item.get("active")
    ]

    driver_lines = []
    for item in active_drivers:
        driver_lines.append(
            f"- {item['driver']}: {item['value']:.2f} "
            f"(contribution {item['contribution']} points) | {item['reason']}"
        )

    cascade_lines = []
    if cascade_df is not None and not cascade_df.empty:
        for _, row in cascade_df.iterrows():
            cascade_lines.append(
                f"- Stage {int(row['stage'])}: {row['name']} "
                f"({row['node']}) | impact {float(row['impact']):.2f}, "
                f"status {row['status']}"
            )

    generated_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    return f"""# CivicShield-X Crisis Intelligence Report

**Generated:** {generated_at}

## Crisis Overview

- **Scenario:** {crisis}
- **Modeled Risk:** {risk_score:.1f}/100
- **Risk Level:** {risk_level}
- **Affected Nodes:** {summary.get("affected_nodes", 0)}
- **Population Risk:** {float(summary.get("population_risk", 0)):.2f}
- **Maximum Cascade Impact:** {float(summary.get("maximum_impact", 0)):.2f}
- **Average Cascade Impact:** {float(summary.get("average_impact", 0)):.2f}

## Sensor State

{chr(10).join(sensor_lines) if sensor_lines else "- No sensor data available."}

## Active Risk Drivers

{chr(10).join(driver_lines) if driver_lines else "- No modeled threshold drivers are currently active."}

## Crisis Propagation

{chr(10).join(cascade_lines) if cascade_lines else "- No cascade events available."}

## System Interpretation

CivicShield-X detected a modeled {risk_level.lower()}-level crisis state and evaluated
the resulting infrastructure dependency cascade.

The report summarizes simulation outputs, threshold-based risk drivers, and modeled
propagation effects. These outputs are synthetic prototype results and are not
real-world emergency forecasts or operational guidance.
"""


def save_crisis_report(report: str, output_dir: str = "reports") -> str:
    directory = Path(output_dir)
    directory.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    path = directory / f"crisis_report_{timestamp}.md"
    path.write_text(report, encoding="utf-8")
    return str(path)
