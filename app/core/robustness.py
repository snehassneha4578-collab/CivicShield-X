from __future__ import annotations

from itertools import product
from typing import Any

import pandas as pd

from app.core.what_if import run_what_if


def _scenario_variants(base_simulation: dict[str, Any]) -> list[dict[str, Any]]:
    sensors = base_simulation.get("sensors", {})

    rainfall = float(sensors.get("rainfall_mm", 0))
    river = float(sensors.get("river_level_pct", 0))

    variants = []

    for rainfall_delta, river_delta, delay, bridge_available in product(
        (-15.0, 0.0, 15.0),
        (-10.0, 0.0, 10.0),
        (0.0, 10.0),
        (True, False),
    ):
        variants.append(
            {
                "rainfall": max(0.0, min(150.0, rainfall + rainfall_delta)),
                "river_level": max(0.0, min(100.0, river + river_delta)),
                "response_delay": delay,
                "bridge_available": bridge_available,
                "condition": (
                    f"rainfall {rainfall_delta:+.0f}, "
                    f"river {river_delta:+.0f}, "
                    f"delay +{delay:.0f}, "
                    f"bridge {'ON' if bridge_available else 'OFF'}"
                ),
            }
        )

    return variants


def evaluate_action_robustness(
    base_simulation: dict[str, Any],
    action: str,
) -> pd.DataFrame:
    variants = _scenario_variants(base_simulation)
    baseline_risk = float(base_simulation.get("risk_score", 0))

    rows = []

    for i, scenario in enumerate(variants, start=1):
        if action == "Protect River Bridge":
            bridge_available = True
        elif action == "Protect Riverside Zone":
            bridge_available = scenario["bridge_available"]
        elif action == "Activate Emergency Routing":
            bridge_available = scenario["bridge_available"]
        else:
            bridge_available = scenario["bridge_available"]

        result = run_what_if(
            base_simulation,
            rainfall=scenario["rainfall"],
            river_level=scenario["river_level"],
            response_delay=scenario["response_delay"],
            bridge_available=bridge_available,
        )

        simulated_risk = float(result["risk_score"])
        reduction = baseline_risk - simulated_risk

        rows.append(
            {
                "scenario_id": f"ROB-{i:02d}",
                "action": action,
                "condition": scenario["condition"],
                "baseline_risk": round(baseline_risk, 2),
                "simulated_risk": round(simulated_risk, 2),
                "risk_reduction": round(reduction, 2),
                "effective": reduction > 0,
            }
        )

    return pd.DataFrame(rows)



def calculate_robustness_score(results: pd.DataFrame) -> dict[str, Any]:
    if results.empty:
        return {
            "robustness_score": 0.0,
            "effective_rate": 0.0,
            "minimum_reduction": 0.0,
            "average_reduction": 0.0,
            "reduction_variability": 0.0,
            "worst_case_risk": 0.0,
            "stability": "UNKNOWN",
        }

    reductions = results["risk_reduction"].astype(float)
    reduction_std = float(reductions.std()) if len(reductions) > 1 else 0.0

    effective_rate = float((reductions > 0).mean() * 100)
    minimum_reduction = float(reductions.min())
    average_reduction = float(reductions.mean())
    worst_case_risk = float(results["simulated_risk"].max())

    effect_component = max(0.0, min(100.0, average_reduction * 2.0))
    worst_case_component = max(
        0.0,
        min(100.0, (minimum_reduction + 10.0) * 2.5),
    )
    stability_component = max(
        0.0,
        min(100.0, 100.0 - reduction_std * 3.0),
    )

    robustness_score = max(
        0.0,
        min(
            100.0,
            effective_rate * 0.35
            + effect_component * 0.30
            + worst_case_component * 0.20
            + stability_component * 0.15,
        ),
    )

    if robustness_score >= 75:
        stability = "ROBUST"
    elif robustness_score >= 50:
        stability = "CONDITIONAL"
    else:
        stability = "FRAGILE"

    return {
        "robustness_score": round(robustness_score, 1),
        "effective_rate": round(effective_rate, 1),
        "minimum_reduction": round(minimum_reduction, 1),
        "average_reduction": round(average_reduction, 1),
        "reduction_variability": round(reduction_std, 1),
        "worst_case_risk": round(worst_case_risk, 1),
        "stability": stability,
    }


def run_robustness_analysis(
    base_simulation: dict[str, Any],
    actions: list[str] | None = None,
) -> dict[str, Any]:
    if actions is None:
        actions = [
            "Protect River Bridge",
            "Protect Riverside Zone",
            "Activate Emergency Routing",
        ]

    analyses = []

    for action in actions:
        results = evaluate_action_robustness(base_simulation, action)
        summary = calculate_robustness_score(results)
        analyses.append(
            {
                "action": action,
                **summary,
                "results": results,
            }
        )

    summary_df = pd.DataFrame(
        [
            {
                "action": item["action"],
                "robustness_score": item["robustness_score"],
                "effective_rate": item["effective_rate"],
                "minimum_reduction": item["minimum_reduction"],
                "average_reduction": item["average_reduction"],
                "worst_case_risk": item["worst_case_risk"],
                "stability": item["stability"],
            }
            for item in analyses
        ]
    )

    return {
        "baseline_risk": float(base_simulation.get("risk_score", 0)),
        "scenarios_per_action": len(analyses[0]["results"]) if analyses else 0,
        "summary": summary_df,
        "analyses": analyses,
    }
