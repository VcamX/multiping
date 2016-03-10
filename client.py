
from __future__ import print_function

import argparse
import logging
import threading

from grpc.beta import implementations

from multiping import (
    message_pb2, servicer, utils
)

_ARGS_CONFIG = 'config/config_client.json'
_ARGS_SERVERS = 'config/servers.json'

_ARGS_PING_COUNT = 1
_ARGS_PING_TIMEOUT = 10

parser = argparse.ArgumentParser(description='Multiping client side.')
parser.add_argument('--config', '-c', default=_ARGS_CONFIG, help="""
Config file (default: {0})""".format(_ARGS_CONFIG))
parser.add_argument('--servers', '-s', default=_ARGS_SERVERS, help="""
Config file for available servers (default: {0})""".format(_ARGS_SERVERS))
parser.add_argument('--async', '-a', action='store_true',
                    help='Using async mechanism')
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

        self._lock = threading.Lock()
        self._queue = []

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
            self._initialized = True

    @property
    def servers(self):
        return self._servers

    def _waiting_result(self, label, future):
        try:
            result = future.result()
        except Exception as e:
            logging.error('Unexpected error: {0}'.format(e))
            result = None
        with self._lock:
            self._queue.append((label, result))

    def _platform_generator(self, size=0):
        while size > 0:
            if len(self._queue) > 0:
                size -= 1
                with self._lock:
                    label, resp = self._queue.pop(0)
                result = None if resp is None else {
                    'system': resp.system,
                    'release': resp.release,
                    'machine': resp.machine,
                }
                yield label, result

    def platform(self, async=False):
        if not self._initialized:
            raise RuntimeError('Must call init() first')

        if async:
            self._queue = []
            for label, stub in self._stubs.items():
                future = stub.Platform.future(message_pb2.PlatformRequest(),
                                            self._config['timeout'])
                t = threading.Thread(target=self._waiting_result,
                                     args=[label, future])
                t.start()
            results = self._platform_generator(len(self.servers))
        else:
            results = {}
            for label, stub in self._stubs.items():
                logging.debug('Sending PlatformRequest')
                resp = stub.Platform(message_pb2.PlatformRequest(),
                                     self._config['timeout'])
                logging.debug('Receiving PlatformReply')
                results[label] = {
                    'system': resp.system,
                    'release': resp.release,
                    'machine': resp.machine,
                }
            results = results.items()
        return results

    def _ping_generator(self, size=0):
        while size > 0:
            if len(self._queue) > 0:
                size -= 1
                with self._lock:
                    label, resp = self._queue.pop(0)
                result = None if resp is None else {
                    'type': resp.type,
                    'ip': resp.ip,
                    'packet_loss': resp.packet_loss,
                    'ttl': resp.ttl,
                    'rtt': resp.rtt,
                    'rtt_stddev': resp.rtt_stddev,
                } if resp.type == message_pb2.PingReply.OK else {
                    'type': resp.type,
                }
                yield label, result

    def ping(self, host, count, timeout, async=False):
        if not self._initialized:
            raise RuntimeError('Must call init() first')

        if async:
            self._queue = []
            for label, stub in self._stubs.items():
                future = stub.Ping.future(
                    message_pb2.PingRequest(host=host, count=count,
                                            timeout=timeout),
                    self._config['timeout'])
                t = threading.Thread(target=self._waiting_result,
                                     args=[label, future])
                t.start()
            results = self._ping_generator(len(self.servers))
        else:
            results = {}
            for label, stub in self._stubs.items():
                resp = stub.Ping(message_pb2.PingRequest(host=host, count=count,
                                                         timeout=timeout),
                                 self._config['timeout'])
                results[label] = {'type': resp.type}
                if resp.type == message_pb2.PingReply.OK:
                    results[label]['ip'] = resp.ip
                    results[label]['packet_loss'] = resp.packet_loss
                    results[label]['ttl'] = resp.ttl
                    results[label]['rtt'] = resp.rtt
                    results[label]['rtt_stddev'] = resp.rtt_stddev
            results = results.items()
        return results


def platform(client):
    client.init()
    results = client.platform(async=args.async)

    print('Servers alive:')
    for label, result in results:
        print()
        print('Server [{0}]'.format(label))
        if result is None:
            print('  RPC Error')
        else:
            print('  Host: {0}'.format(client.servers[label]['host']))
            print('  Port: {0}'.format(client.servers[label]['port']))
            print('  Platform: {system}-{release}-{machine}'.format(
                **result))


def ping(client):
    client.init()
    if utils.is_valid_addr_v4(args.host) or utils.is_valid_hostname(args.host):
        results = client.ping(args.host, args.count, args.timeout,
                              async=args.async)

        print('Ping results:')
        for label, result in results:
            print()
            print('Server [{0}]'.format(label))
            if result is None:
                print('  RPC Error')
            else:
                print('  Type: {0} {1}'.format(
                    result['type'],
                    servicer.ping_reply_type_string(result['type'])))
                if result['type'] == message_pb2.PingReply.OK:
                    print('  Target IP Address: {0}'.format(result['ip']))
                    print('  Packet loss: {0}%'.format(
                        round(result['packet_loss'], 2)))
                    print('  TTL: {0}'.format(result['ttl']))
                    print('  RTT: {0}, RTT STDDEV: {1}'.format(
                        round(result['rtt'], 2), round(result['rtt_stddev'], 2)))
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
