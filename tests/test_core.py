from app.core.simulation import run_simulation

result = run_simulation("flood")

assert result["risk_score"] >= 0
assert result["risk_score"] <= 100
assert result["risk_level"] in ["LOW", "MODERATE", "HIGH", "CRITICAL"]

print("CivicShield-X core simulation test PASSED")
print("Risk:", result["risk_score"])
print("Level:", result["risk_level"])
