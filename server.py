
import argparse
import time
import logging

from multiping import (
    message_pb2, servicer, utils
)

_ARGS_CONFIG = 'config/config_server.json'

parser = argparse.ArgumentParser(description='Multiping server side.')
parser.add_argument('--config', '-c', default=_ARGS_CONFIG,
                    help='Config file (default: {0})'.format(_ARGS_CONFIG))
parser.add_argument('--verbose', '-v', action='store_true',
                    help='Verbose')
args = parser.parse_args()

logging.basicConfig(level=logging.DEBUG if args.verbose else logging.INFO,
                    format='%(asctime)s  %(message)s',
                    datefmt="%Y-%m-%d %H:%M:%S")


def default_config():
    return {
        'port': "[::]:50051",
        'time_to_sleep': 86400,
    }


def serve(config):
    if config is None:
        config = default_config()
    server = message_pb2.beta_create_Communication_server(
        servicer.MessageServicer())
    port = server.add_insecure_port(config['port'])
    logging.info('Listening on {0}'.format(port))
    server.start()
    try:
        while True:
            time.sleep(config['time_to_sleep'])
    except KeyboardInterrupt:
        server.stop(0)


def main():
    config = utils.load_config(args.config)
    serve(config)


if __name__ == '__main__':
    main()
