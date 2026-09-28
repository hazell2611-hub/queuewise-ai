"""
Decision engine.

Modul ini TIDAK menjalankan simulasi.
Modul ini hanya:

1. membaca hasil simulasi/statistik,
2. mengevaluasi setiap skenario,
3. memeriksa constraint user,
4. memilih skenario berdasarkan aturan yang eksplisit,
5. menghasilkan alasan yang dapat diaudit.

Prinsip akademik:

- Angka performa berasal dari engine simulasi/statistik.
- Modul ini tidak membuat angka simulasi baru.
- Data observasi/research case dibedakan dari parameter what-if.
- Skenario dengan asumsi tambahan diberi penanda.
- Keputusan tidak dibuat oleh AI.
"""

# ============================================================
# SCENARIO EVALUATION
# ============================================================

def evaluate_scenario(params, result):
    """
    Mengevaluasi satu skenario berdasarkan tiga constraint:

    1. Sistem stabil
    2. Average waiting time <= target
    3. Cost <= budget

    Semua angka performa berasal dari hasil simulasi.
    """

    avg_wait = result["metrics"]["avg_wait"]["mean"]

    meets_wait_target = (
        avg_wait <= params["max_wait"]
    )

    is_stable = (
        result["capacity"]["is_stable"]
    )

    within_budget = (
        result["cost"]["within_budget"]
    )

    feasible = (
        is_stable
        and meets_wait_target
        and within_budget
    )

    # --------------------------------------------------------
    # IDENTIFIKASI ASUMSI
    # --------------------------------------------------------

    spec = result.get(
        "spec",
        {}
    )

    uses_scenario_assumption = bool(
        spec.get(
            "service_speedup",
            0
        )
        or
        spec.get(
            "demand_shift",
            0
        )
    )

    # --------------------------------------------------------
    # MODEL TYPE
    # --------------------------------------------------------

    model = result.get(
        "model",
        params.get(
            "model_config",
            {}
        )
    )

    arrival_distribution = model.get(
        "arrival_distribution",
        "exponential"
    )

    service_distribution = model.get(
        "service_distribution",
        "exponential"
    )

    is_mm_c = (
        arrival_distribution == "exponential"
        and
        service_distribution == "exponential"
    )

    return {
        "id":
            result["id"],

        "name":
            result["name"],

        "is_stable":
            is_stable,

        "meets_wait_target":
            meets_wait_target,

        "within_budget":
            within_budget,

        "feasible":
            feasible,

        "avg_wait":
            avg_wait,

        "cost":
            result["cost"]["total"],

        "uses_scenario_assumption":
            uses_scenario_assumption,

        "arrival_distribution":
            arrival_distribution,

        "service_distribution":
            service_distribution,

        "is_mm_c":
            is_mm_c,
    }


# ============================================================
# MONEY FORMAT
# ============================================================

def format_money(value):
    """
    Format angka biaya ke format Rupiah sederhana.

    Contoh:
        150000 -> 150.000
    """

    return (
        f"{value:,.0f}"
        .replace(",", ".")
    )


# ============================================================
# REASON FOR FEASIBLE SCENARIO
# ============================================================

def build_reason(
    params,
    baseline_eval,
    chosen_eval,
    chosen_result,
):
    """
    Membuat alasan pemilihan skenario.

    Hanya menggunakan angka yang sudah dihitung
    oleh simulasi/statistik dan parameter user.
    """

    wait_from = (
        baseline_eval["avg_wait"]
    )

    wait_to = (
        chosen_eval["avg_wait"]
    )

    cost = (
        chosen_eval["cost"]
    )

    budget = (
        params["budget"]
    )

    max_wait = (
        params["max_wait"]
    )

    # --------------------------------------------------------
    # CURRENT STAFFING
    # --------------------------------------------------------

    if (
        chosen_eval["id"]
        ==
        baseline_eval["id"]
    ):

        sentence = (
            f"Current staffing keeps the "
            f"simulated average waiting time at "
            f"{wait_to:.2f} minutes, which is "
            f"within the "
            f"{max_wait:g}-minute target "
            f"and the daily budget of "
            f"{format_money(budget)}."
        )

    # --------------------------------------------------------
    # DIFFERENT SCENARIO
    # --------------------------------------------------------

    else:

        if wait_to < wait_from:

            direction = "reduces"

        elif wait_to > wait_from:

            direction = "increases"

        else:

            direction = "keeps"

        sentence = (
            f"{chosen_result['name']} "
            f"{direction} the simulated average "
            f"waiting time from "
            f"{wait_from:.2f} to "
            f"{wait_to:.2f} minutes. "
            f"The scenario remains within the "
            f"{max_wait:g}-minute target and "
            f"the daily budget of "
            f"{format_money(budget)} "
            f"(scenario cost: "
            f"{format_money(cost)}/day)."
        )

    # --------------------------------------------------------
    # WHAT-IF ASSUMPTION WARNING
    # --------------------------------------------------------

    if chosen_eval[
        "uses_scenario_assumption"
    ]:

        sentence += (
            " This scenario includes a "
            "what-if assumption "
            "(service-speed improvement "
            "and/or pre-order demand shift). "
            "Its performance should therefore "
            "be interpreted as a simulated "
            "scenario rather than an observed "
            "historical result."
        )

    return sentence


