from __future__ import annotations

from itertools import combinations
from typing import Any

from app.core.what_if import run_what_if


def _get_sensor_value(simulation: dict[str, Any], sensor_name: str) -> float:
    sensors = simulation["sensors"]
    row = sensors.loc[sensors["sensor"] == sensor_name, "value"]
    if row.empty:
        return 0.0
    return float(row.iloc[0])


def generate_crisis_experiments(
    base_simulation: dict[str, Any],
    include_combinations: bool = True,
) -> list[dict[str, Any]]:
    """
    Generate intervention experiments from the actual CivicShield-X
    what-if simulation engine.

    This is a modeled experimentation system, not a real-world
    emergency recommendation system.
    """
    baseline_risk = float(base_simulation["risk_score"])

    rainfall = _get_sensor_value(base_simulation, "rainfall_mm")
    river = _get_sensor_value(base_simulation, "river_level_pct")

    actions = [
        {
            "id": "BASELINE",
            "name": "No Intervention",
            "rainfall": rainfall,
            "river": river,
            "response_delay": 5,
            "bridge_available": True,
        },
        {
            "id": "BRIDGE_PROTECTION",
            "name": "Protect River Bridge",
            "rainfall": rainfall,
            "river": max(0.0, river - 12.0),
            "response_delay": 3,
            "bridge_available": True,
        },
        {
            "id": "RIVERSIDE_PROTECTION",
            "name": "Protect Riverside Zone",
            "rainfall": rainfall,
            "river": max(0.0, river - 8.0),
            "response_delay": 2,
            "bridge_available": True,
        },
        {
            "id": "EMERGENCY_ROUTING",
            "name": "Activate Emergency Routing",
            "rainfall": rainfall,
            "river": river,
            "response_delay": 0,
            "bridge_available": True,
        },
        {
            "id": "BRIDGE_ISOLATION",
            "name": "Isolate Unsafe Bridge",
            "rainfall": rainfall,
            "river": river,
            "response_delay": 2,
            "bridge_available": False,
        },
    ]

    if include_combinations:
        pair_specs = [
            ("BRIDGE_PROTECTION", "EMERGENCY_ROUTING"),
            ("RIVERSIDE_PROTECTION", "EMERGENCY_ROUTING"),
            ("BRIDGE_PROTECTION", "RIVERSIDE_PROTECTION"),
        ]

        by_id = {item["id"]: item for item in actions}

        for first_id, second_id in pair_specs:
            first = by_id[first_id]
            second = by_id[second_id]

            actions.append(
                {
                    "id": f"{first_id}+{second_id}",
                    "name": f"{first['name']} + {second['name']}",
                    "rainfall": rainfall,
                    "river": max(
                        0.0,
                        river
                        - max(0.0, river - first["river"])
                        - max(0.0, river - second["river"]),
                    ),
                    "response_delay": min(
                        first["response_delay"],
                        second["response_delay"],
                    ),
                    "bridge_available": (
                        first["bridge_available"]
                        and second["bridge_available"]
                    ),
                }
            )

    experiments = []

    for action in actions:
        result = run_what_if(
            base_simulation,
            action["rainfall"],
            action["river"],
            action["response_delay"],
            action["bridge_available"],
        )

        simulated_risk = float(result["risk_score"])
        reduction = round(baseline_risk - simulated_risk, 1)

        experiments.append(
            {
                "experiment_id": action["id"],
                "experiment": action["name"],
                "baseline_risk": round(baseline_risk, 1),
                "simulated_risk": round(simulated_risk, 1),
                "risk_reduction": reduction,
                "risk_level": result["risk_level"],
                "response_delay": action["response_delay"],
                "bridge_available": action["bridge_available"],
                "verified_reduction": reduction > 0,
            }
        )

    return experiments


def summarize_experiments(
    experiments: list[dict[str, Any]],
) -> dict[str, Any]:
    if not experiments:
        return {
            "count": 0,
            "best_reduction": 0.0,
            "best_experiment": None,
            "verified_count": 0,
        }

    verified = [
        item for item in experiments
        if item["verified_reduction"]
    ]

    best = max(
        experiments,
        key=lambda item: item["risk_reduction"],
    )

    return {
        "count": len(experiments),
        "best_reduction": float(best["risk_reduction"]),
        "best_experiment": best["experiment"],
        "verified_count": len(verified),
    }

def analyze_intervention_synergy(
    experiments: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    """
    Compare individual intervention effects against their combinations.

    Synergy is a property of the CivicShield-X modeled simulation,
    not a claim about real-world emergency response.
    """
    by_id = {
        item["experiment_id"]: item
        for item in experiments
    }

    pairs = [
        (
            "BRIDGE_PROTECTION",
            "EMERGENCY_ROUTING",
            "BRIDGE_PROTECTION+EMERGENCY_ROUTING",
        ),
        (
            "RIVERSIDE_PROTECTION",
            "EMERGENCY_ROUTING",
            "RIVERSIDE_PROTECTION+EMERGENCY_ROUTING",
        ),
        (
            "BRIDGE_PROTECTION",
            "RIVERSIDE_PROTECTION",
            "BRIDGE_PROTECTION+RIVERSIDE_PROTECTION",
        ),
    ]

    results = []

    for first_id, second_id, combined_id in pairs:
        first = by_id.get(first_id)
        second = by_id.get(second_id)
        combined = by_id.get(combined_id)

        if not first or not second or not combined:
            continue

        expected = (
            float(first["risk_reduction"])
            + float(second["risk_reduction"])
        )

        actual = float(combined["risk_reduction"])
        synergy = round(actual - expected, 1)

        tolerance = 1.0

        if synergy > tolerance:
            classification = "SYNERGISTIC"
        elif synergy < -tolerance:
            classification = "CONFLICTING"
        else:
            classification = "ADDITIVE"

        results.append(
            {
                "combination": combined["experiment"],
                "first_action": first["experiment"],
                "second_action": second["experiment"],
                "expected_reduction": round(expected, 1),
                "actual_reduction": round(actual, 1),
                "synergy": synergy,
                "classification": classification,
            }
        )

    return results

