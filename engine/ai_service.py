import json
import os
import random
import time
import urllib.error
import urllib.request

MODEL = "gemini-3.5-flash-lite"
API_URL = (
    f"https://generativelanguage.googleapis.com/"
    f"v1beta/models/{MODEL}:generateContent"
)


class AIServiceError(Exception):
    pass


def get_api_key():
    key = os.environ.get("GEMINI_API_KEY", "").strip()

    if not key:
        raise AIServiceError(
            "GEMINI_API_KEY is not configured."
        )

    return key


def call_gemini(
    prompt,
    system_instruction=None,
    timeout=30,
    max_retries=4,
):
    api_key = get_api_key()

    body = {
        "contents": [
            {
                "role": "user",
                "parts": [
                    {
                        "text": prompt
                    }
                ],
            }
        ]
    }

    if system_instruction:
        body["system_instruction"] = {
            "parts": [
                {
                    "text": system_instruction
                }
            ]
        }

    request_data = json.dumps(body).encode("utf-8")

    last_error = None

    for attempt in range(max_retries):
        request = urllib.request.Request(
            f"{API_URL}?key={api_key}",
            data=request_data,
            headers={
                "Content-Type": "application/json"
            },
            method="POST",
        )

        try:
            with urllib.request.urlopen(
                request,
                timeout=timeout,
            ) as response:

                data = json.loads(
                    response.read().decode("utf-8")
                )

            try:
                return data["candidates"][0]["content"]["parts"][0]["text"]

            except (KeyError, IndexError) as error:
                raise AIServiceError(
                    "Gemini returned an unexpected response."
                ) from error

        except urllib.error.HTTPError as error:
            detail = error.read().decode(
                "utf-8",
                errors="replace",
            )

            last_error = error

            # Retry only transient errors.
            if error.code in (408, 429, 500, 502, 503, 504):
                if attempt < max_retries - 1:
                    delay = (2 ** attempt) + random.uniform(0, 1)
                    time.sleep(delay)
                    continue

            raise AIServiceError(
                f"Gemini request failed ({error.code})."
            ) from error

        except (
            urllib.error.URLError,
            TimeoutError,
        ) as error:

            last_error = error

            if attempt < max_retries - 1:
                delay = (2 ** attempt) + random.uniform(0, 1)
                time.sleep(delay)
                continue

            raise AIServiceError(
                "Gemini is temporarily unavailable."
            ) from error

    raise AIServiceError(
        "Gemini is temporarily unavailable."
    ) from last_error


def extract_json(text):
    text = text.strip()

    if text.startswith("```"):
        text = text.strip("`")

        if text.startswith("json"):
            text = text[4:]

    text = text.strip()

    start = text.find("{")
    end = text.rfind("}")

    if start == -1 or end == -1 or end < start:
        raise AIServiceError(
            "No JSON object found in the AI response."
        )

    try:
        return json.loads(
            text[start:end + 1]
        )

    except json.JSONDecodeError as error:
        raise AIServiceError(
            "Gemini returned invalid JSON."
        ) from error