# ============================================================
# NO FEASIBLE SCENARIO
# ============================================================

def build_reason_no_feasible(
    params,
    baseline_eval,
    closest_eval,
    closest_result,
):
    """
    Digunakan jika tidak ada skenario yang
    memenuhi seluruh constraint.

    Tidak menyebut skenario sebagai 'optimal'.
    """

    reasons = []

    # --------------------------------------------------------
    # STABILITY
    # --------------------------------------------------------

    if not closest_eval[
        "is_stable"
    ]:

        reasons.append(
            "the queue remains unstable "
            "(service capacity is lower "
            "than the arrival demand)"
        )

    # --------------------------------------------------------
    # WAIT TARGET
    # --------------------------------------------------------

    if not closest_eval[
        "meets_wait_target"
    ]:

        reasons.append(
            f"the simulated average wait "
            f"({closest_eval['avg_wait']:.2f} min) "
            f"is above the "
            f"{params['max_wait']:g}-minute target"
        )

    # --------------------------------------------------------
    # BUDGET
    # --------------------------------------------------------

    if not closest_eval[
        "within_budget"
    ]:

        reasons.append(
            f"its daily cost "
            f"({format_money(closest_eval['cost'])}) "
            f"exceeds the budget "
            f"({format_money(params['budget'])})"
        )

    if reasons:

        reason_text = (
            " and ".join(reasons)
        )

    else:

        reason_text = (
            "it does not satisfy all "
            "decision constraints"
        )

    return (
        "None of the tested scenarios "
        "satisfy all three decision criteria "
        "at the same time. "
        f"The scenario shown for further "
        f"consideration is "
        f"{closest_result['name']}, "
        f"but {reason_text}. "
        "Additional scenarios, a different "
        "budget, or a different waiting-time "
        "target may be evaluated."
    )


# ============================================================
# MAIN DECISION FUNCTION
# ============================================================

