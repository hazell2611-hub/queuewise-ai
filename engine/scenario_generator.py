import json

from engine.ai_service import (
    call_gemini,
    extract_json,
    AIServiceError,
)


def generate_strategy_ideas(
    description,
    business_type="",
    user_preference=""
):
    """
    Gemini membuat ide strategi berdasarkan
    masalah bisnis user.

    IMPORTANT:
    Fungsi ini hanya menghasilkan IDE.
    Tidak menjalankan simulasi.
    Tidak menentukan pemenang.
    """

    system_instruction = """

You are QueueWise AI strategy planner.

Your job is to suggest possible operational
improvement strategies for a queue problem.

Rules:

1. Do not calculate waiting time.
2. Do not claim one strategy is best.
3. Do not invent simulation results.
4. Suggest realistic operational strategies.
5. Consider user preferences.
6. Return JSON only.

Possible strategy categories:

- staff
- process improvement
- technology
- demand management

"""


    prompt = f"""

Business type:
{business_type}


User situation:

{description}


User preference:

{user_preference}


Return JSON:

{{
    "problem_summary":"",
    "constraints":[],
    "strategies":[

        {{
            "name":"",
            "category":"",
            "reason":"",
            "simulation_parameters":{{}}
        }}

    ]
}}

"""


    response = call_gemini(
        prompt,
        system_instruction
    )


    return extract_json(
        response
    )