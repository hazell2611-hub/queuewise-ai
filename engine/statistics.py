import math

import numpy as np

from engine.scenarios import (
    apply_scenario,
    calculate_cost,
    get_model_config,
)

from engine.simulation import (
    calculate_metrics,
    simulate_queue,
)


# ============================================================
# T-VALUE TABLE
# ============================================================

_T_TABLE = {
    1: 12.706,
    2: 4.303,
    3: 3.182,
    4: 2.776,
    5: 2.571,
    6: 2.447,
    7: 2.365,
    8: 2.306,
    9: 2.262,
    10: 2.228,
    15: 2.131,
    20: 2.086,
    25: 2.060,
    30: 2.042,
}


# ============================================================
# T VALUE
# ============================================================

def t_value(df):
    """
    Nilai-t 95% untuk derajat bebas df.

    Untuk df >= 30 digunakan pendekatan
    normal 1.96.
    """

    if df >= 30:
        return 1.96

    keys = sorted(
        _T_TABLE
    )

    for k in keys:

        if df <= k:
            return _T_TABLE[k]

    return 1.96


# ============================================================
# CONFIDENCE INTERVAL
# ============================================================

def mean_ci(
    values,
    confidence=0.95,
):
    """
    Menghitung:

    - mean
    - standard deviation
    - half-width
    - lower CI
    - upper CI
    - number of replications

    berdasarkan hasil satu metrik
    dari beberapa replikasi.
    """

    values = np.array(
        values,
        dtype=float,
    )

    n = len(values)

    if n == 0:

        raise ValueError(
            "Cannot calculate CI from empty values."
        )

    mean = float(
        values.mean()
    )

    if n < 2:

        return {
            "mean": mean,
            "std": 0.0,
            "half_width": 0.0,
            "low": mean,
            "high": mean,
            "n": n,
        }

    std = float(
        values.std(
            ddof=1
        )
    )

    half_width = (
        t_value(n - 1)
        * std
        / math.sqrt(n)
    )

    return {

        "mean":
            mean,

        "std":
            std,

        "half_width":
            half_width,

        "low":
            mean - half_width,

        "high":
            mean + half_width,

        "n":
            n,
    }


# ============================================================
# RUN ONE SCENARIO - REPLICATED
# ============================================================

def run_scenario_replicated(
    params,
    scenario,
    replications=30,
    base_seed=1000,
):
    """
    Menjalankan satu skenario berkali-kali.

    Setiap replikasi menggunakan seed berbeda.

    Hasil setiap metrik diringkas menjadi:

        {
            mean,
            std,
            half_width,
            low,
            high,
            n
        }

    Biaya tidak acak sehingga dihitung satu kali.
    """

    effective = apply_scenario(
        params,
        scenario,
    )

    # --------------------------------------------------------
    # MODEL CONFIG
    # --------------------------------------------------------

    model_config = get_model_config(
        params
    )

    # --------------------------------------------------------
    # TEMPORARY METRIC STORAGE
    # --------------------------------------------------------

    per_metric = {}

    # --------------------------------------------------------
    # REPLICATION LOOP
    # --------------------------------------------------------

    for seed_offset in range(
        replications
    ):

        seed = (
            base_seed
            + seed_offset
        )

        # ----------------------------------------------
        # SIMULATION
        # ----------------------------------------------

        records = simulate_queue(

            effective[
                "arrival_rate"
            ],

            effective[
                "service_time"
            ],

            effective[
                "staff"
            ],

            params[
                "operating_hours"
            ],

            seed=seed,

            arrival_distribution=
                model_config[
                    "arrival_distribution"
                ],

            service_distribution=
                model_config[
                    "service_distribution"
                ],

            arrival_params=
                model_config[
                    "arrival_params"
                ],

            service_params=
                model_config[
                    "service_params"
                ],
        )

        # ----------------------------------------------
        # METRICS
        # ----------------------------------------------

        metrics = calculate_metrics(

            records,

            effective[
                "staff"
            ],

            params[
                "operating_hours"
            ],
        )

        # ----------------------------------------------
        # STORE METRICS
        # ----------------------------------------------

        for key, value in metrics.items():

            per_metric.setdefault(
                key,
                [],
            ).append(value)

    # --------------------------------------------------------
    # SUMMARY
    # --------------------------------------------------------

    summary = {
        key: mean_ci(values)
        for key, values
        in per_metric.items()
    }

    # --------------------------------------------------------
    # CAPACITY
    # --------------------------------------------------------
    #
    # NOTE:
    # Capacity calculation menggunakan
    # average service_time sebagai indikator
    # kapasitas teoritis sederhana.
    #
    # Untuk non-exponential research case,
    # ini tetap merupakan approximation/summary,
    # bukan distribusi capacity lengkap.
    #

    capacity_per_hour = (
        effective["staff"]
        * 60
        / effective["service_time"]
    )

    load_ratio = (
        effective["arrival_rate"]
        / capacity_per_hour
    )

    # --------------------------------------------------------
    # RETURN
    # --------------------------------------------------------

    return {

        "id":
            scenario["id"],

        "name":
            scenario["name"],

        "spec": {

            "staff_change":
                scenario[
                    "staff_change"
                ],

            "service_speedup":
                scenario[
                    "service_speedup"
                ],

            "demand_shift":
                scenario[
                    "demand_shift"
                ],

            "extra_cost":
                scenario[
                    "extra_cost"
                ],
        },

        "effective":
            effective,

        "model":
            model_config,

        "replications":
            replications,

        "metrics":
            summary,

        "cost":
            calculate_cost(
                params,
                effective["staff"],
                scenario,
            ),

        "capacity": {

            "capacity_per_hour":
                capacity_per_hour,

            "load_ratio":
                load_ratio,

            "is_stable":
                load_ratio < 1,
        },
    }


