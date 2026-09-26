from pathlib import Path
import json
from datetime import datetime

MEMORY_FILE = Path("data/city_memory.json")


def load_city_memory():
    if not MEMORY_FILE.exists():
        return []

    try:
        return json.loads(MEMORY_FILE.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return []


def save_crisis_snapshot(
    crisis,
    risk_score,
    risk_level,
    cascade_summary,
    response_action=None,
):
    memory = load_city_memory()

    snapshot = {
        "id": f"CRISIS-{len(memory) + 1:03d}",
        "timestamp": datetime.now().isoformat(timespec="seconds"),
        "crisis": str(crisis),
        "risk_score": round(float(risk_score), 1),
        "risk_level": str(risk_level),
        "affected_nodes": int(cascade_summary.get("affected_nodes", 0)),
        "maximum_impact": round(
            float(cascade_summary.get("maximum_impact", 0)), 2
        ),
        "population_risk": round(
            float(cascade_summary.get("population_risk", 0)), 2
        ),
        "response_action": (
            str(response_action)
            if response_action
            else "No response recorded"
        ),
    }

    memory.append(snapshot)

    MEMORY_FILE.parent.mkdir(parents=True, exist_ok=True)
    MEMORY_FILE.write_text(
        json.dumps(memory, indent=2),
        encoding="utf-8",
    )

    return snapshot


def compare_city_memory(current_risk, memory):
    if not memory:
        return {
            "previous_count": 0,
            "average_risk": 0.0,
            "highest_risk": 0.0,
            "current_vs_average": 0.0,
        }

    risks = [float(item["risk_score"]) for item in memory]

    average_risk = sum(risks) / len(risks)
    highest_risk = max(risks)

    return {
        "previous_count": len(memory),
        "average_risk": round(average_risk, 1),
        "highest_risk": round(highest_risk, 1),
        "current_vs_average": round(
            float(current_risk) - average_risk,
            1,
        ),
    }


def save_experiment(
    name,
    rainfall,
    river_level,
    response_delay,
    bridge_available,
    risk_score,
    risk_level,
):
    memory = load_city_memory()

    experiments = [
        item for item in memory
        if item.get("record_type") == "experiment"
    ]

    experiment = {
        "record_type": "experiment",
        "id": f"EXP-{len(experiments) + 1:03d}",
        "timestamp": datetime.now().isoformat(timespec="seconds"),
        "name": str(name),
        "rainfall": round(float(rainfall), 1),
        "river_level": round(float(river_level), 1),
        "response_delay": round(float(response_delay), 1),
        "bridge_available": bool(bridge_available),
        "risk_score": round(float(risk_score), 1),
        "risk_level": str(risk_level),
    }

    memory.append(experiment)

    MEMORY_FILE.parent.mkdir(parents=True, exist_ok=True)
    MEMORY_FILE.write_text(
        json.dumps(memory, indent=2),
        encoding="utf-8",
    )

    return experiment


def load_experiments():
    memory = load_city_memory()
    return [
        item for item in memory
        if item.get("record_type") == "experiment"
    ]
