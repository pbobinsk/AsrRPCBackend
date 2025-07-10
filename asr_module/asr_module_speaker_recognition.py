import os
import argparse
import json

def main(args):
    print('asr_module_mock '+str(args))
    # Zmieniamy katalog na podany
    # os.chdir(args.directory)
    print('asr_module_mock '+"Aktualny katalog:", os.getcwd())

    last_part = os.path.basename(args.directory)

    # Wyświetlamy nazwy plików
    print('asr_module_mock '+"Nazwa pliku audio ", args.audio_name)
    print('asr_module_mock '+"Nazwa pliku audio lekarz", args.audio_name_doctor)
    print('asr_module_mock '+"Ścieka do zapisu wyników działania skryptu: ", args.directory)

    audio_id = args.audio_name.rsplit('.', 1)[0]
    audio_doctor_id = args.audio_name_doctor.rsplit('.', 1)[0]

    ROOT = os.getcwd()
    print('asr_module_mock '+'ROOT', ROOT)
    data_dir = os.path.join(ROOT,'auxiliary/data')
    print(data_dir)
    os.makedirs(data_dir, exist_ok=True)
    audio_path = os.path.join(ROOT, args.audio_name)
    audio_doctor_path = os.path.join(ROOT, args.audio_name_doctor)

    json_file_path = os.path.join(ROOT, f"{args.audio_name}.json")

    print('asr_module_mock '+f"JSON saved to: {json_file_path}")


if __name__ == "__main__":
    # Tworzymy parser argumentów
    parser = argparse.ArgumentParser(description="Skrypt do przetwarzania pliku audio")
    parser.add_argument("directory", type=str, help="Ścieżka do miejsca, w którym ma się uruchamiać skrypt")
    parser.add_argument("audio_name", type=str, help="Nazwa pliku audio - nagranie rozmowy lekarz-pacjęt")
    parser.add_argument("audio_name_doctor", type=str, help="Nazwa pliku audio - nagranie lekarza")

    # Parsujemy argumenty
    args = parser.parse_args()
    main(args)






