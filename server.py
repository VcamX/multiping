
import argparse
import time
import logging

import message_pb2
import servicer
import utils

_ONE_DAY_IN_SECONDS = 60 * 60 * 24

parser = argparse.ArgumentParser(description='Multiping server side.')
parser.add_argument('--config', '-c', default='config.json',
                    help='Config file (default: config.json)')
parser.add_argument('--verbose', '-v', action='store_true',
                    help='Verbose')
args = parser.parse_args()

logging.basicConfig(level=logging.DEBUG if args.verbose else logging.INFO,
                    format='%(asctime)s  %(message)s',
                    datefmt="%Y-%m-%d %H:%M:%S")


def serve(config):
    server = message_pb2.beta_create_Communication_server(
        servicer.MessageServicer())
    port = server.add_insecure_port(config['port'])
    logging.info('Listening on {0}'.format(port))
    server.start()
    try:
        while True:
            time.sleep(_ONE_DAY_IN_SECONDS)
    except KeyboardInterrupt:
        server.stop(0)


def main():
    config = utils.load_config(args.config)
    serve(config)


if __name__ == '__main__':
    main()
