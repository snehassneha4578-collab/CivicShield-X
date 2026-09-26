from __future__ import annotations

from typing import Any


def answer_command(
    command: str,
    simulation: dict[str, Any],
    cascade_summary: dict[str, Any],
    anomaly_summary: dict[str, Any],
    decision: dict[str, Any] | None = None,
) -> dict[str, Any]:
    text = command.strip().lower()
    risk = float(simulation.get("risk_score", 0))
    level = str(simulation.get("risk_level", "UNKNOWN"))

    if any(word in text for word in ["why", "risk", "danger", "threat"]):
        return {
            "intent": "RISK_EXPLANATION",
            "title": "Risk explanation",
            "response": (
                f"The city is currently at modeled risk {risk:.1f}/100 "
                f"({level}). The system detected "
                f"{anomaly_summary.get('anomalies', 0)} sensor anomalies and "
                f"{cascade_summary.get('affected_nodes', 0)} affected infrastructure nodes."
            ),
        }

    if any(word in text for word in ["anomal", "sensor", "detect"]):
        return {
            "intent": "ANOMALY_STATUS",
            "title": "Sensor anomaly status",
            "response": (
                f"{anomaly_summary.get('anomalies', 0)} of "
                f"{anomaly_summary.get('total_sensors', 0)} sensors are outside "
                f"their modeled thresholds, including "
                f"{anomaly_summary.get('critical', 0)} critical anomaly."
            ),
        }

    if any(word in text for word in ["cascade", "propagat", "spread"]):
        return {
            "intent": "CASCADE_STATUS",
            "title": "Crisis propagation",
            "response": (
                f"The modeled cascade affects "
                f"{cascade_summary.get('affected_nodes', 0)} infrastructure nodes. "
                f"Maximum impact is "
                f"{float(cascade_summary.get('maximum_impact', 0)):.1f}."
            ),
        }

    if any(word in text for word in ["bridge", "unavailable", "what if", "scenario"]):
        return {
            "intent": "WHAT_IF",
            "title": "Scenario analysis",
            "response": (
                "The What-If Crisis Lab can evaluate bridge availability, "
                "rainfall, river level, and response delay using the CivicShield-X model."
            ),
        }

    if any(word in text for word in ["response", "action", "protect", "evacuat"]):
        if decision:
            return {
                "intent": "RESPONSE_STATUS",
                "title": "Autonomous response",
                "response": (
                    f"The modeled decision engine selected "
                    f"{decision.get('selected_action', 'no action')} "
                    f"with a modeled risk of "
                    f"{float(decision.get('simulated_risk', risk)):.1f}/100."
                ),
            }

        return {
            "intent": "RESPONSE_STATUS",
            "title": "Response status",
            "response": "No autonomous response result is currently available.",
        }

    if any(word in text for word in ["health", "city health", "condition"]):
        return {
            "intent": "CITY_HEALTH",
            "title": "City health",
            "response": (
                "City health combines modeled risk, anomaly pressure, "
                "and infrastructure cascade pressure."
            ),
        }

    return {
        "intent": "GENERAL",
        "title": "CivicShield-X command",
        "response": (
            "I can analyze city risk, sensor anomalies, crisis propagation, "
            "What-If scenarios, city health, and modeled response actions."
        ),
    }
