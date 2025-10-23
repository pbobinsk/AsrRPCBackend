# batch_convert.py

import os
import sys
import json
import argparse
from io import BytesIO

from rpc_service.rpc_server import doASR4batch

def process_directory(directory_path: str, doctor_path: str):
    """
    Przeszukuje podany katalog, znajduje pliki *.wav dla audio i szuka w innym dla lekarza.
    I potem robi ASR
    """
    print(f"Przeszukuję katalog: {directory_path}\n")
    converted_count = 0
    
    # Przechodzimy przez wszystkie pliki w podanym katalogu
    for filename in os.listdir(directory_path):
        # Sprawdzamy, czy nazwa pliku kończy się na pożądane rozszerzenie
        if filename.endswith("wizyta.wav"):
            input_wav_path = os.path.join(directory_path, filename)
            doctor_filename = filename.replace('_wizyta.wav', '_lekarz.wav')
            input_doctor_path = os.path.join(doctor_path, doctor_filename)
            # Tworzymy nową nazwę pliku, po prostu dodając .pdf na końcu
            # output_pdf_path = input_json_path + ".wav.hist.json"
            # output_pdf_path_ollama = input_json_path + "_ollama.wav.hist.json"
            
            
            try:
                
                print(f"Pretwarzam plik {input_wav_path} i {input_doctor_path}")
                # data = doNLPreal(input_json_path,'gpt-3.5-turbo')
                # with open(output_pdf_path, "w", encoding='utf-8') as f:

                doASR4batch(directory_path, filename, doctor_filename)

                converted_count += 1

            except Exception as e:
                print(f"--> BŁĄD podczas przetwarzania pliku {filename}: {e}")
            
            print("-" * 20)

    print(f"\nZakończono. Przekonwertowano {converted_count} plików.")


def main():
    """
    Główna funkcja skryptu, obsługuje argumenty z linii komend.
    """
    # Używamy argparse do profesjonalnej obsługi argumentów
    parser = argparse.ArgumentParser(description="Robię ASR dla plików *.wav.")
    parser.add_argument("directory", help="Ścieżka do katalogu z plikami wav wywiadu.")
    parser.add_argument("doctor_directory", help="Ścieżka do katalogu z plikami wav lekarzy.")
    
    args = parser.parse_args()
    
    directory_path = args.directory
    doctor_directory_path = args.doctor_directory
    
    if not os.path.isdir(directory_path):
        print(f"BŁĄD: Podana ścieżka '{directory_path}' nie jest prawidłowym katalogiem.")
        sys.exit(1)
    if not os.path.isdir(doctor_directory_path):
        print(f"BŁĄD: Podana ścieżka '{directory_path}' nie jest prawidłowym katalogiem.")
        sys.exit(1)
        
    process_directory(directory_path, doctor_directory_path)


if __name__ == '__main__':
    main()
