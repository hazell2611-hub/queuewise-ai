import math
import os
import sys

# Supaya "from engine.simulation import ..." bisa bekerja dari dalam folder tests/,
# kita tambahkan folder utama proyek ke daftar tempat Python mencari modul.
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from engine.simulation import calculate_metrics, simulate_queue


# ---------- Alat bantu ----------
def approx(a, b, tol=1e-9):
    return abs(a - b) <= tol


def erlang_c_wait(arrival_rate, service_time, staff):
    """Rumus TEORI: rata-rata tunggu (menit) sistem M/M/c yang stabil. Hanya untuk menguji."""
    lam = arrival_rate / 60          # per menit
    mu = 1 / service_time            # per menit per staf
    a = lam / mu                     # beban tawaran
    rho = a / staff
    if rho >= 1:
        return None                  # tidak stabil, tidak ada rata-rata jangka panjang
    total = sum(a ** k / math.factorial(k) for k in range(staff))
    top = a ** staff / (math.factorial(staff) * (1 - rho))
    prob_wait = top / (total + top)  # peluang pelanggan harus menunggu
    return prob_wait / (staff * mu - lam)


def average_metric(name, staff, replications=30, hours=8):
    values = []
    for seed in range(replications):
        records = simulate_queue(40, 3, staff, hours, seed=seed)
        values.append(calculate_metrics(records, staff, hours)[name])
    return sum(values) / len(values)


# ---------- Tes-tes ----------
def test_reproducible():
    a = simulate_queue(40, 3, 3, 8, seed=42)
    b = simulate_queue(40, 3, 3, 8, seed=42)
    c = simulate_queue(40, 3, 3, 8, seed=43)
    assert a == b, "Seed sama harus menghasilkan hasil persis sama"
    assert a != c, "Seed berbeda harus menghasilkan hasil berbeda"


def test_record_logic():
    staff = 3
    records = simulate_queue(40, 3, staff, 8, seed=1)
    assert len(records) > 0
    for r in records:
        assert r["start"] >= r["arrival"], "Tidak boleh dilayani sebelum tiba"
        assert r["end"] > r["start"], "Layanan harus makan waktu"
    # Jumlah pelanggan yang dilayani bersamaan tidak boleh melebihi jumlah staf
    events = []
    for r in records:
        events.append((r["start"], +1))
        events.append((r["end"], -1))
    events.sort()
    current = 0
    for _, change in events:
        current += change
        assert current <= staff, "Staf yang sibuk melebihi jumlah staf!"


def test_same_day_for_every_scenario():
    day2 = simulate_queue(40, 3, 2, 8, seed=42)
    day4 = simulate_queue(40, 3, 4, 8, seed=42)
    assert len(day2) == len(day4), "Jumlah pelanggan harus sama di semua skenario"
    for r2, r4 in zip(day2, day4):
        assert r2["arrival"] == r4["arrival"], "Jam kedatangan harus sama"
        assert approx(r2["end"] - r2["start"], r4["end"] - r4["start"], 1e-6), \
            "Lama layanan tiap pelanggan harus sama"


def test_validation():
    for bad_args in [(40, 3, 0, 8), (0, 3, 2, 8), (40, 0, 2, 8), (40, 3, 2, 0), (40, 3, 1.5, 8)]:
        try:
            simulate_queue(*bad_args, seed=1)
        except ValueError:
            continue
        raise AssertionError(f"Seharusnya ValueError untuk input {bad_args}")


def test_metrics_by_hand():
    # 1 staf, buka 1 jam (60 menit). Semua angka bisa dihitung dengan tangan.
    records = [
        {"id": 1, "arrival": 0, "start": 0,  "end": 10},   # tunggu 0
        {"id": 2, "arrival": 5, "start": 10, "end": 20},   # tunggu 5
        {"id": 3, "arrival": 8, "start": 20, "end": 70},   # tunggu 12, selesai setelah tutup
    ]
    m = calculate_metrics(records, staff=1, operating_hours=1)
    assert m["customers_served"] == 3
    assert m["completed_by_closing"] == 2
    assert approx(m["throughput_per_hour"], 2.0)
    assert approx(m["avg_wait"], 17 / 3)                # (0 + 5 + 12) / 3
    assert approx(m["max_wait"], 12)
    assert approx(m["p90_wait"], 10.6)
    assert approx(m["avg_queue_length"], 17 / 60)       # (5 + 12) orang-menit / 60 menit
    assert m["max_queue_length"] == 2
    assert approx(m["utilization"], 1.0)                # staf sibuk penuh selama 60 menit
    assert approx(m["overtime_minutes"], 10)            # selesai menit 70, tutup menit 60


def test_more_staff_means_less_waiting():
    w2 = average_metric("avg_wait", 2)
    w3 = average_metric("avg_wait", 3)
    w4 = average_metric("avg_wait", 4)
    assert w2 > w3 > w4, f"Waktu tunggu harus turun saat staf bertambah: {w2:.2f}, {w3:.2f}, {w4:.2f}"


def test_two_staff_is_unstable():
    # 40 pelanggan/jam, 3 menit -> 2 staf persis di batas (utilisasi 100%): antrian menumpuk
    w2 = average_metric("avg_wait", 2)
    overtime = average_metric("overtime_minutes", 2)
    assert w2 > 5, f"Dengan 2 staf antrian seharusnya menumpuk, tapi rata-rata tunggu hanya {w2:.2f}"
    assert overtime > 5, "Dengan 2 staf seharusnya ada overtime"


def test_against_queueing_theory():
    for staff in (3, 4):
        theory = erlang_c_wait(40, 3, staff)
        simulated = average_metric("avg_wait", staff, replications=200)
        error = abs(simulated - theory) / theory
        print(f"    {staff} staf: teori {theory:.3f} menit, simulasi {simulated:.3f} menit, selisih {error * 100:.1f}%")
        assert error < 0.10, f"Simulasi menyimpang {error * 100:.1f}% dari teori"

        utilization = average_metric("utilization", staff, replications=200)
        expected = (40 / 60) * 3 / staff                 # lambda / (c * mu)
        assert abs(utilization - expected) < 0.03, \
            f"Utilisasi {utilization:.3f}, seharusnya sekitar {expected:.3f}"


# ---------- Penjalan tes sederhana ----------
if __name__ == "__main__":
    tests = [
        test_reproducible,
        test_record_logic,
        test_same_day_for_every_scenario,
        test_validation,
        test_metrics_by_hand,
        test_more_staff_means_less_waiting,
        test_two_staff_is_unstable,
        test_against_queueing_theory,
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