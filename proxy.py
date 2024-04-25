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


def parse_head(hd_raw):
    head = hd_raw.decode('utf8').split("\r\n")
    request = head[0]
    headers = {t[0]: t[1] for t in map(lambda x: x.split(': ') + [''], head[1:])}
    return request, headers


def recv_all(sock):
    data = b''
    closed = False

    # Read in Http head
    while True:
        part = sock.recv(BUFSIZE)
        if not part:
            closed = True
            break
        data += part
        if b'\r\n\r\n' in data:
            break

    if not data:
        return data

    hd_raw = data.partition(b'\r\n\r\n')[0]
    req, headers = parse_head(hd_raw)

    # Read full body
    if 'Content-Length' in headers:
        length = len(hd_raw) + 4 + int(headers['Content-Length'])
        while len(data) < length:
            data += sock.recv(BUFSIZE)
    elif not closed:
        if req.startswith('TRACE'):
            # TRACE method must not include a body
            pass
        elif data.startswith(b'OPTIONS') and 'Origin' in headers and 'Access-Control-Request-Method' in headers:
            # Preflight requests don't have a body
            pass
        else:
            # Continue to read till the connection is closed
            while True:
                part = sock.recv(BUFSIZE)
                if not part:
                    closed = True
                    break
                data += part

    return data


def stop_proxy():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        s.connect(('127.0.0.1', PROXY_PORT))
        s.send(b'POST /stopproxy HTTP/1.1\r\n\r\n')
    except:
        # Swallow all exceptions
        pass
    finally:
        s.close()


class ProxyServer:
    input_list = []
    channels = {}
    clients = []

    def __init__(self, host, port):
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # NOTE: Setting this on Windows will cause multiple instances listening on the same port.
        if os.name == 'posix':
            self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1);
        self.server.bind((host, port))
        self.server.listen()
        self.running = False

    def run(self):
        self.input_list.append(self.server)
        self.running = True
        while self.running:
            time.sleep(DELAY)
            rlist, _, _ = select.select(self.input_list, [], [])
            for s in rlist:
                if s == self.server:
                    self.on_accept()
                    break

                data = recv_all(s)
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
        self.server.close()

    def on_accept(self):
        clientsock, clientaddr = self.server.accept()
        self.clients.append(clientaddr)
        self.input_list.append(clientsock)
        logging.info("{} has connected".format(clientaddr))
        forward = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            forward.connect(('127.0.0.1', ZOTERO_PORT))
        except socket.error as e:
            logging.warning("Cannot connect to Zotero, is the app started?")
            logging.debug("Failed to connect to Zotero: {}".format(e))
            forward.close()
            # NOTE: Cannot close client sockets here for it will discard quit commands.
            return
        self.input_list.append(forward)
        self.channels[clientsock] = forward
        self.channels[forward] = clientsock

    def on_close(self, s):
        pname = s.getpeername()
        if pname in self.clients:
            self.clients.pop(self.clients.index(pname))
        if s in self.channels:
            out = self.channels[s]
            out.close()
            self.input_list.remove(out)
            del self.channels[s]
            del self.channels[out]
        self.input_list.remove(s)
        s.close()
        logging.info("{} has disconnected".format(pname))

    def on_recv(self, s, data):
        logging.debug('received data: {}'.format(data))
        if data.startswith(b'POST /stopproxy'):
            logging.info('received stopping command!')
            s.close()
            self.running = False
            return
        if s not in self.channels:
            self.on_close(s)
            return
        # Parse HEAD
        head_raw, _, body_raw = data.partition(b"\r\n\r\n")
        request, headers = parse_head(head_raw)
        if s.getpeername() in self.clients:
            # Preflight responses
            logging.info('message received on client {}'.format(s.getpeername()))
            if data.startswith(b'OPTIONS') and 'Origin' in headers and 'Access-Control-Request-Method' in headers:
                for k,v in PREFLIGHT_HEADERS.items():
                    headers[k] = v
                data = '\r\n'.join(['HTTP/1.0 200 OK'] + [': '.join(h) for h in headers.items()] + ['', '']).encode('utf8') + body_raw
                s.sendall(data)
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
                        level=logging.INFO)

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
            stop_proxy()


if __name__ == '__main__':
    main(sys.argv)
