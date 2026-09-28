import json

from engine.ai_service import (
    AIServiceError,
    call_gemini,
    extract_json,
)

from engine.decision import recommend

from engine.scenarios import (
    build_scenarios,
    create_ai_scenario,
)

from engine.statistics import (
    run_scenarios_replicated,
    validate_against_theory,
)

from engine.validation import validate_inputs

from engine.scenario_generator import (
    generate_strategy_ideas,
)


# ============================================================
# REQUIRED FIELDS
# ============================================================

REQUIRED_FIELDS = [
    "arrival_rate",
    "service_time",
    "staff",
    "operating_hours",
    "staff_cost",
    "max_wait",
    "budget",
]


FIELD_LABELS = {
    "arrival_rate":
        "Customer arrival rate",

    "service_time":
        "Average service time",

    "staff":
        "Current staff / counters",

    "operating_hours":
        "Operating hours",

    "staff_cost":
        "Staff cost",

    "max_wait":
        "Maximum waiting time",

    "budget":
        "Maximum daily budget",
}


# ============================================================
# HELPERS
# ============================================================

def is_missing(value):
    return value is None or value == ""


def find_missing_fields(data):

    missing = []

    for field in REQUIRED_FIELDS:

        if is_missing(
            data.get(field)
        ):

            missing.append(
                {
                    "field": field,
                    "label": FIELD_LABELS[field],
                }
            )

    return missing


def clean_number(value):

    if value is None:
        return None

    try:
        return float(value)

    except (
        TypeError,
        ValueError,
    ):
        return None



# ============================================================
# GEMINI EXTRACTION
# ============================================================

def understand_description(
    description,
    business_type="",
):

    if not description:

        return {
            "business_type":
                business_type,

            "arrival_rate":
                None,

            "service_time":
                None,

            "staff":
                None,

            "operating_hours":
                None,

            "staff_cost":
                None,

            "max_wait":
                None,

            "budget":
                None,

            "ambiguities":
                [],

            "notes":
                [],
        }


    prompt = f"""

You are QueueWise AI.

Extract queue information from this description.

Business type:
{business_type}


Description:
{description}


Rules:
- Never invent numbers.
- Use null if information is missing.
- Return JSON only.


JSON format:

{{
"business_type":"",
"arrival_rate":null,
"service_time":null,
"staff":null,
"operating_hours":null,
"staff_cost":null,
"max_wait":null,
"budget":null,
"ambiguities":[],
"notes":[]
}}

"""


    response = call_gemini(
        prompt
    )


    data = extract_json(
        response
    )


    result = {

        "business_type":
            data.get(
                "business_type"
            )
            or business_type,


        "arrival_rate":
            clean_number(
                data.get(
                    "arrival_rate"
                )
            ),


        "service_time":
            clean_number(
                data.get(
                    "service_time"
                )
            ),


        "staff":
            clean_number(
                data.get(
                    "staff"
                )
            ),


        "operating_hours":
            clean_number(
                data.get(
                    "operating_hours"
                )
            ),


        "staff_cost":
            clean_number(
                data.get(
                    "staff_cost"
                )
            ),


        "max_wait":
            clean_number(
                data.get(
                    "max_wait"
                )
            ),


        "budget":
            clean_number(
                data.get(
                    "budget"
                )
            ),


        "ambiguities":
            data.get(
                "ambiguities",
                []
            ),


        "notes":
            data.get(
                "notes",
                []
            ),
    }


    if result["staff"] is not None:

        if float(
            result["staff"]
        ).is_integer():

            result["staff"] = int(
                result["staff"]
            )

        else:

            result["staff"] = None


    return result

# ============================================================
# MERGE AI INPUT
# ============================================================

def merge_missing_inputs(
    raw_data,
    extracted,
):

    merged = dict(raw_data)

    for field in REQUIRED_FIELDS:

        current = merged.get(field)

        ai_value = extracted.get(field)


        if (
            is_missing(current)
            and ai_value is not None
        ):

            merged[field] = ai_value


    return merged



# ============================================================
# AI GENERATED SCENARIO BUILDER
# ============================================================

def build_ai_scenarios(
    strategy_ideas,
):

    scenarios = []


    if not strategy_ideas:
        return scenarios


    strategies = (
        strategy_ideas.get(
            "strategies",
            []
        )
    )


    if not isinstance(
        strategies,
        list
    ):
        return scenarios


    for index, strategy in enumerate(
        strategies,
        start=1,
    ):

        try:

            scenario = create_ai_scenario(
                f"ai_{index}",
                strategy,
            )


            scenarios.append(
                scenario
            )


        except Exception:

            continue


    return scenarios



# ============================================================
# BUILD DIGEST FOR GEMINI
# ============================================================

def build_scenario_digest(
    results,
):

    digest = []


    for result in results:

        metrics = result.get(
            "metrics",
            {}
        )


        avg_wait = metrics.get(
            "avg_wait",
            {}
        )


        utilization = metrics.get(
            "utilization",
            {}
        )


        digest.append(
            {

                "name":
                    result.get(
                        "name"
                    ),


                "average_wait":
                    avg_wait.get(
                        "mean"
                    ),


                "utilization":
                    utilization.get(
                        "mean"
                    ),


                "cost":
                    result.get(
                        "cost",
                        {}
                    ).get(
                        "total"
                    ),


                "stable":
                    result.get(
                        "capacity",
                        {}
                    ).get(
                        "is_stable"
                    ),

            }
        )


    return digest



