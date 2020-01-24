#  coding: utf-8
import socketserver
import logging
import os
import time
import mimetypes

# Copyright 2013 Abram Hindle, Eddie Antonio Santos
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
#
# Furthermore it is derived from the Python documentation examples thus
# some of the code is Copyright © 2001-2013 Python Software
# Foundation; All Rights Reserved
#
# http://docs.python.org/2/library/socketserver.html
#
# run: python freetests.py

# try: curl -v -X GET http://127.0.0.1:8080/

# The following websites were used as sources:
# https://pymotw.com/3/socketserver/
# https://gist.github.com/joncardasis/cc67cfb160fa61a0457d6951eff2aeae

logging.basicConfig(level=logging.DEBUG, format='%(name)s: %(message)s',)

class MyWebServer(socketserver.BaseRequestHandler):

    def __init__(self, request, client_address, server):
        self.logger = logging.getLogger('MyWebServer')
        self.content_dir = 'www'
        # self.logger.debug('__init__')
        socketserver.BaseRequestHandler.__init__(self, request, client_address, server)

    def setup(self):
        # self.logger.debug('setup')
        return socketserver.BaseRequestHandler.setup(self)

    def handle(self):
        # self.logger.debug('handle')
        self.data = self.request.recv(1024).strip().decode()

        # Put heads into dictionary for future use (No longer needed)
        # split_headers = self.data.split(' ')
        # headers = {}
        # for item in split_headers:
        #     if ": " in item:
        #         split_item = item.split(": ")
        #         headers[split_item[0]] = split_item[1]

        response = ""
        type = ""
        request_method = self.data.split(' ')[0]

        # Set reply to get GET method
        if request_method == "GET":
            file_requested = self.data.split(" ")[1]
            # Check for route moving
            if "css" not in file_requested:
                type = "text/html"
                if "index.html" not in file_requested:
                    # 301 Moved Permanently checking
                    if file_requested[-1] != "/":
                        response_header = self.generate_headers(301, type)
                        response_header += "Location: " + file_requested + "/"
                        self.request.sendall(response_header.encode())
                        return
                    else:
                        file_requested += "index.html"
            else:
                type = "text/css"
            filepath = self.content_dir + file_requested

            try:
                f = open(filepath, 'rb')
                response_data = f.read()
                f.close()
                response_header = self.generate_headers(200, type)

            except Exception as e:
                # self.logger.debug("File not found. Serving 404 page.")
                response_header = self.generate_headers(404, type)
                response_data = b"<html><body><center><h1>Error 404: File not found</h1></center><p>Head back to <a href='/index.html'>Index</a>.</p></body></html>"

            response = response_header.encode()
            response += response_data
            self.request.sendall(response)
            return
        # For everything else, return a 405
        else:
            response = self.generate_headers(405, "text/html").encode()
            self.request.sendall(response)
            return

    def finish(self):
        # self.logger.debug('finish')
        return socketserver.BaseRequestHandler.finish(self)

    def generate_headers(self, response_code, type):
        header = ''
        if response_code == 200:
            header += 'HTTP/1.1 200 OK\n'
        elif response_code == 301:
            header += 'HTTP/1.1 301 Moved Permanently\n'
        elif response_code == 404:
            header += 'HTTP/1.1 404 Not Found\n'
        elif response_code == 405:
            header += 'HTTP/1.1 405 Method Not Allowed\n'

        time_now = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
        header += 'Content-Type: {ct}\n'.format(ct=type)
        header += 'Date: {now}\n'.format(now=time_now)
        return header

if __name__ == "__main__":
    HOST, PORT = "localhost", 8080

    socketserver.TCPServer.allow_reuse_address = True
    # Create the server, binding to localhost on port 8080
    server = socketserver.TCPServer((HOST, PORT), MyWebServer)

    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    server.serve_forever()
