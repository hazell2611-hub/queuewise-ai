import os
import sys

# Supaya "from app import app" dan "from engine..." bisa bekerja dari dalam folder tests/
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app
from engine.simulation import calculate_metrics, simulate_queue

# "Browser palsu" dari Flask: bisa mengirim permintaan tanpa menyalakan server
client = app.test_client()

VALID = {
    "arrival_rate": 40, "service_time": 3, "staff": 3, "operating_hours": 8,
    "staff_cost": 25000, "max_wait": 5, "budget": 700000, "description": "",
}


def post(payload):
    return client.post("/api/simulate", json=payload)


def with_change(**changes):
    payload = dict(VALID)
    payload.update(changes)
    return payload


def test_valid_request_matches_engine():
    response = post(VALID)
    assert response.status_code == 200
    body = response.get_json()
    expected = calculate_metrics(simulate_queue(40, 3, 3, 8, seed=42), 3, 8)
    for key, value in expected.items():
        assert abs(body["metrics"][key] - value) < 1e-9, f"Metrik {key} berbeda dari mesin simulasi"


def test_stability_flag():
    assert post(with_change(staff=2)).get_json()["capacity"]["is_stable"] is False
    assert post(with_change(staff=3)).get_json()["capacity"]["is_stable"] is True


def test_missing_field_rejected():
    payload = dict(VALID)
    del payload["budget"]
    response = post(payload)
    assert response.status_code == 400
    assert "error" in response.get_json()


def test_bad_values_rejected():
    bad_payloads = [
        with_change(staff=0),
        with_change(staff=2.5),
        with_change(arrival_rate=-5),
        with_change(service_time=0),
        with_change(operating_hours=100),
        with_change(arrival_rate="abc"),
        with_change(staff=True),
        with_change(arrival_rate=None),
    ]
    for payload in bad_payloads:
        assert post(payload).status_code == 400, f"Seharusnya ditolak: {payload}"


def test_not_json_rejected():
    response = client.post("/api/simulate", data="halo", content_type="text/plain")
    assert response.status_code == 400


def test_wrong_method_rejected():
    assert client.get("/api/simulate").status_code == 405


if __name__ == "__main__":
    tests = [
        test_valid_request_matches_engine,
        test_stability_flag,
        test_missing_field_rejected,
        test_bad_values_rejected,
        test_not_json_rejected,
        test_wrong_method_rejected,
    ]
    failed = 0
    for test in tests:
        try:
            test()
            print(f"LULUS  {test.__name__}")
        except AssertionError as error:
            failed += 1
            print(f"GAGAL  {test.__name__}: {error}")
    print(f"\n{len(tests) - failed} dari {len(tests)} tes lulus")