# ============================================================
# GEMINI EXPLANATION
# ============================================================

def explain_analysis(
    params,
    results,
    recommendation,
):

    evidence = {

        "inputs":
            params,

        "scenarios":
            build_scenario_digest(
                results
            ),

        "recommendation":
            recommendation,

    }


    prompt = """

Explain this QueueWise result.

Important:
- Do not create new numbers.
- Do not change recommendation.
- Explain in simple business language.
- Return JSON only.


Format:

{
"headline":"",
"summary":"",
"why":[],
"caution":"",
"next_action":""
}


Evidence:

""" + json.dumps(
        evidence,
        default=str,
        ensure_ascii=False,
    )


    response = call_gemini(
        prompt
    )


    return extract_json(
        response
    )
    
    # ============================================================
# MAIN QUEUEWISE AI AGENT
# ============================================================

def analyze_with_agent(
    raw_data,
    replications=30,
):

    raw_data = dict(
        raw_data
    )


    description = str(
        raw_data.get(
            "description",
            ""
        )
        or ""
    ).strip()


    business_type = str(
        raw_data.get(
            "business_type",
            ""
        )
        or ""
    ).strip()



    # ========================================================
    # 1. GENERATE AI STRATEGIES
    # ========================================================

    strategy_ideas = None


    if description:

        try:

            strategy_ideas = (
                generate_strategy_ideas(
                    description,
                    business_type,
                    raw_data.get(
                        "user_preference",
                        ""
                    ),
                )
            )

        except AIServiceError:

            strategy_ideas = None



    # ========================================================
    # 2. EXTRACT INPUT FROM DESCRIPTION
    # ========================================================

    extracted = None


    ai_input_warning = None


    if description:

        try:

            extracted = (
                understand_description(
                    description,
                    business_type,
                )
            )


            raw_data = (
                merge_missing_inputs(
                    raw_data,
                    extracted,
                )
            )


        except AIServiceError as error:

            ai_input_warning = str(
                error
            )


    else:

        extracted = (
            understand_description(
                "",
                business_type,
            )
        )



    # ========================================================
    # 3. CHECK REQUIRED DATA
    # ========================================================

    missing = (
        find_missing_fields(
            raw_data
        )
    )


    if missing:

        return {

            "status":
                "needs_input",


            "strategy_ideas":
                strategy_ideas,


            "agent":
                {

                    "extracted":
                        extracted,


                    "missing_fields":
                        missing,


                    "input_warning":
                        ai_input_warning,


                },


            "draft_inputs":
                raw_data,

        }



    # ========================================================
    # 4. VALIDATE INPUT
    # ========================================================

    try:

        params = validate_inputs(
            raw_data
        )


    except ValueError as error:

        return {

            "status":
                "validation_error",

            "error":
                str(error),

        }



    # ========================================================
    # 5. BUILD SCENARIOS
    # ========================================================

    scenarios = (
        build_scenarios(
            params
        )
    )


    ai_scenarios = (
        build_ai_scenarios(
            strategy_ideas
        )
    )


    scenarios.extend(
        ai_scenarios
    )



    # ========================================================
    # 6. RUN SIMULATION
    # ========================================================

    results = (
        run_scenarios_replicated(
            params,
            scenarios,
            replications=replications,
        )
    )



    # ========================================================
    # 7. THEORY VALIDATION
    # ========================================================

    theory_checks = []


    for result in results:

        check = (
            validate_against_theory(
                params,
                result,
                params["arrival_rate"],
                params["service_time"],
            )
        )


        if check is not None:

            theory_checks.append(
                {
                    "scenario":
                        result["name"],

                    **check,
                }
            )



    # ========================================================
    # 8. DECISION ENGINE
    # ========================================================

    recommendation = (
        recommend(
            params,
            results,
        )
    )



    # ========================================================
    # 9. AI EXPLANATION
    # ========================================================

    ai_explanation = None


    ai_explanation_warning = None


    try:

        ai_explanation = (
            explain_analysis(
                params,
                results,
                recommendation,
            )
        )


    except AIServiceError as error:

        ai_explanation_warning = str(
            error
        )



    # ========================================================
    # FINAL RESPONSE
    # ========================================================

    return {

        "status":
            "complete",


        "inputs":
            params,


        "replications":
            replications,


        "strategy_ideas":
            strategy_ideas,


        "ai_scenarios":
            [

                scenario["name"]

                for scenario in ai_scenarios

            ],


        "scenarios":
            results,


        "theory_validation":
            theory_checks,


        "recommendation":
            recommendation,


        "agent":
            {

                "extracted":
                    extracted,


                "explanation":
                    ai_explanation,


                "input_warning":
                    ai_input_warning,


                "explanation_warning":
                    ai_explanation_warning,

            },

    }