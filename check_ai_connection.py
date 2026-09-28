"""
Skrip manual untuk mengecek koneksi ke Gemini API.
BUKAN bagian dari test suite otomatis (tidak dipanggil app.py atau tes lain),
karena butuh API key asli dan koneksi internet.

Jalankan: python check_ai_connection.py
"""
from dotenv import load_dotenv

load_dotenv()

from engine.ai_service import AIServiceError, call_gemini

print("Mengirim prompt percobaan ke Gemini...")
try:
    reply = call_gemini("Reply with exactly the word: OK")
    print("Berhasil! Jawaban dari Gemini:")
    print(reply)
except AIServiceError as error:
    print("GAGAL:", error)