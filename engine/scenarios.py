from engine.simulation import calculate_metrics, simulate_queue
from engine.validation import read_number

MAX_STAFF = 50


# ============================================================
# SCENARIO BUILDER
# ============================================================

def make_scenario(
    scenario_id,
    name,
    staff_change=0,
    service_speedup=0.0,
    demand_shift=0.0,
    extra_cost=0.0,
):
    """
    Membuat satu definisi skenario.

    Nilai staff_change, service_speedup, dan demand_shift
    merupakan perubahan relatif terhadap kondisi dasar.
    """

    return {
        "id": scenario_id,
        "name": name,
        "staff_change": staff_change,
        "service_speedup": service_speedup,
        "demand_shift": demand_shift,
        "extra_cost": extra_cost,
    }


# ============================================================
# CUSTOM SCENARIO
# ============================================================

def clean_custom_scenario(spec, base_staff):
    """
    Memeriksa skenario buatan user.

    Melempar ValueError jika input tidak wajar.
    """

    if not isinstance(spec, dict):
        raise ValueError(
            "Each custom scenario must be an object."
        )

    staff_change = read_number(
        spec,
        "staff_change",
        -(base_staff - 1),
        MAX_STAFF - base_staff,
        "Staff change",
        default=0,
    )

    if staff_change != int(staff_change):
        raise ValueError(
            "Staff change must be a whole number."
        )

    speedup = read_number(
        spec,
        "speedup_percent",
        0,
        50,
        "Faster-service percentage",
        default=0,
    )

    shift = read_number(
        spec,
        "preorder_share_percent",
        0,
        60,
        "Pre-order percentage",
        default=0,
    )

    extra = read_number(
        spec,
        "extra_cost",
        0,
        1_000_000_000,
        "Extra daily cost",
        default=0,
    )

    name = (
        str(spec.get("name", ""))
        .strip()[:60]
        or "Custom scenario"
    )

    return make_scenario(
        "custom",
        name,
        int(staff_change),
        speedup / 100,
        shift / 100,
        extra,
    )


# ============================================================
# BUILD SCENARIOS
# ============================================================

def build_scenarios(params):
    """
    Membuat daftar skenario:

    1. Current staffing
    2. Add 1 staff
    3. Add 2 staff
    4. Faster service
    5. Pre-order
    6. Add 1 staff + faster service
    7. Custom scenarios
    """

    scenarios = []

    def add(scenario):

        effective_staff = (
            params["staff"]
            + scenario["staff_change"]
        )

        if 1 <= effective_staff <= MAX_STAFF:
            scenarios.append(scenario)

    speedup_pct = params["speedup_percent"]
    preorder_pct = params["preorder_share_percent"]

    speedup = speedup_pct / 100
    shift = preorder_pct / 100

    # --------------------------------------------------------
    # BASELINE
    # --------------------------------------------------------

    add(
        make_scenario(
            "current",
            "Current staffing",
        )
    )

    # --------------------------------------------------------
    # ADD STAFF
    # --------------------------------------------------------

    add(
        make_scenario(
            "add_1",
            "Add 1 staff",
            staff_change=1,
        )
    )

    add(
        make_scenario(
            "add_2",
            "Add 2 staff",
            staff_change=2,
        )
    )

    # --------------------------------------------------------
    # FASTER SERVICE
    # --------------------------------------------------------

    if speedup > 0:

        add(
            make_scenario(
                "faster",
                f"Faster service (-{speedup_pct:g}%)",
                service_speedup=speedup,
                extra_cost=params["speedup_cost"],
            )
        )

    # --------------------------------------------------------
    # PRE-ORDER
    # --------------------------------------------------------

    if shift > 0:

        add(
            make_scenario(
                "preorder",
                f"Pre-order ({preorder_pct:g}% skip the counter)",
                demand_shift=shift,
                extra_cost=params["preorder_cost"],
            )
        )

    # --------------------------------------------------------
    # COMBINATION
    # --------------------------------------------------------

    if speedup > 0:

        add(
            make_scenario(
                "add_1_faster",
                f"Add 1 staff + faster service (-{speedup_pct:g}%)",
                staff_change=1,
                service_speedup=speedup,
                extra_cost=params["speedup_cost"],
            )
        )

    # --------------------------------------------------------
    # CUSTOM
    # --------------------------------------------------------

    for number, spec in enumerate(
        params["custom_scenarios"],
        start=1,
    ):

        custom = clean_custom_scenario(
            spec,
            params["staff"],
        )

        custom["id"] = f"custom_{number}"

        scenarios.append(custom)

    return scenarios


# ============================================================
# APPLY SCENARIO
# ============================================================

def apply_scenario(params, scenario):
    """
    Menghitung parameter efektif setelah skenario diterapkan.

    Distribusi/model dasar tidak diubah oleh skenario.
    Yang berubah hanya:
    - jumlah staff
    - service time
    - arrival rate
    """

    staff = (
        params["staff"]
        + scenario["staff_change"]
    )

    if staff < 1 or staff > MAX_STAFF:

        raise ValueError(
            f"Scenario '{scenario['name']}' "
            f"leads to an invalid staff count ({staff})."
        )

    service_time = (
        params["service_time"]
        * (1 - scenario["service_speedup"])
    )

    arrival_rate = (
        params["arrival_rate"]
        * (1 - scenario["demand_shift"])
    )

    if service_time <= 0:
        raise ValueError(
            f"Scenario '{scenario['name']}' "
            "produces an invalid service time."
        )

    if arrival_rate <= 0:
        raise ValueError(
            f"Scenario '{scenario['name']}' "
            "produces an invalid arrival rate."
        )

    return {
        "staff": staff,
        "service_time": service_time,
        "arrival_rate": arrival_rate,
    }


