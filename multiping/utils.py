
from __future__ import print_function

import re
import platform
import json
import logging
import time


def platform_info():
    return {
        'system': platform.system(),
        'release': platform.release(),
        'machine': platform.machine(),
    }


def load_config(file):
    with open(file, 'r') as f:
        try:
            config = json.load(f)
        except ValueError:
            logging.error('Config file error: {0}'.format(file))
            config = {}
    return config


def load_servers(file):
    with open(file, 'r') as f:
        try:
            servers = json.load(f)
        except ValueError:
            logging.error('Servers config file error: {0}'.format(file))
            servers = {}
    return servers


def is_valid_addr_v4(addr):
    """Borrowed from http://stackoverflow.com/questions/106179"""
    p = re.compile(
        '^(([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])\.){3}([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])$')
    return p.match(addr) is not None


def is_valid_hostname(hostname):
    """Borrowed from http://stackoverflow.com/questions/106179"""
    p = re.compile(
        '^(([a-zA-Z0-9]|[a-zA-Z0-9][a-zA-Z0-9\-]*[a-zA-Z0-9])\.)*([A-Za-z0-9]|[A-Za-z0-9][A-Za-z0-9\-]*[A-Za-z0-9])$')
    return p.match(hostname) is not None


def resource_string(file):
    with open(file, 'r') as f:
        s = f.read()
    return s


def count_time(func):
    def inner(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        print()
        print('Time elapsed: {0}'.format(time.time()-start))
        return result
    return inner
