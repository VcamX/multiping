
import argparse
import time
import logging

from grpc.beta import implementations

from multiping import (
    message_pb2, servicer, utils
)

_ARGS_CONFIG = 'config/config_server.json'

parser = argparse.ArgumentParser(description='Multiping server side.')
parser.add_argument('--config', '-c', default=_ARGS_CONFIG,
                    help='config file (default: {0})'.format(_ARGS_CONFIG))
parser.add_argument('--ssl', action='store_true', help='use SSL')
parser.add_argument('--verbose', '-v', action='store_true',
                    help='verbose mode')
args = parser.parse_args()

logging.basicConfig(level=logging.DEBUG if args.verbose else logging.INFO,
                    format='%(asctime)s  %(message)s',
                    datefmt="%Y-%m-%d %H:%M:%S")


def default_config():
    return {
        'port': '[::]:50051',
        'time_to_sleep': 86400,
        'private_key': '',
        'certificate_chain': '',
    }


def serve(config):
    d_config = default_config()
    if config is not None:
        d_config.update(config)
    config = d_config

    server = message_pb2.beta_create_Communication_server(
        servicer.MessageServicer())
    if args.ssl:
        if config['private_key'] == '' or config['certificate_chain'] == '':
            raise RuntimeError(
                'To enable SSL private_key and certificate_chain must be set')
        creds = implementations.ssl_server_credentials([(
            utils.resource_string(config['private_key']),
            utils.resource_string(config['certificate_chain']))])
        port = server.add_secure_port('[::]:{0}'.format(config['port']), creds)
    else:
        port = server.add_insecure_port('[::]:{0}'.format(config['port']))
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
