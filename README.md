Multiping
=========

Sending pings from different hosts and gathering results.

### Server
```
usage: server.py [-h] [--config CONFIG] [--verbose]

Multiping server side.

optional arguments:
  -h, --help            show this help message and exit
  --config CONFIG, -c CONFIG
                        Config file (default: config_server.json)
  --verbose, -v         Verbose
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
                        Config file (default: config_client.json)
  --servers SERVERS, -s SERVERS
                        Config file for available servers (default:
                        servers.json)
  --async, -a           Using async mechanism
  --verbose, -v         Verbose

actions:
  Commands supported for client.

  {platform,ping}
    platform            Show platform information of servers alive
    ping                Ping to host
```