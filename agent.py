#!/usr/bin/env python3

import json
import requests
import os
import logging
import atexit
import sys


home = os.environ['HOME']
pipe = '{}/.wps-zotero/wps-zotero-pipe'.format(home);
PIDFILE = '{}/.wps-zotero/wps-zotero-agent.pid'.format(home)
def running(sig=0):
    try:
        with open(PIDFILE) as f:
            pid = int(next(f))
        os.kill(pid, sig)
    except Exception:
        return False
    return os.path.exists(pipe)

if len(sys.argv) > 1 and sys.argv[1] == 'kill':
    running(2)
    sys.exit()

if running():
    sys.exit()
atexit.register(lambda : os.remove(PIDFILE))
with open(PIDFILE, 'w') as f:
    f.write('{}\n'.format(os.getpid()))

# Start logging
logfile = os.environ['HOME'] + '/.wps-zotero/agent.log'
if os.path.exists(logfile) and os.path.getsize(logfile) > 100 * 1024:
    os.remove(logfile)
logging.basicConfig(filename=logfile,
                    filemode='a',
                    format='%(asctime)s.%(msecs)03d %(levelname)s %(module)s: %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S',
                    level=logging.DEBUG)
logging.info('agent started')

# Create named pipe
if os.path.exists(pipe):
    os.remove(pipe)
if 0 != os.system('mkfifo {}'.format(pipe)):
    logging.error('Cannot create fifo!');
    sys.exit(1);
# delete the pipe unpon exiting
def onExit():
    logging.info('exiting')
    os.remove(pipe)
atexit.register(onExit);


while True:
    logging.info('::::::::::: reading...')
    # reading
    with open(pipe) as f:
        raw = f.read().strip()
    
    # received data (url and json payload)
    data = [line.strip() for line in raw.split('\n')]
    logging.debug('received data: {}'.format(data))
    assert(len(data) >= 2)
    url, payload = data[0], data[1]
    jpayload = json.loads(payload)

    # make requests
    try:
        response = requests.post(url, headers={'Content-Type': 'application/json; charset=utf-8'}, json=jpayload)
    except Exception as e:
        logging.warn('network error: {}'.format(e))
        with open(pipe, 'w') as f:
            f.write('1000\n"null"')
        continue

    # writing (status and json payload)
    logging.info('::::::::::: writing...')
    logging.debug('pushing result: {}, {}'.format(response.status_code, response.text))
    respStr = response.text
    try:
        response.json()
    except:
        respStr = '"' + respStr + '"'
    with open(pipe, 'w') as f:
        f.write('{}\n{}'.format(response.status_code, respStr))

