import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from engine.ai_service import AIServiceError, extract_json, get_api_key


def test_extract_json_plain():
    assert extract_json('{"a": 1, "b": 2}') == {"a": 1, "b": 2}


def test_extract_json_with_code_fence():
    text = '```json\n{"arrival_rate": 40, "service_time": 3}\n```'
    assert extract_json(text) == {"arrival_rate": 40, "service_time": 3}


def test_extract_json_with_surrounding_text():
    text = 'Here is the result:\n{"staff": 2}\nHope that helps!'
    assert extract_json(text) == {"staff": 2}


def test_extract_json_rejects_garbage():
    try:
        extract_json("Sorry, I cannot help with that.")
    except AIServiceError:
        return
    raise AssertionError("Seharusnya AIServiceError untuk teks tanpa JSON")


def test_extract_json_rejects_broken_json():
    try:
        extract_json('{"arrival_rate": 40,}')  # koma nyasar, JSON tidak valid
    except AIServiceError:
        return
    raise AssertionError("Seharusnya AIServiceError untuk JSON yang rusak")


def test_missing_api_key_raises_clear_error():
    old_value = os.environ.pop("GEMINI_API_KEY", None)
    try:
        get_api_key()
        raise AssertionError("Seharusnya AIServiceError kalau GEMINI_API_KEY tidak ada")
    except AIServiceError as error:
        assert "GEMINI_API_KEY" in str(error)
    finally:
        if old_value is not None:
            os.environ["GEMINI_API_KEY"] = old_value


if __name__ == "__main__":
    tests = [
        test_extract_json_plain, test_extract_json_with_code_fence,
        test_extract_json_with_surrounding_text, test_extract_json_rejects_garbage,
        test_extract_json_rejects_broken_json, test_missing_api_key_raises_clear_error,
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