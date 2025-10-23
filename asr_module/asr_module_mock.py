import os
import sys  # Potrzebne do eleganckiego wyjścia z programu w razie błędu
import logging
import time  # Do symulacji opóźnień
import random # Do losowania
import shutil
from pathlib import Path

# Dobra praktyka: skonfiguruj logowanie na początku
logging.basicConfig(level=logging.DEBUG, format='%(levelname)s:%(name)s:%(message)s')
log = logging.getLogger('asr_module_mock')

class MockAsrError(Exception):
    """Niestandardowy wyjątek dla symulowanych błędów ASR."""
    pass

def main(args):
    """
    Główna funkcja makiety ASR z dodaną walidacją ścieżek i plików.
    """
    log.info(f"Otrzymane argumenty: {args}")

    # --- KROK 1: WALIDACJA GŁÓWNEGO KATALOGU ROBOCZEGO ---
    # Używamy ścieżki z argumentów, a nie os.getcwd()!
    # os.path.abspath() tworzy pełną, jednoznaczną ścieżkę.
    work_dir = os.path.abspath(args.directory)
    log.info(f"Ustawiono katalog roboczy na: {work_dir}")

    # Sprawdzamy, czy podany katalog w ogóle istnieje
    if not os.path.isdir(work_dir):
        log.error(f"Krytyczny błąd: Podany katalog roboczy nie istnieje! Ścieżka: {work_dir}")
        raise Exception(f"Krytyczny błąd: Podany katalog roboczy nie istnieje! Ścieżka: {work_dir}")
        # sys.exit(1)  # Zakończ program z kodem błędu

    # --- KROK 2: WALIDACJA PLIKÓW WEJŚCIOWYCH ---
    # Tworzymy pełne ścieżki do plików, łącząc katalog roboczy z nazwą pliku.
    audio_path = os.path.join(work_dir, args.audio_name)
    doctor_audio_path = os.path.join(work_dir, args.audio_name_doctor)

    log.info(f"Oczekiwana ścieżka do pliku audio: {audio_path}")
    log.info(f"Oczekiwana ścieżka do pliku audio lekarza: {doctor_audio_path}")

    # Sprawdzamy, czy plik audio istnieje
    if not os.path.isfile(audio_path):
        log.error(f"Krytyczny błąd: Plik audio nie został znaleziony! Ścieżka: {audio_path}")
        raise Exception(f"Krytyczny błąd: Plik audio nie został znaleziony! Ścieżka: {audio_path}")
        # sys.exit(1)

    # Sprawdzamy, czy plik audio lekarza istnieje
    if not os.path.isfile(doctor_audio_path):
        log.error(f"Krytyczny błąd: Plik audio lekarza nie został znaleziony! Ścieżka: {doctor_audio_path}")
        raise Exception(f"Krytyczny błąd: Plik audio lekarza nie został znaleziony! Ścieżka: {doctor_audio_path}")
        # sys.exit(1)

    # --- KROK 3: GŁÓWNA LOGIKA (teraz mamy pewność, że wszystko istnieje) ---
    log.info("Wszystkie pliki wejściowe i katalogi zostały zweryfikowane. Rozpoczynam przetwarzanie.")

    # Tworzymy katalog na dane pomocnicze (jeśli potrzebny)
    # os.makedirs z exist_ok=True jest bezpieczne i nie wymaga wcześniejszego sprawdzania.
    data_dir = os.path.join(work_dir, 'auxiliary', 'data')
    log.info(f"Zapewniam istnienie katalogu na dane pomocnicze: {data_dir}")
    os.makedirs(data_dir, exist_ok=True)

    # Tworzymy ścieżkę do zapisu pliku wynikowego .json
    json_file_path = os.path.join(work_dir, f"{args.audio_name}.json")

    # --- SYMULACJA OPÓŹNIENIA ---
    # Losujemy czas przetwarzania, np. od 5 do 20 sekund.
    processing_time = random.uniform(1.0, 2.0)
    log.info(f"Symuluję przetwarzanie ASR, które potrwa {processing_time:.2f} sekund...")
    
    # Używamy pętli z krótkimi przerwami, aby pokazać postęp
    # Dzielimy całkowity czas na mniejsze interwały, np. co 1 sekundę.
    start_time = time.time()
    while time.time() - start_time < processing_time:
        # Można tu logować postęp, jeśli to potrzebne, np. co kilka sekund.
        # print(".", end='', flush=True) # Prosty wskaźnik postępu w konsoli
        time.sleep(1) # Czekamy 1 sekundę
    
    log.info("Symulacja przetwarzania zakończona.")

    # --- SYMULACJA LOSOWEGO BŁĘDU ---
    # Ustawiamy prawdopodobieństwo wystąpienia błędu, np. 25% (0.25)
    error_probability = 0.015
    if random.random() < error_probability:
        log.warning("Symuluję losowy błąd podczas przetwarzania ASR!")
        # Rzucamy nasz niestandardowy wyjątek
        raise MockAsrError("Nie udało się przetworzyć pliku audio z powodu losowego błędu symulacji.")
        
    # --- LOGIKA SUKCESU (jeśli nie wystąpił błąd) ---

    json_file_path = os.path.join(work_dir, f"{args.audio_name}.json")
    csv_file_path = os.path.join(work_dir, f"{Path(args.audio_name).stem}.csv")
    json_gen_path = os.path.join(work_dir, "WR_S0001_Z05BO.wav.json")
    csv_gen_path = os.path.join(work_dir, "WR_S0001_Z05BO.csv")
    logging.debug('json_gen_path -> json_file_path: '+json_gen_path+' -> '+json_file_path)
    logging.debug('csv_gen_path -> csv_file_path: '+csv_gen_path+' -> '+csv_file_path)
    shutil.copy(json_gen_path,json_file_path)
    shutil.copy(csv_gen_path,csv_file_path)

    log.info("Przetwarzanie zakończyło się sukcesem (brak symulowanego błędu).")
    
    
    log.info(f"Plik wynikowy JSON został pomyślnie zapisany w: {json_file_path}")

    # except MockAsrError as e:
    #     # Obsługa naszego symulowanego błędu
    #     log.error(f"WYSTĄPIŁ SYMULOWANY BŁĄD: {e}")
    #     # Można tu zapisać plik .json z informacją o błędzie
    #     json_file_path = os.path.join(work_dir, f"{args.audio_name}.error.json")
    #     error_content = {"status": "error", "message": str(e)}
    #     with open(json_file_path, 'w', encoding='utf-8') as f:
    #         import json
    #         json.dump(error_content, f, ensure_ascii=False, indent=4)
    #     log.info(f"Informacja o błędzie zapisana w: {json_file_path}")
    #     sys.exit(1) # Zakończ z kodem błędu

    # except Exception as e:
    #     # Obsługa wszystkich innych, nieoczekiwanych błędów
    #     log.error(f"Wystąpił nieoczekiwany błąd systemowy: {e}", exc_info=True)
    #     sys.exit(1)

    log.info("Atrapa ASR zakończyła działanie.") 
    log.info("Przetwarzanie zakończone sukcesem.")
    log.info(f"Plik wynikowy JSON został pomyślnie zapisany w: {json_file_path}")

# Przykładowy sposób uruchomienia (do Twoich testów)
if __name__ == '__main__':
    # Makieta obiektu 'args'
    class MockArgs:
        def __init__(self, directory, audio_name, audio_name_doctor):
            self.directory = directory
            self.audio_name = audio_name
            self.audio_name_doctor = audio_name_doctor
        
        def __str__(self):
            return f"dir={self.directory}, audio={self.audio_name}, doctor_audio={self.audio_name_doctor}"

    mock_args = MockArgs(
        directory='audio_files', # Katalog, w którym są pliki
        audio_name='test.wav',
        audio_name_doctor='user_10.wav'
    )
    main(mock_args)
