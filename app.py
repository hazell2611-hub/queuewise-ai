from dotenv import load_dotenv

load_dotenv()


from flask import (
    Flask,
    jsonify,
    render_template,
    request,
)


from engine.ai_agent import (
    analyze_with_agent,
    understand_description,
)

from engine.ai_service import (
    AIServiceError,
)

from engine.decision import (
    recommend,
)

from engine.scenarios import (
    build_scenarios,
    run_scenarios,
)

from engine.simulation import (
    calculate_metrics,
    simulate_queue,
)

from engine.statistics import (
    run_scenarios_replicated,
    validate_against_theory,
)

from engine.validation import (
    validate_inputs,
)


app = Flask(
    __name__
)


DEFAULT_SEED = 42
DEFAULT_REPLICATIONS = 30


# ============================================================
# PAGES
# ============================================================

@app.route("/")
def home():

    return render_template(
        "index.html",
        app_name="QueueWise AI",
    )


@app.route("/analyze")
def analyze():

    return render_template(
        "analyze.html",
        app_name="QueueWise AI",
    )


# ============================================================
# HEALTH
# ============================================================

@app.route("/api/health")
def health():

    return jsonify({
        "status":
            "ok",

        "app":
            "QueueWise AI",
    })


# ============================================================
# AI AGENT - UNDERSTAND DESCRIPTION
# ============================================================

@app.route(
    "/api/agent/extract",
    methods=["POST"],
)
def api_agent_extract():

    data = request.get_json(
        silent=True
    )


    if data is None:

        return jsonify({
            "error":
                "The request must contain JSON data."
        }), 400


    description = str(
        data.get(
            "description",
            ""
        )
        or ""
    ).strip()


    business_type = str(
        data.get(
            "business_type",
            ""
        )
        or ""
    ).strip()


    if not description:

        return jsonify({
            "error":
                "Please describe your queue first."
        }), 400


    try:

        extracted = (
            understand_description(
                description,
                business_type,
            )
        )


    except AIServiceError as error:

        return jsonify({
            "error":
                str(error)
        }), 503


    return jsonify({
        "status":
            "ok",

        "extracted":
            extracted,
    })


# ============================================================
# AI AGENT - COMPLETE WORKFLOW
# ============================================================

@app.route(
    "/api/agent/analyze",
    methods=["POST"],
)
def api_agent_analyze():

    data = request.get_json(
        silent=True
    )


    if data is None:

        return jsonify({
            "error":
                "The request must contain JSON data."
        }), 400


    # --------------------------------------------------------
    # REPLICATIONS
    # --------------------------------------------------------

    replications = data.get(
        "replications",
        DEFAULT_REPLICATIONS,
    )


    try:

        replications = int(
            replications
        )


    except (
        TypeError,
        ValueError,
    ):

        return jsonify({
            "error":
                "replications must be a whole number."
        }), 400


    if not (
        5
        <= replications
        <= 300
    ):

        return jsonify({
            "error":
                "replications must be between 5 and 300."
        }), 400


    # --------------------------------------------------------
    # RUN AGENT
    # --------------------------------------------------------

    try:

        result = (
            analyze_with_agent(
                data,
                replications=
                    replications,
            )
        )


    except ValueError as error:

        return jsonify({
            "error":
                str(error)
        }), 400


    except Exception as error:

        app.logger.exception(
            "QueueWise AI agent failed."
        )


        return jsonify({
            "error":
                (
                    "QueueWise could not complete the "
                    "analysis."
                ),

            "detail":
                str(error),
        }), 500


    return jsonify(
        result
    )


# ============================================================
# ORIGINAL API - SINGLE SIMULATION
# ============================================================

@app.route(
    "/api/simulate",
    methods=["POST"],
)
def api_simulate():

    data = request.get_json(
        silent=True
    )


    if data is None:

        return jsonify({
            "error":
                "The request must contain JSON data."
        }), 400


    try:

        params = validate_inputs(
            data
        )


    except ValueError as error:

        return jsonify({
            "error":
                str(error)
        }), 400


    records = simulate_queue(

        params[
            "arrival_rate"
        ],

        params[
            "service_time"
        ],

        params[
            "staff"
        ],

        params[
            "operating_hours"
        ],

        seed=
            DEFAULT_SEED,
    )


    metrics = calculate_metrics(

        records,

        params[
            "staff"
        ],

        params[
            "operating_hours"
        ],
    )


    capacity_per_hour = (

        params["staff"]
        * 60
        / params["service_time"]
    )


    load_ratio = (

        params["arrival_rate"]
        / capacity_per_hour
    )


    return jsonify({

        "inputs":
            params,

        "scenario": {
            "name":
                "Current staffing",

            "staff":
                params["staff"],
        },

        "seed":
            DEFAULT_SEED,

        "metrics":
            metrics,

        "capacity": {

            "capacity_per_hour":
                capacity_per_hour,

            "load_ratio":
                load_ratio,

            "is_stable":
                load_ratio < 1,
        },
    })


