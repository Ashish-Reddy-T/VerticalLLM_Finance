import os, yaml,logging
from pathlib import Path
from dotenv import find_dotenv, load_dotenv

def get_config():
    config_path = Path(__file__).parent / "config.yaml"
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)

def get_keys(key):
    dotenv_path = find_dotenv()
    load_dotenv(dotenv_path)

    ALPHA_VANTAGE = os.getenv("ALPHA_VANTAGE")
    FINNHUB = os.getenv("FINNHUB")
    NEWSAPI = os.getenv("NEWSAPI")
    TWITTER = os.getenv("TWITTER")
    REDDIT = os.getenv("REDDIT")
    PATH = "/Users/AshishR_T/.ollama/models/blobs/sha256-f5074b1221da0f5a2910d33b642efa5b9eb58cfdddca1c79e16d7ad28aa2b31f"

    if key == "ALPHA_VANTAGE":
        return ALPHA_VANTAGE
    elif key == "FINNHUB":
        return FINNHUB
    elif key == "NEWSAPI":
        return NEWSAPI
    elif key == "TWITTER":
        return TWITTER
    elif key == "REDDIT":
        return REDDIT
    elif key == "PATH":
        return PATH
    else:
        return None
    
def setup_logger():
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)

    if logger.hasHandlers():
        logger.handlers.clear()
    
    log_file = Path(__file__).parent / "backtest.log"
    file_handler = logging.FileHandler(log_file, mode='w')
    file_handler.setLevel(logging.DEBUG)

    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)

    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    logger.info("Logger has been set up.")
    return logger