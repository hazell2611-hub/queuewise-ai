import os
import sys

# Supaya "from app import app" dan "from engine..." bisa bekerja dari dalam folder tests/
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app
from engine.scenarios import apply_scenario, build_scenarios, make_scenario, run_scenarios
from engine.simulation import calculate_metrics, simulate_queue
from engine.validation import validate_inputs

client = app.test_client()

BASE = {
    "arrival_rate": 40, "service_time": 3, "staff": 2, "operating_hours": 8,
    "staff_cost": 25000, "max_wait": 5, "budget": 700000, "description": "",
}


def params(**changes):
    payload = dict(BASE)
    payload.update(changes)
    return validate_inputs(payload)


def approx(a, b, tol=1e-9):
    return abs(a - b) <= tol


def test_default_scenarios():
    scenarios = build_scenarios(params())
    ids = [s["id"] for s in scenarios]
    assert ids == ["current", "add_1", "add_2", "faster", "preorder", "add_1_faster"], ids
    assert len(set(ids)) == len(ids), "ID skenario harus unik"


def test_zero_percent_skips_scenarios():
    ids = [s["id"] for s in build_scenarios(params(speedup_percent=0, preorder_share_percent=0))]
    assert ids == ["current", "add_1", "add_2"], ids


def test_apply_scenario_math():
    base = params()
    eff = apply_scenario(base, make_scenario("x", "x", staff_change=1, service_speedup=0.2, demand_shift=0.25))
    assert eff["staff"] == 3
    assert approx(eff["service_time"], 2.4)
    assert approx(eff["arrival_rate"], 30.0)


def test_cost_and_budget():
    results = {r["id"]: r for r in run_scenarios(params(), build_scenarios(params()))}
    assert approx(results["current"]["cost"]["total"], 400000)        # 2 x 8 x 25.000
    assert approx(results["add_1"]["cost"]["total"], 600000)          # 3 x 8 x 25.000
    assert approx(results["add_2"]["cost"]["total"], 800000)          # 4 x 8 x 25.000
    assert results["add_1"]["cost"]["within_budget"] is True
    assert results["add_2"]["cost"]["within_budget"] is False         # melebihi 700.000
    assert approx(results["faster"]["cost"]["total"], 430000)         # 400.000 + 30.000
    assert approx(results["add_1_faster"]["cost"]["total"], 630000)   # 600.000 + 30.000


def test_current_matches_direct_simulation():
    results = {r["id"]: r for r in run_scenarios(params(), build_scenarios(params()), seed=42)}
    expected = calculate_metrics(simulate_queue(40, 3, 2, 8, seed=42), 2, 8)
    for key, value in expected.items():
        assert approx(results["current"]["metrics"][key], value), f"Metrik {key} berbeda"


def test_more_staff_less_waiting_same_day():
    results = {r["id"]: r for r in run_scenarios(params(), build_scenarios(params()))}
    waits = [results[k]["metrics"]["avg_wait"] for k in ("current", "add_1", "add_2")]
    assert waits[0] >= waits[1] >= waits[2], waits
    assert results["add_1"]["metrics"]["customers_served"] == results["add_2"]["metrics"]["customers_served"]


def test_stability_flags():
    results = {r["id"]: r for r in run_scenarios(params(), build_scenarios(params()))}
    assert results["current"]["capacity"]["is_stable"] is False       # 40 vs kapasitas 40
    assert results["add_1"]["capacity"]["is_stable"] is True
    assert results["faster"]["capacity"]["is_stable"] is True         # layanan 2,4 menit -> kapasitas 50


def test_custom_scenarios():
    custom = [{"name": "Mine", "staff_change": 1, "speedup_percent": 10, "extra_cost": 5000}, {}]
    scenarios = build_scenarios(params(custom_scenarios=custom))
    assert [s["id"] for s in scenarios][-2:] == ["custom_1", "custom_2"]
    assert scenarios[-2]["name"] == "Mine"
    assert scenarios[-1]["name"] == "Custom scenario"


def test_bad_custom_scenarios_rejected():
    bad_specs = [
        {"staff_change": -2},              # staf dasar 2, hasilnya 0
        {"staff_change": 1.5},
        {"speedup_percent": 80},
        {"preorder_share_percent": -5},
        {"extra_cost": "banyak"},
        "bukan dictionary",
    ]
    for spec in bad_specs:
        try:
            build_scenarios(params(custom_scenarios=[spec]))
        except ValueError:
            continue
        raise AssertionError(f"Seharusnya ditolak: {spec}")


def test_too_many_custom_scenarios_rejected():
    try:
        params(custom_scenarios=[{}] * 6)
    except ValueError:
        return
    raise AssertionError("Lebih dari 5 skenario custom seharusnya ditolak")


def test_api_scenarios_endpoint():
    response = client.post("/api/scenarios", json=dict(BASE))
    assert response.status_code == 200
    body = response.get_json()
    assert len(body["scenarios"]) == 6
    first = body["scenarios"][0]
    assert {"metrics", "cost", "capacity", "effective", "name"} <= set(first)


def test_api_scenarios_rejects_bad_input():
    assert client.post("/api/scenarios", json=dict(BASE, staff=0)).status_code == 400
    assert client.post("/api/scenarios", json=dict(BASE, custom_scenarios=[{"speedup_percent": 99}])).status_code == 400
    assert client.post("/api/scenarios", data="x", content_type="text/plain").status_code == 400
    assert client.get("/api/scenarios").status_code == 405


if __name__ == "__main__":
    tests = [
        test_default_scenarios, test_zero_percent_skips_scenarios, test_apply_scenario_math,
        test_cost_and_budget, test_current_matches_direct_simulation,
        test_more_staff_less_waiting_same_day, test_stability_flags, test_custom_scenarios,
        test_bad_custom_scenarios_rejected, test_too_many_custom_scenarios_rejected,
        test_api_scenarios_endpoint, test_api_scenarios_rejects_bad_input,
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