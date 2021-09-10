import argparse
import os

from app.server import app


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Server')
    parser.add_argument('--config', help='Config file', default='config.yaml')
    args = parser.parse_args()
    os.environ['CONFIG_FILE'] = args.config
    app.run()
