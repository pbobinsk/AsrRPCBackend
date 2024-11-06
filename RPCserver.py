import os, argparse, json
from dotenv import load_dotenv
from jsonrpcserver import Success, method, serve, Result, Error
import logging

load_dotenv()
import sys
sys.path.append(os.getenv('ASR_DIR'))
from scripts import asr_module as asr # type: ignore

WORKING_DIR = os.getenv('WORKING_DIR')
logging.basicConfig(
    level=os.getenv('LOGLEVEL', 'INFO').upper()
)
PORT = os.getenv('PORT',5000)
nameSpaceArgs= argparse.Namespace(**{"directory":WORKING_DIR})

@method
def ping():
    return Success("pong")

@method
def hello(name: str) -> Result:
    if (name==''):
        logging.error('Error')
        return Error(-1,'Empty string')
    return Success({'ans':"Hello " + name})

def test():
    print(os.listdir(WORKING_DIR))
    args= argparse.Namespace(**{"directory":WORKING_DIR,"audio_name":"WR_S0001_Z05BO.wav"})
    audio_path = os.path.join(WORKING_DIR, args.audio_name)
    json_file_path = os.path.join(WORKING_DIR, f"{args.audio_name}.json")
    f = open(json_file_path, encoding='utf-8')
    data = json.load(f)
    print(data)
    

if __name__ == '__main__':
    #test()
    setattr(nameSpaceArgs,'audio_name','test.wav')
    print(nameSpaceArgs)
    asr.main(nameSpaceArgs)
    #print("Done")
    try:
        serve(port=int(PORT))
    except KeyboardInterrupt:
        print('Server terminated')

    