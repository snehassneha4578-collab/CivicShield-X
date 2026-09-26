from app.core.cascade import simulate_cascade, cascade_summary

cascade = simulate_cascade(65, "flood")
summary = cascade_summary(cascade)

assert len(cascade) == 6
assert summary["affected_nodes"] == 6
assert 0 <= summary["population_risk"] <= 100

print("CivicShield-X cascade test PASSED")
print("Affected nodes:", summary["affected_nodes"])
print("Maximum impact:", summary["maximum_impact"])
print("Population risk:", summary["population_risk"])
