import argparse
import os


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Server')
    parser.add_argument('--config', help='Config file', default='config.yaml')
    args = parser.parse_args()
    os.environ['CONFIG_FILE'] = args.config

    from app.server import app
    from app.config import load_config

    config = load_config()
    app.run(port=config['port'])
