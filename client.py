
from __future__ import print_function

import argparse
import logging

from grpc.beta import implementations

import message_pb2
import utils

_ARGS_CONFIG = 'client_config.json'
_ARGS_SERVERS = 'servers.json'

parser = argparse.ArgumentParser(description='Multiping client side.')
parser.add_argument('--config', '-c', default=_ARGS_CONFIG, help="""
Config file (default: {0})""".format(_ARGS_CONFIG))
parser.add_argument('--servers', '-s', default=_ARGS_SERVERS, help="""
Config file for available servers (default: {0})""".format(_ARGS_SERVERS))
parser.add_argument('--verbose', '-v', action='store_true',
                    help='Verbose')

subparsers = parser.add_subparsers(
    dest='action', title='actions',
    description='Commands supported for client.')
parser_platform = subparsers.add_parser(
    'platform', help='Show platform information of servers alive')
args = parser.parse_args()

logging.basicConfig(level=logging.DEBUG if args.verbose else logging.INFO,
                    format='%(asctime)s  %(message)s',
                    datefmt="%Y-%m-%d %H:%M:%S")


class Client(object):

    @staticmethod
    def _default_config():
        return {
            'timeout': 60,
        }

    def __init__(self, servers, config):
        self._servers = servers
        self._config = Client._default_config() if config is None else config
        self._channels = None
        self._stubs = None
        self._platform_info = None
        self._initialized = False

    def init(self):
        if not self._initialized:
            self._channels = {}
            self._stubs = {}
            for label, server in self._servers.items():
                chan = implementations.insecure_channel(server['host'],
                                                        server['port'])
                st = message_pb2.beta_create_Communication_stub(chan)

                self._channels[label] = chan
                self._stubs[label] = st

    @property
    def servers(self):
        return self._servers

    def _get_platform_info(self):
        self._platform_info = {}
        for label, stub in self._stubs.items():
            logging.debug('Sending PlatformRequest')
            resp = stub.Platform(message_pb2.PlatformRequest(),
                                 self._config['timeout'])
            logging.debug('Receiving PlatformReply')
            self._platform_info[label] = {
                'system': resp.system,
                'release': resp.release,
                'machine': resp.machine,
            }

    @property
    def platform_info(self):
        if self._platform_info is None:
            self._get_platform_info()
        return self._platform_info

            print()
def platform(client):
    client.init()
    platform_info = client.platform_info
    print('Servers alive:')
    for label in platform_info:
        print()
        print('Server [{0}]'.format(label))
        print('  Host: {0}'.format(client.servers[label]['host']))
        print('  Port: {0}'.format(client.servers[label]['port']))
        print('  Platform: {system}-{release}-{machine}'.format(
            **platform_info[label]))


def main():
    servers = utils.load_servers(args.servers)
    config = utils.load_config(args.config)
    client = Client(servers, config)

    if args.action == 'platform':
        platform(client)


if __name__ == '__main__':
    main()
