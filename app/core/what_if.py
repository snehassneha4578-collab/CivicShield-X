import pandas as pd

def run_what_if(base_simulation, rainfall, river_level, response_delay, bridge_available):
    sensors = base_simulation["sensors"].copy()

    adjustments = {
        "rainfall_mm": float(rainfall),
        "river_level_pct": float(river_level),
    }

    for sensor, value in adjustments.items():
        sensors.loc[sensors["sensor"] == sensor, "value"] = value

    risk = 0

    for _, row in sensors.iterrows():
        sensor = row["sensor"]
        value = float(row["value"])

        if sensor == "rainfall_mm" and value > 60:
            risk += 25
        elif sensor == "river_level_pct" and value > 70:
            risk += 25
        elif sensor == "traffic_pct" and value > 75:
            risk += 15
        elif sensor == "power_load_pct" and value > 90:
            risk += 15
        elif sensor == "hospital_load_pct" and value > 80:
            risk += 20

    if not bridge_available:
        risk += 12

    risk += min(15, float(response_delay) * 0.75)
    risk = min(100, round(risk, 1))

    if risk >= 75:
        level = "CRITICAL"
    elif risk >= 50:
        level = "HIGH"
    elif risk >= 25:
        level = "MODERATE"
    else:
        level = "LOW"

    return {
        "risk_score": risk,
        "risk_level": level,
        "sensors": sensors,
        "response_delay": response_delay,
        "bridge_available": bridge_available,
    }


def autonomous_decision_engine(base_simulation):
    """Evaluate modeled response actions and verify their risk effect."""
    baseline = float(base_simulation["risk_score"])

    actions = [
        {
            "id": "EVACUATE_RIVERSIDE",
            "name": "Protect Riverside Residential Zone",
            "rainfall_adjustment": 0,
            "river_adjustment": -8,
            "response_delay": 2,
            "bridge_available": True,
        },
        {
            "id": "PROTECT_BRIDGE",
            "name": "Protect River Bridge",
            "rainfall_adjustment": 0,
            "river_adjustment": -12,
            "response_delay": 3,
            "bridge_available": True,
        },
        {
            "id": "EMERGENCY_ROUTING",
            "name": "Activate Emergency Routing",
            "rainfall_adjustment": 0,
            "river_adjustment": 0,
            "response_delay": 0,
            "bridge_available": True,
        },
    ]

    evaluations = []

    for action in actions:
        sensors = base_simulation["sensors"].copy()

        rainfall = float(
            sensors.loc[
                sensors["sensor"] == "rainfall_mm",
                "value"
            ].iloc[0]
        )

        river = float(
            sensors.loc[
                sensors["sensor"] == "river_level_pct",
                "value"
            ].iloc[0]
        )

        scenario = run_what_if(
            base_simulation,
            rainfall + action["rainfall_adjustment"],
            river + action["river_adjustment"],
            action["response_delay"],
            action["bridge_available"],
        )

        scenario_risk = float(scenario["risk_score"])
        reduction = round(baseline - scenario_risk, 1)

        evaluations.append(
            {
                "action_id": action["id"],
                "action": action["name"],
                "baseline_risk": baseline,
                "simulated_risk": scenario_risk,
                "risk_reduction": reduction,
                "verified": scenario_risk < baseline,
            }
        )

    verified_actions = [
        item for item in evaluations
        if item["verified"]
    ]

    if verified_actions:
        decision = max(
            verified_actions,
            key=lambda item: item["risk_reduction"]
        )
    else:
        decision = {
            "action_id": "MONITOR",
            "action": "Continue monitoring city state",
            "baseline_risk": baseline,
            "simulated_risk": baseline,
            "risk_reduction": 0.0,
            "verified": False,
        }

    return {
        "baseline_risk": baseline,
        "decision": decision,
        "evaluations": evaluations,
        "verification": {
            "status": "VERIFIED" if decision["verified"] else "NO_EFFECT",
            "risk_reduced": decision["risk_reduction"],
        },
    }
