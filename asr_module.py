import os
import argparse
import json

def do_asr(args):
    # Zmieniamy katalog na podany
    os.chdir(args.directory)
    print("Aktualny katalog:", os.getcwd())

    last_part = os.path.basename(args.directory)

    # Wyświetlamy nazwy plików
    print("Nazwa pliku audio ", args.audio_name)
    print("Ścieka do zapisu wyników działania skryptu: ", args.directory)

    audio_id = args.audio_name.rsplit('.', 1)[0]

    ROOT = os.getcwd()
    print('ROOT', ROOT)
    data_dir = os.path.join(ROOT,'auxiliary/data')
    print(data_dir)
    os.makedirs(data_dir, exist_ok=True)
    audio_path = os.path.join(ROOT, args.audio_name)

    json_file_path = os.path.join(ROOT, f"{args.audio_name}.json")

    print(f"JSON saved to: {json_file_path}")


if __name__ == '__main__':

    # Tworzymy parser argumentów
    parser = argparse.ArgumentParser(description="Skrypt do przetwarzania pliku audio")
    parser.add_argument("directory", type=str, help="Ścieżka do miejsca, w którym ma się uruchamiać skrypt")
    parser.add_argument("audio_name", type=str, help="Nazwa pliku audio")

    # Parsujemy argumenty
    args = parser.parse_args()

    do_asr(args)