def recommend(
    params,
    results,
):
    """
    Menghasilkan rekomendasi berbasis constraint.

    Aturan:

    1. Cari semua skenario feasible:
       - stable
       - average wait <= max_wait
       - cost <= budget

    2. Jika ada beberapa feasible:
       pilih biaya terendah.

       Jika biaya sama:
       pilih average waiting time terendah.

    3. Jika tidak ada feasible:
       pilih skenario dengan violation score
       terendah dan jelaskan constraint
       yang masih gagal.

    Catatan:
    Ini adalah aturan decision-support yang eksplisit,
    bukan prediksi AI.
    """

    # --------------------------------------------------------
    # SAFETY CHECK
    # --------------------------------------------------------

    if not results:

        raise ValueError(
            "No simulation results were provided."
        )

    # --------------------------------------------------------
    # EVALUATE ALL SCENARIOS
    # --------------------------------------------------------

    evaluations = [
        evaluate_scenario(
            params,
            result
        )
        for result in results
    ]

    # --------------------------------------------------------
    # MAP RESULT BY ID
    # --------------------------------------------------------

    by_id = {
        result["id"]: result
        for result in results
    }

    # --------------------------------------------------------
    # BASELINE
    # --------------------------------------------------------
    #
    # build_scenarios() menempatkan
    # Current staffing sebagai skenario pertama.
    #

    baseline_eval = evaluations[0]

    # --------------------------------------------------------
    # FEASIBLE SCENARIOS
    # --------------------------------------------------------

    feasible = [
        evaluation
        for evaluation in evaluations
        if evaluation["feasible"]
    ]

    # ========================================================
    # CASE A: FEASIBLE SCENARIOS EXIST
    # ========================================================

    if feasible:

        # ----------------------------------------------------
        # PRIMARY CRITERION:
        # LOWEST COST
        #
        # SECONDARY:
        # LOWEST AVERAGE WAIT
        # ----------------------------------------------------

        feasible_sorted = sorted(
            feasible,
            key=lambda evaluation: (
                evaluation["cost"],
                evaluation["avg_wait"],
            ),
        )

        chosen_eval = (
            feasible_sorted[0]
        )

        chosen_result = by_id[
            chosen_eval["id"]
        ]

        reason = build_reason(
            params,
            baseline_eval,
            chosen_eval,
            chosen_result,
        )

        status = "feasible"

    # ========================================================
    # CASE B: NO FEASIBLE SCENARIO
    # ========================================================

    else:

        def violation_score(
            evaluation
        ):
            """
            Menghitung tingkat pelanggaran
            constraint.

            Digunakan hanya untuk menentukan
            skenario yang paling dekat dengan
            seluruh constraint.

            Nilai ini BUKAN score kualitas
            bisnis.
            """

            # ----------------------------------------------
            # WAIT VIOLATION
            # ----------------------------------------------

            over_wait = (

                max(
                    0.0,

                    evaluation[
                        "avg_wait"
                    ]
                    -
                    params[
                        "max_wait"
                    ],
                )

                /

                max(
                    params[
                        "max_wait"
                    ],
                    1e-9,
                )
            )

            # ----------------------------------------------
            # BUDGET VIOLATION
            # ----------------------------------------------

            over_budget = (

                max(
                    0.0,

                    evaluation[
                        "cost"
                    ]
                    -
                    params[
                        "budget"
                    ],
                )

                /

                max(
                    params[
                        "budget"
                    ],
                    1e-9,
                )
            )

            # ----------------------------------------------
            # INSTABILITY
            # ----------------------------------------------

            unstable_penalty = (

                5.0

                if not evaluation[
                    "is_stable"
                ]

                else 0.0
            )

            return (
                unstable_penalty
                +
                over_wait
                +
                over_budget
            )

        # ----------------------------------------------------
        # SORT BY CONSTRAINT VIOLATION
        # ----------------------------------------------------

        evaluations_sorted = sorted(
            evaluations,
            key=violation_score,
        )

        chosen_eval = (
            evaluations_sorted[0]
        )

        chosen_result = by_id[
            chosen_eval["id"]
        ]

        reason = build_reason_no_feasible(
            params,
            baseline_eval,
            chosen_eval,
            chosen_result,
        )

        status = (
            "no_feasible_option"
        )

    # ========================================================
    # ALTERNATIVE:
    # LOWEST WAIT AMONG FEASIBLE
    # ========================================================

    feasible_sorted_by_wait = sorted(
        feasible,
        key=lambda evaluation:
            evaluation["avg_wait"]
    )

    fastest = (
        feasible_sorted_by_wait[0]
        if feasible_sorted_by_wait
        else None
    )

    alternatives = []

    if (
        fastest
        and
        fastest["id"]
        !=
        chosen_eval["id"]
    ):

        alternatives.append({

            "id":
                fastest["id"],

            "name":
                by_id[
                    fastest["id"]
                ]["name"],

            "role":
                "lowest_wait_feasible",

            "note": (
                "Lowest simulated average "
                "waiting time among feasible "
                "options: "
                f"{fastest['avg_wait']:.2f} "
                "minutes, with a daily cost "
                f"of "
                f"{format_money(fastest['cost'])}."
            ),
        })

    # ========================================================
    # RETURN DECISION SUPPORT RESULT
    # ========================================================

    return {

        "status":
            status,

        "recommended_id":
            chosen_eval["id"],

        "recommended_name":
            chosen_result["name"],

        "reason":
            reason,

        "evaluation":
            chosen_eval,

        "feasible_ids":
            [
                evaluation["id"]
                for evaluation in feasible
            ],

        "alternatives":
            alternatives,

        "criteria": {

            "max_wait":
                params["max_wait"],

            "budget":
                params["budget"],
        },

        "model": params.get(
            "model_config",
            {
                "arrival_distribution":
                    "exponential",

                "service_distribution":
                    "exponential",
            },
        ),

        "table":
            evaluations,
    }