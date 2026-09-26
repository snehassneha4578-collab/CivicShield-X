import pandas as pd

DEPENDENCIES = [
    ("WATER-01", "BRIDGE-01", "river_overflow", 0.85),
    ("BRIDGE-01", "ROAD-01", "bridge_stress", 0.90),
    ("ROAD-01", "FIRE-01", "response_delay", 0.75),
    ("ROAD-01", "HOSP-01", "ambulance_delay", 0.80),
    ("POWER-01", "HOSP-01", "power_dependency", 0.70),
    ("WATER-01", "HOSP-01", "water_dependency", 0.55),
    ("ROAD-01", "RES-01", "mobility_disruption", 0.65),
]

NODE_NAMES = {
    "WATER-01": "City Water Plant",
    "BRIDGE-01": "River Bridge",
    "ROAD-01": "North Highway",
    "FIRE-01": "Central Fire Station",
    "HOSP-01": "Central Hospital",
    "POWER-01": "North Power Substation",
    "RES-01": "Riverside Residential Zone",
}

def simulate_cascade(risk_score, crisis="flood"):
    events = []

    if crisis == "flood":
        base = min(100, risk_score + 15)

        events.append({
            "stage": 1,
            "node": "WATER-01",
            "name": NODE_NAMES["WATER-01"],
            "cause": "Extreme rainfall and rising water level",
            "impact": min(100, base),
            "status": "CRITICAL"
        })

        bridge = min(100, base * 0.90)
        events.append({
            "stage": 2,
            "node": "BRIDGE-01",
            "name": NODE_NAMES["BRIDGE-01"],
            "cause": "River overflow reaches bridge infrastructure",
            "impact": bridge,
            "status": "CRITICAL" if bridge >= 70 else "STRESSED"
        })

        road = min(100, bridge * 0.92)
        events.append({
            "stage": 3,
            "node": "ROAD-01",
            "name": NODE_NAMES["ROAD-01"],
            "cause": "Bridge and roadway capacity degradation",
            "impact": road,
            "status": "CRITICAL" if road >= 70 else "STRESSED"
        })

        emergency = min(100, road * 0.82)
        events.append({
            "stage": 4,
            "node": "FIRE-01",
            "name": NODE_NAMES["FIRE-01"],
            "cause": "Emergency vehicle response delay",
            "impact": emergency,
            "status": "CRITICAL" if emergency >= 70 else "DEGRADED"
        })

        hospital = min(100, (road * 0.45) + (emergency * 0.45))
        events.append({
            "stage": 5,
            "node": "HOSP-01",
            "name": NODE_NAMES["HOSP-01"],
            "cause": "Ambulance delays and increasing emergency demand",
            "impact": hospital,
            "status": "CRITICAL" if hospital >= 70 else "STRESSED"
        })

        population = min(100, (road * 0.55) + (hospital * 0.45))
        events.append({
            "stage": 6,
            "node": "RES-01",
            "name": NODE_NAMES["RES-01"],
            "cause": "Mobility disruption and reduced emergency accessibility",
            "impact": population,
            "status": "CRITICAL" if population >= 70 else "AT RISK"
        })

    return pd.DataFrame(events)

def cascade_summary(cascade_df):
    return {
        "affected_nodes": len(cascade_df),
        "maximum_impact": round(cascade_df["impact"].max(), 2),
        "average_impact": round(cascade_df["impact"].mean(), 2),
        "population_risk": round(
            cascade_df.loc[cascade_df["node"] == "RES-01", "impact"].iloc[0], 2
        )
    }

if __name__ == "__main__":
    cascade = simulate_cascade(65, "flood")
    print("\nCIVICSHIELD-X CASCADE ENGINE")
    print("=" * 55)
    print(cascade[["stage", "name", "cause", "impact", "status"]].to_string(index=False))
    print("\nCASCADE SUMMARY")
    print(cascade_summary(cascade))


def build_crisis_replay(cascade_df, risk_score):
    """Build a chronological replay timeline from the modeled cascade."""
    if cascade_df is None or cascade_df.empty:
        return []

    events = []

    events.append({
        "time": "T+00 MIN",
        "stage": 0,
        "event": "CRISIS DETECTED",
        "node": "CITY",
        "impact": float(risk_score),
        "status": "DETECTED",
    })

    for _, row in cascade_df.sort_values("stage").iterrows():
        stage = int(row["stage"])
        minutes = stage * 3

        events.append({
            "time": f"T+{minutes:02d} MIN",
            "stage": stage,
            "event": row["cause"],
            "node": row["name"],
            "impact": round(float(row["impact"]), 2),
            "status": row["status"],
        })

    maximum_impact = max(
        float(event["impact"])
        for event in events
    )

    events.append({
        "time": f"T+{(len(events)) * 3:02d} MIN",
        "stage": len(events),
        "event": "CASCADE PEAK",
        "node": "CITY SYSTEM",
        "impact": round(maximum_impact, 2),
        "status": "PEAK",
    })

    return events
