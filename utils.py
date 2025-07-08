import os
import yaml
from pathlib import Path


def get_config():
    """Load configuration and override API keys with environment variables."""
    config_path = Path(__file__).parent / "config.yaml"    template_path = Path(__file__).parent / "config_template.yaml"

    if config_path.exists():
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f) or {}
    else:
        with open(template_path, 'r') as f:
            config = yaml.safe_load(f) or {}

    api_keys = config.get('api_keys', {})
    env_map = {
        'alpha_vantage': 'ALPHA_VANTAGE_API_KEY',
        'finnhub': 'FINNHUB_API_KEY',
        'news': 'NEWS_API_KEY',
    }
    for key, env_var in env_map.items():
        env_val = os.getenv(env_var)
        if env_val:
            api_keys[key] = env_val
    config['api_keys'] = api_keys
    return config
