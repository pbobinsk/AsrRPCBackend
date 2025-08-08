import os
import argparse
import wget
import pandas as pd
import json
from pydub import AudioSegment
from nemo.collections.asr.parts.utils.speaker_utils import rttm_to_labels, labels_to_pyannote_object
from omegaconf import OmegaConf
from nemo.collections.asr.models import ClusteringDiarizer
import nemo.collections.asr as nemo_asr
from nemo.collections.asr.models.msdd_models import NeuralDiarizer
import whisper

def main(args):
    # Zmieniamy katalog na podany
    os.chdir(args.directory)
    print("Aktualny katalog:", os.getcwd())

    last_part = os.path.basename(args.directory)

    # Wyświetlamy nazwy plików
    print("Nazwa pliku audio ", args.audio_name)
    print("Nazwa pliku audio lekarz", args.audio_name_doctor)
    print("Ścieka do zapisu wyników działania skryptu: ", args.directory)

    audio_id = args.audio_name.rsplit('.', 1)[0]
    audio_doctor_id = args.audio_name_doctor.rsplit('.', 1)[0]

    ROOT = os.getcwd()
    print('ROOT', ROOT)
    data_dir = os.path.join(ROOT,'auxiliary/data')
    print(data_dir)
    os.makedirs(data_dir, exist_ok=True)
    audio_path = os.path.join(ROOT, args.audio_name)
    audio_doctor_path = os.path.join(ROOT, args.audio_name_doctor)


    # Tworzenie manifestu do diaryzacji mówców.
    # {'audio_filepath': /path/to/audio_file, 'offset': 0, 'duration':None, 'label': 'infer', 'text': '-',
    # 'num_speakers': None, 'rttm_filepath': /path/to/rttm/file, 'uem_filepath'='/path/to/uem/filepath'}

    meta = {
        'audio_filepath': audio_path,
        'offset': 0,
        'duration':None,
        'label': 'infer',
        'text': '-',
        'num_speakers': 2,
        'rttm_filepath': None,
        'uem_filepath' : None
    }
    with open('auxiliary/data/input_manifest.json','w') as fp:
        json.dump(meta,fp)
        fp.write('\n')

    # !cat auxiliary/data/input_manifest.json

    output_dir = os.path.join(ROOT, 'auxiliary/oracle_vad')
    os.makedirs(output_dir,exist_ok=True)

    MODEL_CONFIG = os.path.join(data_dir,'diar_infer_telephonic.yaml')
    if not os.path.exists(MODEL_CONFIG):
        config_url = "https://raw.githubusercontent.com/NVIDIA/NeMo/main/examples/speaker_tasks/diarization/conf/inference/diar_infer_telephonic.yaml"
        MODEL_CONFIG = wget.download(config_url,data_dir)

    config = OmegaConf.load(MODEL_CONFIG)
    print(OmegaConf.to_yaml(config))

    config.diarizer.manifest_filepath = 'auxiliary/data/input_manifest.json'
    config.diarizer.out_dir = output_dir # Katalog do przechowywania plików pośrednich i wyników predykcji
    pretrained_speaker_model = 'titanet_large'
    config.diarizer.speaker_embeddings.model_path = pretrained_speaker_model
    config.diarizer.speaker_embeddings.parameters.window_length_in_sec = [1.5,1.25,1.0,0.75,0.5]
    config.diarizer.speaker_embeddings.parameters.shift_length_in_sec = [0.75,0.625,0.5,0.375,0.1]
    config.diarizer.speaker_embeddings.parameters.multiscale_weights= [1,1,1,1,1]
    config.diarizer.oracle_vad = False # ----> ORACLE VAD
    config.diarizer.clustering.parameters.oracle_num_speakers = False
                
    oracle_vad_clusdiar_model = ClusteringDiarizer(cfg=config)
    # And lets diarize
    oracle_vad_clusdiar_model.diarize()
    save_rttm = os.path.join(ROOT, f'{output_dir}/pred_rttms/{audio_id}.rttm')
    # !cat {save_rttm}
    config.diarizer.msdd_model.model_path = 'diar_msdd_telephonic' # Telephonic speaker diarization model
    config.diarizer.msdd_model.parameters.sigmoid_threshold = [0.7, 1.0] # Evaluate with T=0.7 and T=1.0

    oracle_vad_msdd_model = NeuralDiarizer(cfg=config)
    oracle_vad_msdd_model.diarize()
    # !cat {save_rttm}

    # Nazwy kolumn na podstawie struktury RTTM (dostosuj w razie potrzeby)
    columns = ['speaker', 'file_ID', 'channel', 'start', 'duration', 'orthography', 'speaker_type', 'turn', 'confidence', 'signal_quality']

    # Wczytanie danych do listy i przekształcenie do DataFrame
    data = []
    with open(save_rttm, 'r') as rttm_file:
        for line in rttm_file:
            fields = line.strip().split()  # Podział linii na podstawie spacji
            data.append(fields)

    # Utworzenie DataFrame
    df = pd.DataFrame(data, columns=columns)

    df = df.drop(['orthography', 'speaker_type', 'confidence', 'signal_quality'], axis=1)
    df['stop'] = df['start'].astype(float) + df['duration'].astype(float)

    # Konwersja kolumny 'duration' na float
    df['duration'] = df['duration'].astype(float)
    df['start'] = df['start'].astype(float)
    df['stop'] = df['stop'].astype(float)

    # Znalezienie grup ciągłych powtarzających się wartości w kolumnie 'turn'
    df['group'] = (df['turn'] != df['turn'].shift()).cumsum()

    # Agregacja danych: najmniejszy start, maksymalny stop dla każdej grupy
    agg_df = df.groupby(['group', 'turn']).agg(
        start=('start', 'min'),
        stop=('stop', 'max')
    ).reset_index()

    # Obliczenie nowego duration jako stop - start
    agg_df['duration'] = agg_df['stop'] - agg_df['start']

    # Przywrócenie kolumny 'turn' do końcowego DataFrame
    result = pd.DataFrame({
        'speaker': df['speaker'].iloc[0],
        'file_ID': df['file_ID'].iloc[0],  # Przyjmujemy stałą wartość file_ID
        'channel': df['channel'].iloc[0],  # Przyjmujemy stałą wartość channel
        'start': agg_df['start'],
        'duration': agg_df['duration'],
        'turn': agg_df['turn'],
        'stop': agg_df['stop']
    })

    # Lista do przechowywania ścieżek plików
    file_paths = []

    # Create the output directory if it doesn't exist
    audio_save_dir = f"auxiliary/audio_per_turn/{result['file_ID'].iloc[0]}"
    os.makedirs(audio_save_dir, exist_ok=True)

    audio = AudioSegment.from_wav(audio_path)

    # Iteracja przez wiersze DataFrame
    for index, row in result.iterrows():
        file_id = row['file_ID'].strip()
        turn = row['turn'].strip()

        start_time = row['start'] * 1000  # konwersja na milisekundy
        stop_time = row['stop'] * 1000      # konwersja na milisekundy
        cut_audio = audio[start_time:stop_time]
        
        # Budowanie nazwy pliku WAV na podstawie 'file_ID', 'turn' i indeksu
        wav_filename = f"{file_id}_{turn}_{index}.wav"

        output_file_path = os.path.join(audio_save_dir, f"{wav_filename}")

        cut_audio.export(output_file_path, format="wav")

        # Utwórz pełną ścieżkę do pliku
        wav_file_path = os.path.join(audio_save_dir, wav_filename)
        
        # Dodaj ścieżkę do listy
        file_paths.append(wav_file_path)

    # Dodaj nową kolumnę do DataFrame z ścieżkami
    result['wav_file_path'] = file_paths

    result.to_csv(f"auxiliary/{result['file_ID'].iloc[0]}.csv", index=False, sep=';', encoding='utf-8')

    # Definiowanie ścieżki do pliku CSV
    csv_file_path = f'auxiliary/{audio_id}.csv'

    # Wczytaj plik CSV do DataFrame
    df_whisper = pd.read_csv(csv_file_path, sep=';', encoding='utf-8')  # Użyj separatora i kodowania zgodnie z tym, co ustawiłeś podczas zapisu

    # Załaduj model Whisper
    model = whisper.load_model("large-v3")

    def whisper_transcribe(file_path):
        # Ustaw język na ten, który chcesz transkrybować
        transcription = model.transcribe(file_path, language='pl')
        return transcription["text"]

    # Użyj funkcji whisper_transcribe do transkrypcji
    df_whisper['transcription'] = df_whisper['wav_file_path'].apply(lambda path: whisper_transcribe(path))

    # Mapowanie wartości
    df_whisper['speaker_tag'] = df_whisper['turn'].map({'speaker_0': 0, 'speaker_1': 1})

    # zmienianie tagów mówców w pd.df ze speaker_0 i speaker_1 na doktor i patient:
    max_duration_rows = df_whisper.loc[df_whisper.groupby('turn')['duration'].idxmax()]

    speaker_0_max_duration = max_duration_rows[max_duration_rows['turn'] == 'speaker_0'].reset_index(drop=True)
    speaker_1_max_duration = max_duration_rows[max_duration_rows['turn'] == 'speaker_1'].reset_index(drop=True) 

    speaker_model = nemo_asr.models.EncDecSpeakerLabelModel.from_pretrained(model_name='titanet_large')
    decision_0 = speaker_model.verify_speakers(audio_doctor_path, speaker_0_max_duration['wav_file_path'][0])
    decision_1 = speaker_model.verify_speakers(audio_doctor_path, speaker_1_max_duration['wav_file_path'][0])

    if decision_0:
        # Zastępuje speaker_0 na doctor i speaker_1 na patient
        df_whisper['turn'] = df_whisper['turn'].replace({'speaker_0': 'doctor', 'speaker_1': 'patient'})
    elif decision_1:
        # Zastępuje speaker_1 na doctor i speaker_0 na patient
        df_whisper['turn'] = df_whisper['turn'].replace({'speaker_1': 'doctor', 'speaker_0': 'patient'})


    # Konwersja DataFrame do records
    json_data_records = df_whisper.to_json(orient='records')

    # Ładowanie ciągów string z JSON i zadbanie o polskie znaki
    parsed_json = json.loads(json_data_records)
    print(json.dumps(parsed_json, ensure_ascii=False, indent=2))

    json_file_path = os.path.join(ROOT, f"{args.audio_name}.json")

    # Zapisywanie JSON z UTF-8 encoding
    with open(json_file_path, "w", encoding="utf-8") as f:
        json.dump(parsed_json, f, ensure_ascii=False, indent=2)

    print(f"JSON saved to: {json_file_path}")

    # Zapisywanie wynikowego csv
    df_whisper.to_csv(f"{ROOT}/{df_whisper['file_ID'].iloc[0]}.csv", index=False, sep=';', encoding='utf-8')

if __name__ == "__main__":
    # Tworzymy parser argumentów
    print('1')
    parser = argparse.ArgumentParser(description="Skrypt do przetwarzania pliku audio")
    parser.add_argument("audio_files", type=str, help="Ścieżka do miejsca, w którym ma się uruchamiać skrypt")
    parser.add_argument("test.wav", type=str, help="Nazwa pliku audio - nagranie rozmowy lekarz-pacjęt")
    parser.add_argument("user_10.wav", type=str, help="Nazwa pliku audio - nagranie lekarza")
    
    print('2')
    
    # Parsujemy argumenty
    # args = parser.parse_args()

    print('3')
    # main(args)
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







