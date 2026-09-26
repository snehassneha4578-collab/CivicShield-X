from __future__ import annotations

from typing import Any


DEFAULT_DISTRICTS = [
    {
        "id": "DIST-01",
        "name": "Riverside",
        "population": 25000,
        "risk_profile": "flood_sensitive",
    },
    {
        "id": "DIST-02",
        "name": "Central",
        "population": 18000,
        "risk_profile": "infrastructure_dense",
    },
    {
        "id": "DIST-03",
        "name": "North",
        "population": 15000,
        "risk_profile": "transport_sensitive",
    },
]


DEFAULT_INFRASTRUCTURE = [
    {
        "id": "WATER-01",
        "name": "City Water Plant",
        "type": "water",
        "district": "DIST-01",
        "capacity": 85,
    },
    {
        "id": "BRIDGE-01",
        "name": "River Bridge",
        "type": "bridge",
        "district": "DIST-01",
        "capacity": 80,
    },
    {
        "id": "ROAD-01",
        "name": "North Highway",
        "type": "road",
        "district": "DIST-03",
        "capacity": 90,
    },
    {
        "id": "POWER-01",
        "name": "North Power Substation",
        "type": "power",
        "district": "DIST-03",
        "capacity": 88,
    },
    {
        "id": "HOSP-01",
        "name": "Central Hospital",
        "type": "hospital",
        "district": "DIST-02",
        "capacity": 82,
    },
    {
        "id": "FIRE-01",
        "name": "Central Fire Station",
        "type": "emergency",
        "district": "DIST-02",
        "capacity": 78,
    },
]


DEFAULT_DEPENDENCIES = [
    ("WATER-01", "BRIDGE-01", "river_overflow", 0.85),
    ("BRIDGE-01", "ROAD-01", "bridge_stress", 0.90),
    ("ROAD-01", "FIRE-01", "response_delay", 0.75),
    ("ROAD-01", "HOSP-01", "ambulance_delay", 0.80),
    ("POWER-01", "HOSP-01", "power_dependency", 0.70),
    ("WATER-01", "HOSP-01", "water_dependency", 0.55),
]


def generate_city(seed: int = 42) -> dict[str, Any]:
    districts = [dict(item) for item in DEFAULT_DISTRICTS]
    infrastructure = [dict(item) for item in DEFAULT_INFRASTRUCTURE]

    dependencies = [
        {
            "source": source,
            "target": target,
            "mechanism": mechanism,
            "strength": strength,
        }
        for source, target, mechanism, strength in DEFAULT_DEPENDENCIES
    ]

    total_population = sum(
        int(district["population"]) for district in districts
    )

    return {
        "city_id": f"CITY-SYN-{seed}",
        "name": "CivicShield Synthetic City",
        "seed": seed,
        "districts": districts,
        "infrastructure": infrastructure,
        "dependencies": dependencies,
        "population": total_population,
        "infrastructure_count": len(infrastructure),
        "dependency_count": len(dependencies),
    }


def city_summary(city: dict[str, Any]) -> dict[str, Any]:
    return {
        "city_id": city["city_id"],
        "districts": len(city["districts"]),
        "population": int(city["population"]),
        "infrastructure": int(city["infrastructure_count"]),
        "dependencies": int(city["dependency_count"]),
    }
