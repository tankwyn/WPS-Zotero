#!/usr/bin/env python3

import socket
import select
import time
import sys
import logging
import os
import atexit
import traceback
import errno

ZOTERO_PORT = 23119
PROXY_PORT = 21931
BUFSIZE = 4096
DELAY = 0.0001
PREFLIGHT_HEADERS = {
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Methods': 'GET,POST,OPTIONS,PUT,PATCH,DELETE',
    'Access-Control-Allow-Headers': '*',
    'Access-Control-Allow-Credentials': 'true',
}


def recvall(sock):
    data = b''
    while True:
        part = sock.recv(BUFSIZE)
        data += part
        if len(part) < BUFSIZE:
            break
    return data


class ProxyServer:
    input_list = []
    channels = {}
    clients = []

    def __init__(self, host, port):
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server.bind((host, port))
        self.server.listen()
        self.running = False

    def run(self):
        self.input_list.append(self.server)
        self.running = True
        while self.running:
            time.sleep(DELAY)
            logging.debug('---> begin to select')
            rlist, _, _ = select.select(self.input_list, [], [])
            logging.debug('---> select completed')
            for s in rlist:
                if s == self.server:
                    self.on_accept()
                    break

                data = recvall(s)
                if len(data) == 0:
                    self.on_close(s)
                    break
                else:
                    self.on_recv(s, data)

        # Close all sockets
        for s in self.input_list:
            s.close()
        self.input_list.clear()
        self.channels.clear()
        self.clients.clear()

    def on_accept(self):
        forward = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            forward.connect(('127.0.0.1', ZOTERO_PORT))
        except socket.error:
            logging.warning("Cannot connect to Zotero, is the app started?")
            return
        clientsock, clientaddr = self.server.accept()
        logging.info("{} has connected".format(clientaddr))
        self.clients.append(clientaddr)
        self.input_list.append(clientsock)
        self.input_list.append(forward)
        self.channels[clientsock] = forward
        self.channels[forward] = clientsock

    def on_close(self, s):
        logging.info("{} has disconnected".format(s.getpeername()))
        out = self.channels[s]
        pname = s.getpeername()
        if pname in self.clients:
            self.clients.pop(self.clients.index(pname))
        # Remove records
        self.input_list.remove(s)
        self.input_list.remove(out)
        del self.channels[s]
        del self.channels[out]
        # Close sockets
        s.close()
        out.close()

    def on_recv(self, s, data):
        logging.debug('received data: {}'.format(data))
        # Parse HEAD
        head_raw, _, body_raw = data.partition(b"\r\n\r\n")
        head = head_raw.decode('utf8').split("\r\n")
        request = head[0]
        headers = {t[0]: t[1] for t in map(lambda x: x.split(': ') + [''], head[1:])}
        if s.getpeername() in self.clients:
            # Stop proxy
            if data.startswith(b'POST') and ' /stopproxy ' in request:
                logging.info('received stopping command!')
                self.running = False
                return
            # Preflight responses
            logging.info('message received on client {}'.format(s.getpeername()))
            if data.startswith(b'OPTIONS') and 'Origin' in headers and 'Access-Control-Request-Method' in headers:
                for k,v in PREFLIGHT_HEADERS.items():
                    headers[k] = v
                data = '\r\n'.join(['HTTP/1.0 200 OK'] + [': '.join(h) for h in headers.items()] + ['', '']).encode('utf8') + body_raw
                s.send(data)
                logging.info('responded to a preflight request')
                return
        else:
            logging.info('message received from zotero')
            # CORS
            headers['Access-Control-Allow-Origin'] = '*'
            data = '\r\n'.join([request] + [': '.join(h) for h in headers.items()] + ['', '']).encode('utf8') + body_raw
        self.channels[s].send(data)
        logging.info('responded to {}'.format(self.channels[s].getpeername()))


def main(argv):
    # Configure logging
    if os.name == 'posix':
        logfile = os.environ['HOME'] + '/.wps-zotero-proxy.log'
    else:
        logfile = os.environ['APPDATA'] + '\\kingsoft\\wps\\jsaddons\\wps-zotero-proxy.log'
    if os.path.exists(logfile) and os.path.getsize(logfile) > 100 * 1024:
        os.remove(logfile)
    logging.basicConfig(filename=logfile,
                        filemode='a',
                        format='%(asctime)s.%(msecs)03d %(levelname)s %(module)s: %(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S',
                        level=logging.DEBUG)

    if len(argv) < 2:
        try:
            server = ProxyServer('127.0.0.1', PROXY_PORT)
            logging.info('proxy started!')
            atexit.register(lambda : logging.info('proxy stopped!'))
            server.run()
        except Exception as e:
            if isinstance(e, socket.error) and e.errno == errno.EADDRINUSE:
                logging.warning("port is already binded!")
                sys.exit()
            else:
                logging.error('encountered unexpected error, exiting!')
                logging.error(e)
                logging.error(traceback.format_exc())
    else:
        if (argv[1] == 'kill'):
            s = None
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.connect(('127.0.0.1', PROXY_PORT))
                s.send(b'POST /stopproxy HTTP/1.1\r\n\r\n')
            finally:
                if s:
                    s.close()


if __name__ == '__main__':
    main(sys.argv)
