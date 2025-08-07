"""
Ten plik działa jak fabryka dla modułu ASR.

Automatycznie sprawdza, czy biblioteka 'whisper' jest dostępna.
Jeśli tak, udostępnia funkcję `main` z prawdziwego modułu.
W przeciwnym razie, udostępnia funkcję `main` z modułu-atrapy.
"""

# Zmienna, która będzie przechowywać informację, czy używamy prawdziwej implementacji
_using_real_asr = False

try:
    # Krok 1: Spróbuj zaimportować bibliotekę 'whisper'.
    # To jest test, który decyduje o wszystkim.
    import whisper
    
    # Krok 2: Jeśli import się powiódł, zaimportuj funkcję `main`
    # z Twojego prawdziwego modułu i udostępnij ją pod nazwą `main`.
    print("INFO: Biblioteka 'whisper' znaleziona. Używam prawdziwego modułu ASR.")
    from .asr_module_speaker_recognition import main
    _using_real_asr = True

except ImportError:
    # Krok 3: Jeśli import się nie powiódł, zaimportuj funkcję `main`
    # z modułu-atrapy i udostępnij ją pod tą samą nazwą `main`.
    print("UWAGA: Biblioteka 'whisper' nie jest zainstalowana. Używam modułu-atrapy ASR.")
    from .asr_module_mock import main
    _using_real_asr = False

def is_real_asr_in_use():
    """Funkcja pomocnicza, która pozwala sprawdzić, która wersja jest aktywna."""
    return _using_real_asr