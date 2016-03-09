
import platform
import json
import logging


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