# ============================================================
# RUN ALL SCENARIOS - REPLICATED
# ============================================================

def run_scenarios_replicated(
    params,
    scenarios,
    replications=30,
    base_seed=1000,
):
    """
    Menjalankan seluruh skenario
    dengan jumlah replikasi yang sama.
    """

    return [

        run_scenario_replicated(
            params,
            scenario,
            replications,
            base_seed,
        )

        for scenario in scenarios
    ]


# ============================================================
# ERLANG C
# ============================================================

def erlang_c_wait(
    arrival_rate,
    service_time,
    staff,
):
    """
    Expected waiting time in queue
    untuk model M/M/c.

    HANYA valid untuk:
        Poisson arrivals
        Exponential service
        c servers
        rho < 1

    Return:
        waiting time dalam MENIT.

    Return None jika sistem tidak stabil.
    """

    lam = (
        arrival_rate / 60
    )

    mu = (
        1 / service_time
    )

    a = (
        lam / mu
    )

    rho = (
        a / staff
    )

    if rho >= 1:
        return None

    total = sum(
        a ** k
        / math.factorial(k)
        for k in range(staff)
    )

    top = (
        a ** staff
        /
        (
            math.factorial(staff)
            * (1 - rho)
        )
    )

    prob_wait = (
        top
        /
        (total + top)
    )

    wait_minutes = (
        prob_wait
        /
        (staff * mu - lam)
    )

    return wait_minutes


# ============================================================
# THEORY VALIDATION
# ============================================================

def validate_against_theory(
    params,
    scenario_result,
    arrival_rate,
    service_time,
):
    """
    Membandingkan simulasi dengan Erlang C.

    Validasi HANYA dilakukan apabila:

    1. Arrival distribution = exponential
    2. Service distribution = exponential
    3. Tidak ada service speedup
    4. Tidak ada demand shift
    5. Sistem stabil

    Karena Erlang C adalah model M/M/c.
    """

    # --------------------------------------------------------
    # MODEL CHECK
    # --------------------------------------------------------

    model = scenario_result.get(
        "model",
        params.get(
            "model_config",
            {},
        ),
    )

    arrival_distribution = model.get(
        "arrival_distribution",
        "exponential",
    )

    service_distribution = model.get(
        "service_distribution",
        "exponential",
    )

    # --------------------------------------------------------
    # NON M/M/C -> SKIP
    # --------------------------------------------------------

    if arrival_distribution != "exponential":

        return None

    if service_distribution != "exponential":

        return None

    # --------------------------------------------------------
    # SCENARIO TRANSFORMATION -> SKIP
    # --------------------------------------------------------

    if scenario_result[
        "spec"
    ][
        "service_speedup"
    ]:

        return None

    if scenario_result[
        "spec"
    ][
        "demand_shift"
    ]:

        return None

    # --------------------------------------------------------
    # STABILITY CHECK
    # --------------------------------------------------------

    if not scenario_result[
        "capacity"
    ][
        "is_stable"
    ]:

        return None

    # --------------------------------------------------------
    # EFFECTIVE PARAMETERS
    # --------------------------------------------------------

    staff = scenario_result[
        "effective"
    ][
        "staff"
    ]

    effective_arrival_rate = (
        scenario_result[
            "effective"
        ][
            "arrival_rate"
        ]
    )

    effective_service_time = (
        scenario_result[
            "effective"
        ][
            "service_time"
        ]
    )

    # --------------------------------------------------------
    # ERLANG C
    # --------------------------------------------------------

    theory_wait = erlang_c_wait(

        effective_arrival_rate,

        effective_service_time,

        staff,
    )

    if theory_wait is None:
        return None

    # --------------------------------------------------------
    # SIMULATION RESULT
    # --------------------------------------------------------

    sim = scenario_result[
        "metrics"
    ][
        "avg_wait"
    ]

    # --------------------------------------------------------
    # ERROR PERCENT
    # --------------------------------------------------------

    if theory_wait == 0:

        error_pct = 0.0

    else:

        error_pct = (
            abs(
                sim["mean"]
                - theory_wait
            )
            / theory_wait
            * 100
        )

    # --------------------------------------------------------
    # CI CHECK
    # --------------------------------------------------------

    within_ci = (

        sim["low"]
        - 1e-9

        <= theory_wait

        <=

        sim["high"]
        + 1e-9
    )

    # --------------------------------------------------------
    # RETURN
    # --------------------------------------------------------

    return {

        "theory_wait":
            theory_wait,

        "simulated_wait":
            sim["mean"],

        "half_width":
            sim["half_width"],

        "error_percent":
            error_pct,

        "within_tolerance":
            within_ci,
    }