# ============================================================
# COST
# ============================================================

def calculate_cost(params, staff, scenario):
    """
    Biaya per hari:

        staff × jam operasional × tarif per jam
        + biaya tambahan skenario
    """

    staff_cost = (
        staff
        * params["operating_hours"]
        * params["staff_cost"]
    )

    total = (
        staff_cost
        + scenario["extra_cost"]
    )

    return {
        "staff_cost": staff_cost,
        "extra_cost": scenario["extra_cost"],
        "total": total,
        "within_budget": total <= params["budget"],
    }


# ============================================================
# MODEL CONFIG
# ============================================================

def get_model_config(params):
    """
    Mengambil konfigurasi model simulasi.

    Jika frontend/backend belum mengirim konfigurasi,
    sistem tetap menggunakan M/M/c:

        arrival      = exponential
        service      = exponential

    Ini menjaga backward compatibility dengan
    project QueueWise versi sebelumnya.
    """

    model = params.get(
        "model_config",
        {}
    )

    arrival_distribution = model.get(
        "arrival_distribution",
        "exponential",
    )

    service_distribution = model.get(
        "service_distribution",
        "exponential",
    )

    arrival_params = model.get(
        "arrival_params",
        None,
    )

    service_params = model.get(
        "service_params",
        None,
    )

    return {
        "arrival_distribution":
            arrival_distribution,

        "service_distribution":
            service_distribution,

        "arrival_params":
            arrival_params,

        "service_params":
            service_params,
    }


# ============================================================
# RUN ONE SCENARIO
# ============================================================

def run_scenario(
    params,
    scenario,
    seed=42,
):
    """
    Menjalankan satu skenario:

        scenario
            ↓
        effective parameters
            ↓
        simulation
            ↓
        metrics
            ↓
        capacity / stability
            ↓
        cost
    """

    effective = apply_scenario(
        params,
        scenario,
    )

    model_config = get_model_config(
        params
    )

    # --------------------------------------------------------
    # SIMULATION
    # --------------------------------------------------------

    records = simulate_queue(

        arrival_rate=
            effective["arrival_rate"],

        service_time=
            effective["service_time"],

        staff=
            effective["staff"],

        operating_hours=
            params["operating_hours"],

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

    # --------------------------------------------------------
    # METRICS
    # --------------------------------------------------------

    metrics = calculate_metrics(

        records,

        effective["staff"],

        params["operating_hours"],
    )

    # --------------------------------------------------------
    # CAPACITY
    # --------------------------------------------------------

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
    # RESULT
    # --------------------------------------------------------

    return {

        "id":
            scenario["id"],

        "name":
            scenario["name"],

        "spec": {

            "staff_change":
                scenario["staff_change"],

            "service_speedup":
                scenario["service_speedup"],

            "demand_shift":
                scenario["demand_shift"],

            "extra_cost":
                scenario["extra_cost"],
        },

        "effective":
            effective,

        "model":
            model_config,

        "metrics":
            metrics,

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

def create_ai_scenario(
    scenario_id,
    strategy,
):
    """
    Mengubah strategi dari AI Agent
    menjadi format scenario QueueWise.
    """

    params = (
        strategy.get(
            "simulation_parameters",
            {}
        )
        or {}
    )


    return make_scenario(

        scenario_id,

        strategy.get(
            "name",
            "AI generated scenario"
        ),


        staff_change=int(
            params.get(
                "staff_change",
                0
            )
        ),


        service_speedup=float(
            params.get(
                "service_speedup",
                0
            )
        ),


        demand_shift=float(
            params.get(
                "demand_shift",
                0
            )
        ),


        extra_cost=float(
            params.get(
                "extra_cost",
                0
            )
        ),
    )


# ============================================================
# RUN ALL SCENARIOS
# ============================================================

def run_scenarios(
    params,
    scenarios,
    seed=42,
):
    """
    Menjalankan semua skenario.

    Semua skenario menggunakan seed yang sama
    agar perbandingan antar-skenario lebih adil.
    """

    return [
        run_scenario(
            params,
            scenario,
            seed=seed,
        )
        for scenario in scenarios
    ]

def create_ai_scenario(
    scenario_id,
    strategy,
):
    """
    Mengubah strategi dari AI Agent
    menjadi format scenario QueueWise.
    """

    params = (
        strategy.get(
            "simulation_parameters",
            {}
        )
        or {}
    )


    return make_scenario(

        scenario_id,

        strategy.get(
            "name",
            "AI generated scenario"
        ),


        staff_change=int(
            params.get(
                "staff_change",
                0
            )
        ),


        service_speedup=float(
            params.get(
                "service_speedup",
                0
            )
        ),


        demand_shift=float(
            params.get(
                "demand_shift",
                0
            )
        ),


        extra_cost=float(
            params.get(
                "extra_cost",
                0
            )
        ),
    )