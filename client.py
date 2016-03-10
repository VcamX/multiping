
from __future__ import print_function

import argparse
import logging

from grpc.beta import implementations

import message_pb2
import servicer
import utils

_ARGS_CONFIG = 'config_client.json'
_ARGS_SERVERS = 'servers.json'

_ARGS_PING_COUNT = 1
_ARGS_PING_TIMEOUT = 10

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
parser_ping = subparsers.add_parser('ping', help='Ping to host')

parser_ping.add_argument('host')
parser_ping.add_argument('--count', type=int,
                         default=_ARGS_PING_COUNT, help="""
Number of packets to send (default: {0})""".format(_ARGS_PING_COUNT))
parser_ping.add_argument('--timeout', type=int,
                         default=_ARGS_PING_TIMEOUT, help="""
Timeout of ping (default: {0})""".format(_ARGS_PING_TIMEOUT))

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

    def ping(self, host, count, timeout):
        print('Ping results:')
        for label, stub in self._stubs.items():
            print()
            resp = stub.Ping(message_pb2.PingRequest(host=host, count=count,
                                                     timeout=timeout),
                             self._config['timeout'])
            print('From server [{0}]'.format(label))
            print('  Type: {0} {1}'.format(
                resp.type,
                servicer.ping_reply_type_string(resp.type)))
            if resp.type == message_pb2.PingReply.OK:
                print('  Target IP Address: {0}'.format(resp.ip))
                print('  Packet loss: {0}%'.format(round(resp.packet_loss, 2)))
                print('  TTL: {0}'.format(resp.ttl))
                print('  RTT: {0}, RTT STDDEV: {1}'.format(
                    round(resp.rtt, 2), round(resp.rtt_stddev, 2)))


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


def ping(client):
    client.init()
    if utils.is_valid_addr_v4(args.host) or utils.is_valid_hostname(args.host):
        client.ping(args.host, args.count, args.timeout)
    else:
        logging.error('Invalid host name: {0}'.format(args.host))


def main():
    servers = utils.load_servers(args.servers)
    config = utils.load_config(args.config)
    client = Client(servers, config)

    if args.action == 'platform':
        platform(client)
    elif args.action == 'ping':
        ping(client)


if __name__ == '__main__':
    main()
