import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app

client = app.test_client()

BASE = {"arrival_rate": 40, "service_time": 3, "staff": 2, "operating_hours": 8,
        "staff_cost": 25000, "max_wait": 5, "budget": 700000, "description": ""}


def test_statistics_endpoint_shape():
    response = client.post("/api/scenarios/statistics", json=dict(BASE, replications=20))
    assert response.status_code == 200
    body = response.get_json()
    assert body["replications"] == 20
    first = body["scenarios"][0]
    assert "half_width" in first["metrics"]["avg_wait"]
    assert "low" in first["metrics"]["avg_wait"] and "high" in first["metrics"]["avg_wait"]


def test_statistics_endpoint_has_theory_validation():
    response = client.post("/api/scenarios/statistics", json=dict(BASE, replications=40))
    body = response.get_json()
    names = [t["scenario"] for t in body["theory_validation"]]
    assert "Add 1 staff" in names
    assert "Current staffing" not in names       # tidak stabil, dilewati
    assert "Faster service (-20%)" not in names  # bukan M/M/c murni, dilewati


def test_statistics_endpoint_rejects_bad_replications():
    assert client.post("/api/scenarios/statistics", json=dict(BASE, replications=2)).status_code == 400
    assert client.post("/api/scenarios/statistics", json=dict(BASE, replications=1000)).status_code == 400
    assert client.post("/api/scenarios/statistics", json=dict(BASE, replications="many")).status_code == 400


def test_statistics_endpoint_default_replications():
    payload = dict(BASE)
    response = client.post("/api/scenarios/statistics", json=payload)
    assert response.get_json()["replications"] == 30


if __name__ == "__main__":
    tests = [test_statistics_endpoint_shape, test_statistics_endpoint_has_theory_validation,
              test_statistics_endpoint_rejects_bad_replications, test_statistics_endpoint_default_replications]
    failed = 0
    for test in tests:
        try:
            test()
            print(f"LULUS  {test.__name__}")
        except AssertionError as error:
            failed += 1
            print(f"GAGAL  {test.__name__}: {error}")
    print(f"\n{len(tests) - failed} dari {len(tests)} tes lulus")