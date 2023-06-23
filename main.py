from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler

import json
import mimetypes
import pathlib
import socket
import threading
import urllib.parse

UDP_IP = '127.0.0.1'
UDP_PORT = 5000
JSON = "storage/data.json"
BASE_DIR = pathlib.Path()


class HttpHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        pr_url = urllib.parse.urlparse(self.path)
        if pr_url.path == '/':
            self.send_html_file('index.html')
        elif pr_url.path == '/message.html':
            self.send_html_file('message.html')
        elif pathlib.Path().joinpath(pr_url.path[1:]).exists():
            self.send_static()
        else:
            self.send_html_file('error.html', 404)

    def do_POST(self):
        data = self.rfile.read(int(self.headers['Content-Length']))
        print(data)
        data_parse = urllib.parse.unquote_plus(data.decode())
        print(data_parse)
        data_dict = {key: value for key, value in [el.split('=') for el in data_parse.split('&')]}
        with open(BASE_DIR.joinpath('storage/data.json'), "w", encoding='utf-8') as j:
            json.dump(data_dict, j, ensure_ascii=False)
        print(data_dict)
        self.send_response(302)
        self.send_header('Location', '/')
        self.end_headers()

    def send_html_file(self, filename, status=200):
        self.send_response(status)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        with open(filename, 'rb') as fd:
            self.wfile.write(fd.read())

    def send_static(self):
        self.send_response(200)
        mt = mimetypes.guess_type(self.path)
        if mt:
            self.send_header("Content-type", mt[0])
        else:
            self.send_header("Content-type", 'text/plain')
        self.end_headers()
        with open(f'.{self.path}', 'rb') as file:
            self.wfile.write(file.read())

    @staticmethod
    def send_to_server(data):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        server_1 = UDP_IP, UDP_PORT
        sock.sendto(data, server_1)
        sock.close()


def run_client(server_class=HTTPServer, handler_class=HttpHandler):
    server_address = ('', 3000)
    http = server_class(server_address, handler_class)
    try:
        http.serve_forever()
    except KeyboardInterrupt:
        http.server_close()


def run_server():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    serv = UDP_IP, UDP_PORT
    sock.bind(serv)
    try:
        while True:
            data, address = sock.recvfrom(1024)
            data_parse = urllib.parse.unquote_plus(data.decode())
            data_dict = {
                str(datetime.now()): {key: value for key, value in [el.split('=') for el in data_parse.split('&')]}}

    except KeyboardInterrupt:
        print(f'Destroy server')
    finally:
        sock.close()


if __name__ == '__main__':
    server = threading.Thread(target=run_server)
    client = threading.Thread(target=run_client)

    server.start()
    client.start()
    server.join()
    client.join()


    server.start()
    client.start()
    server.join()
    client.join()
