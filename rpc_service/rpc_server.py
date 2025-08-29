import os, argparse, json
from dotenv import load_dotenv
from jsonrpcserver import Success, method, serve, Result, Error
import logging, traceback
import shutil
from pathlib import Path

load_dotenv()
# from asr_module import asr_module_mock as asr # type: ignore
import asr_module as asr

log_level = os.getenv('LOGLEVEL', 'INFO').upper()
logging.basicConfig(
    level=log_level,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'

)
log = logging.getLogger('rpc_service.ASR')
log.setLevel(log_level)
log.info("Konfiguracja logowania zakończona.")
log.info(f"Poziom logowania: {log_level}")

log.info('Init ...')
WORKING_DIR = os.getenv('WORKING_DIR')
PORT = os.getenv('PORT',5000)
nameSpaceArgs= argparse.Namespace(**{"directory":WORKING_DIR})
PRODUCTION = int(os.getenv('PRODUCTION',1))
OPENAI_DIR = os.getenv('OPENAI_DIR')
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
WORKING_DIR = os.path.join(PROJECT_ROOT, WORKING_DIR)
OPENAI_DIR = os.path.join(PROJECT_ROOT, OPENAI_DIR)
log.debug(PRODUCTION)
log.debug(PROJECT_ROOT)
log.debug(WORKING_DIR)
log.debug(OPENAI_DIR)
log.info('Init end')
if asr.is_real_asr_in_use():
    log.info("Przetwarzanie wykonane przez prawdziwy silnik ASR.")
else:
    log.info("Przetwarzanie wykonane przez atrapę.")

@method
def ping():
    print(WORKING_DIR)
    return Success("pong")

@method
def hello(name: str) -> Result:
    if (name==''):
        log.error('Error')
        return Error(-1,'Empty string')
    return Success({'ans':"Hello " + name})

@method
def uploadFile(path: str) -> Result:
    try:
        shutil.copy(path, WORKING_DIR)
    except Exception as e:
        log.error('Error during coping file '+str(e))
        return Error(-1,str(e))
    log.debug('File copied '+path+" -> "+WORKING_DIR)
    return Success({'ans':"File copied"})

@method
def doASR(file: str, file_doctor) -> Result:
    print('doASR')
    try:
        setattr(nameSpaceArgs,'audio_name',file)
        setattr(nameSpaceArgs,'audio_name_doctor',file_doctor)
        asr.main(nameSpaceArgs)
        json_file_path = os.path.join(WORKING_DIR, f"{nameSpaceArgs.audio_name}.json")
        csv_file_path = os.path.join(WORKING_DIR, f"{Path(nameSpaceArgs.audio_name).stem}.csv")
        f = open(json_file_path, encoding='utf-8')
        data = json.load(f)
        csv_openai_path = os.path.join(OPENAI_DIR, Path(csv_file_path).name)
        json_openai_path = os.path.join(OPENAI_DIR, Path(json_file_path).name)
        log.debug('json_file_path -> json_openai_path: '+json_file_path+' -> '+json_openai_path)
        log.debug('csv_file_path -> csv_openai_path: '+csv_file_path+' -> '+csv_openai_path)
    except Exception as e:
        log.error('Error during ASR '+str(e))
        return Error(-1,str(e))
    log.debug('ASR done for '+file+' and '+file_doctor)
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
    log.info('Starting server')
    try:
        serve(port=int(PORT))
    except KeyboardInterrupt:
        print('Server terminated')