# ============================================================
# ORIGINAL API - SCENARIOS
# ============================================================

@app.route(
    "/api/scenarios",
    methods=["POST"],
)
def api_scenarios():

    data = request.get_json(
        silent=True
    )


    if data is None:

        return jsonify({
            "error":
                "The request must contain JSON data."
        }), 400


    try:

        params = validate_inputs(
            data
        )


        scenarios = (
            build_scenarios(
                params
            )
        )


        results = (
            run_scenarios(
                params,
                scenarios,
                seed=DEFAULT_SEED,
            )
        )


    except ValueError as error:

        return jsonify({
            "error":
                str(error)
        }), 400


    return jsonify({

        "inputs":
            params,

        "seed":
            DEFAULT_SEED,

        "scenarios":
            results,
    })


# ============================================================
# ORIGINAL API - STATISTICS
# ============================================================

@app.route(
    "/api/scenarios/statistics",
    methods=["POST"],
)
def api_scenarios_statistics():

    data = request.get_json(
        silent=True
    )


    if data is None:

        return jsonify({
            "error":
                "The request must contain JSON data."
        }), 400


    replications = data.get(
        "replications",
        DEFAULT_REPLICATIONS,
    )


    try:

        replications = int(
            replications
        )


    except (
        TypeError,
        ValueError,
    ):

        return jsonify({
            "error":
                "replications must be a whole number."
        }), 400


    if not (
        5
        <= replications
        <= 300
    ):

        return jsonify({
            "error":
                "replications must be between 5 and 300."
        }), 400


    try:

        params = validate_inputs(
            data
        )


        scenarios = (
            build_scenarios(
                params
            )
        )


        results = (
            run_scenarios_replicated(
                params,
                scenarios,
                replications=
                    replications,
            )
        )


    except ValueError as error:

        return jsonify({
            "error":
                str(error)
        }), 400


    theory_checks = []


    for result in results:

        check = (
            validate_against_theory(

                params,

                result,

                params[
                    "arrival_rate"
                ],

                params[
                    "service_time"
                ],
            )
        )


        if check is not None:

            theory_checks.append({

                "scenario":
                    result["name"],

                **check,
            })
            
            


    return jsonify({

        "inputs":
            params,

        "replications":
            replications,

        "scenarios":
            results,

        "theory_validation":
            theory_checks,
    })


# ============================================================
# ORIGINAL API - RECOMMENDATION
# ============================================================

@app.route(
    "/api/scenarios/recommend",
    methods=["POST"],
)
def api_scenarios_recommend():

    data = request.get_json(
        silent=True
    )


    if data is None:

        return jsonify({
            "error":
                "The request must contain JSON data."
        }), 400


    replications = data.get(
        "replications",
        DEFAULT_REPLICATIONS,
    )


    try:

        replications = int(
            replications
        )


    except (
        TypeError,
        ValueError,
    ):

        return jsonify({
            "error":
                "replications must be a whole number."
        }), 400


    if not (
        5
        <= replications
        <= 300
    ):

        return jsonify({
            "error":
                "replications must be between 5 and 300."
        }), 400


    try:

        params = validate_inputs(
            data
        )


        scenarios = (
            build_scenarios(
                params
            )
        )


        results = (
            run_scenarios_replicated(
                params,
                scenarios,
                replications=
                    replications,
            )
        )


    except ValueError as error:

        return jsonify({
            "error":
                str(error)
        }), 400


    theory_checks = []


    for result in results:

        check = (
            validate_against_theory(

                params,

                result,

                params[
                    "arrival_rate"
                ],

                params[
                    "service_time"
                ],
            )
        )


        if check is not None:

            theory_checks.append({

                "scenario":
                    result["name"],

                **check,
            })


    recommendation = (
        recommend(
            params,
            results,
        )
    )


    return jsonify({

        "inputs":
            params,

        "replications":
            replications,

        "scenarios":
            results,

        "theory_validation":
            theory_checks,

        "recommendation":
            recommendation,
    })


# ============================================================
# RUN
# ============================================================

if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=5000
    )