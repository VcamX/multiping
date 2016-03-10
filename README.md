Multiping
=========

Ping from different hosts and gather results.

### Server
```
usage: server.py [-h] [--config CONFIG] [--ssl] [--verbose]

Multiping server side.

optional arguments:
  -h, --help            show this help message and exit
  --config CONFIG, -c CONFIG
                        config file (default: config/config_server.json)
  --ssl                 use SSL
  --verbose, -v         verbose mode
```
### Client
```
usage: client.py [-h] [--config CONFIG] [--servers SERVERS] [--async]
                 [--verbose]
                 {platform,ping} ...

Multiping client side.

optional arguments:
  -h, --help            show this help message and exit
  --config CONFIG, -c CONFIG
                        config file (default: config/config_client.json)
  --servers SERVERS, -s SERVERS
                        config file for available servers (default:
                        config/servers.json)
  --async, -a           use async mechanism
  --verbose, -v         verbose mode

actions:
  Commands supported for client.

  {platform,ping}
    platform            platform information of servers alive
    ping                ping to host
```
```
usage: client.py platform [-h]

Platform information of servers alive.

optional arguments:
  -h, --help  show this help message and exit
```
```
usage: client.py ping [-h] [--count COUNT] [--timeout TIMEOUT] host

Ping to host.

positional arguments:
  host

optional arguments:
  -h, --help         show this help message and exit
  --count COUNT      number of packets to send (default: 1)
  --timeout TIMEOUT  timeout of ping (default: 10)
```
