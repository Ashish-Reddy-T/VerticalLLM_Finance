import os
import yaml
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
    else:
        return None