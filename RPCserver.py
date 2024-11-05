import os, argparse, json
from dotenv import load_dotenv
import asr_module as asr

load_dotenv()
WORKING_DIR = os.getenv('WORKING_DIR')

def test():
    print(os.listdir(WORKING_DIR))
    args= argparse.Namespace(**{"directory":WORKING_DIR,"audio_name":"WR_S0001_Z05BO.wav"})
    audio_path = os.path.join(WORKING_DIR, args.audio_name)
    json_file_path = os.path.join(WORKING_DIR, f"{args.audio_name}.json")
    f = open(json_file_path, encoding='utf-8')
    data = json.load(f)
    print(data)
    

if __name__ == '__main__':
    test()
    args= argparse.Namespace(**{"directory":WORKING_DIR,"audio_name":"WR_S0001_Z05BO.wav"})
    asr.main(args)
    print("Done")
    