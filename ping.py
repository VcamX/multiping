
import re
import platform
import logging

import sh

import message_pb2

EXIT_CODE_UNKNOWN = -1
EXIT_CODE_OK = 0
EXIT_CODE_NOT_RESPONDING_LINUX = 1
EXIT_CODE_NOT_RESPONDING_OSX = 2
EXIT_CODE_INVALID_ARGS = 64
EXIT_CODE_UNRESOLVABLE = 68


def _parse_ping_statistic(s):
    def find_packet_loss(line):
        return float(line.split(',')[2].split()[0][:-1])

    def find_ttl(lines):
        for l in lines:
            if l.find('ttl') > 0:
                return int(re.findall('(?<=ttl=)\d+', l)[0])
        raise RuntimeError('TTL parse error')

    def find_rtt(line):
        nums = re.findall('\d+.\d+', line)
        return float(nums[1]), float(nums[-1])

    def find_ip(line):
        return re.findall('\d+.\d+.\d+.\d+', line)[0]

    lines = s.splitlines()
    packet_loss = find_packet_loss(lines[-2])
    ttl = find_ttl(lines)
    rtt, rtt_stddev = find_rtt(lines[-1])
    ip = find_ip(lines[0])
    return {
        'packet_loss': packet_loss,
        'ttl': ttl,
        'rtt': rtt,
        'rtt_stddev': rtt_stddev,
        'ip': ip,
    }


def ping(host, count, timeout):
    """IPv4 version of ping."""
    c_arg = '-c {0}'.format(count)
    p = platform.system()
    if p == 'Darwin':
        t_arg = '-t {0}'.format(timeout)
    elif p == 'Linux':
        t_arg = '-w {0}'.format(timeout)
    else:
        logging.error('Unsupported platform for ping: {0}'.format(p))
        return None

    try:
        if p == 'Linux':
            result = sh.ping('-4', c_arg, t_arg, host)
        else:
            result = sh.ping(c_arg, t_arg, host)
        data = _parse_ping_statistic(result.stdout)
        data['type'] = message_pb2.PingReply.OK
    except sh.ErrorReturnCode as e:
        if e.exit_code in [
            EXIT_CODE_NOT_RESPONDING_LINUX,
            EXIT_CODE_NOT_RESPONDING_OSX,
        ]:  # Not responding host
            data = {'type': message_pb2.PingReply.NOT_RESPONDING}
        elif e.exit_code == EXIT_CODE_INVALID_ARGS:  # Invalid arguments
            data = {'type': message_pb2.PingReply.INVALID_ARGS}
        elif e.exit_code == EXIT_CODE_UNRESOLVABLE:  # Unresolvable host
            data = {'type': message_pb2.PingReply.UNRESOLVABLE}
        else:
            logging.error('Unexpected error: {0}'.format(e.exit_code))
            data = {'type': message_pb2.PingReply.UNKNOWN}
    except Exception as e:
        logging.error('Unexpected error: {0}'.format(e))
        data = {'type': message_pb2.PingReply.UNKNOWN}
    return data
