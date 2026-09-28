import json
import os
import urllib.error
import urllib.request

MODEL = "gemini-3.5-flash-lite"
API_URL = f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL}:generateContent"


class AIServiceError(Exception):
    """Dilempar kalau AI tidak bisa dihubungi, kunci hilang, atau jawabannya tidak bisa dipakai."""


def get_api_key():
    key = os.environ.get("GEMINI_API_KEY", "").strip()
    if not key:
        raise AIServiceError(
            "GEMINI_API_KEY is not set. Create a .env file with GEMINI_API_KEY=... "
            "and make sure the app loads it with load_dotenv() before this is called."
        )
    return key


def call_gemini(prompt, system_instruction=None, timeout=20):
    """
    Mengirim SATU prompt ke Gemini dan mengembalikan teks jawabannya (str).
    Melempar AIServiceError untuk semua jenis kegagalan (kunci hilang, jaringan, format aneh),
    supaya pemanggil cukup menangani SATU jenis error.
    """
    api_key = get_api_key()

    body = {"contents": [{"role": "user", "parts": [{"text": prompt}]}]}
    if system_instruction:
        body["system_instruction"] = {"parts": [{"text": system_instruction}]}

    request = urllib.request.Request(
        f"{API_URL}?key={api_key}",
        data=json.dumps(body).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            data = json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as error:
        detail = error.read().decode("utf-8", errors="replace")[:300]
        raise AIServiceError(f"Gemini returned an error ({error.code}): {detail}") from error
    except urllib.error.URLError as error:
        raise AIServiceError(f"Could not reach Gemini: {error.reason}") from error
    except TimeoutError as error:
        raise AIServiceError("Gemini did not respond in time.") from error

    try:
        return data["candidates"][0]["content"]["parts"][0]["text"]
    except (KeyError, IndexError) as error:
        raise AIServiceError(f"Unexpected response shape from Gemini: {data}") from error


def extract_json(text):
    """
    Mengambil objek JSON dari teks jawaban AI, walau dibungkus ```json ... ``` atau ada kalimat
    pengantar. Melempar AIServiceError kalau tidak ditemukan JSON yang valid.
    """
    text = text.strip()
    if text.startswith("```"):
        text = text.strip("`")
        if text.startswith("json"):
            text = text[4:]
    text = text.strip()

    start = text.find("{")
    end = text.rfind("}")
    if start == -1 or end == -1 or end < start:
        raise AIServiceError(f"No JSON object found in AI response: {text[:200]}")

    try:
        return json.loads(text[start:end + 1])
    except json.JSONDecodeError as error:
        raise AIServiceError(f"AI response was not valid JSON: {error}") from error