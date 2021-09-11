import os
import yaml

_config = None

def _load_config():
    config_name = os.environ.get('CONFIG_FILE', 'config.yaml')

    try:
        opened_file = open(config_name, 'r')
        config = yaml.load(opened_file)
        opened_file.close()
        return config
    except Exception:
        raise ValueError(f'Error on uploading config file: {config_name}')


def load_config():
    global _config
    if _config is None:
        _config = _load_config()

    return _config
