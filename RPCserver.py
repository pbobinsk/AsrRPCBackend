import os, argparse, json
from dotenv import load_dotenv
from jsonrpcserver import Success, method, serve, Result, Error
import logging
import shutil

load_dotenv()
import sys
sys.path.append(os.getenv('ASR_DIR'))
from scripts import asr_module_speaker_recognition as asr # type: ignore

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

@method
def uploadFile(path: str) -> Result:
    try:
        shutil.copy(path, WORKING_DIR)
    except Exception as e:
        logging.error('Error during coping file '+str(e))
        return Error(-1,str(e))
    logging.debug('File copied '+path)
    return Success({'ans':"File copied"})

@method
def doASR(file: str, file_doctor) -> Result:
    try:
        setattr(nameSpaceArgs,'audio_name',file)
        setattr(nameSpaceArgs,'audio_name_doctor',file_doctor)
        asr.main(nameSpaceArgs)
        audio_path = os.path.join(WORKING_DIR, "WR_S0001_Z05BO.wav.json")
        json_file_path = os.path.join(WORKING_DIR, f"{nameSpaceArgs.audio_name}.json")
        shutil.copy(audio_path,json_file_path)
        f = open(json_file_path, encoding='utf-8')
        data = json.load(f)
    except Exception as e:
        logging.error('Error during ASR '+str(e))
        return Error(-1,str(e))
    logging.debug('ASR done for '+file+' and '+file_doctor)
    return Success(data)

def test():
    print(os.listdir(WORKING_DIR))
    setattr(nameSpaceArgs,'audio_name','WR_S0001_Z05BO.wav')
    setattr(nameSpaceArgs,'audio_name_doctor','WR_S0001_Z05BO_speaker_0_4.wav')
    asr.main(nameSpaceArgs)
    json_file_path = os.path.join(WORKING_DIR, "WR_S0001_Z05BO.wav.json")
    f = open(json_file_path, encoding='utf-8')
    data = json.load(f)
    print(data)
    print("Test done")

if __name__ == '__main__':
    """
    test()
    """
    try:
        serve(port=int(PORT))
    except KeyboardInterrupt:
        print('Server terminated')

