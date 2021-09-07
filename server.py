from app.server import app, load_config
import argparse

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Server')
    parser.add_argument('--config', help='Config file', default='config.yaml')
    args = parser.parse_args()
    load_config(app, args.config)
    app.run()
