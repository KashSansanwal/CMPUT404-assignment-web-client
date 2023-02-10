#!/usr/bin/env python3
# coding: utf-8
# Copyright 2016 Abram Hindle, https://github.com/tywtyw2002, and https://github.com/treedust
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

# Do not use urllib's HTTP GET and POST mechanisms.
# Write your own HTTP GET and POST
# The point is to understand what you have to send and get experience with it

import sys
import socket
import re
# you may use urllib to encode data appropriately
import urllib.parse

def help():
    print("httpclient.py [GET/POST] [URL]\n")

class HTTPResponse(object):
    def __init__(self, code=200, body=""):
        self.code = code
        self.body = body

class HTTPClient(object):
    #def get_host_port(self,url):

    # connect to the host and port
    def connect(self, host, port):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((host, port))
        return None

    # read code from the socket
    def get_code(self, data):
        response = data.split('\r\n')[0]
        code = response.split(" ")[1]
        return int(code)

    # read headers from the socket
    def get_headers(self,data):
        headers = data.split('\r\n\r\n')
        return headers[0]

    # read body from the socket
    def get_body(self, data):
        body = data.split('\r\n\r\n')
        return body[1]
    
    # send data over the socket
    def sendall(self, data):
        self.socket.sendall(data.encode('utf-8'))
        
    # close the socket
    def close(self):
        self.socket.close()

    # read everything from the socket
    def recvall(self, sock):
        buffer = bytearray()
        done = False
        while not done:
            part = sock.recv(1024)
            if (part):
                buffer.extend(part)
            else:
                done = not part
        return buffer.decode('utf-8')

    def GET(self, url, args=None):
        # Parse URL
        url_par = urllib.parse.urlparse(url)

        # Unpack the result of urlparse into separate variables
        host, port, scheme = url_par.hostname, url_par.port, url_par.scheme

        # If port not given set default port
        if not port:
            port = self.get_default_port(scheme)

        # Connect to host
        self.connect(host, port)

        # Set path if its none
        path = '/'
        if url_par.path:
            path = url_par.path

        # Send request
        request = "GET {} HTTP/1.1\r\nHost: {}\r\nConnection:close\r\n\r\n".format(
            path,
            host
        )
        self.sendall(request)

        # Receive response
        response = self.recvall(self.socket)

        # Parse response
        code, body = self.get_code(response), self.get_body(response)
        print(code)
        print(self.get_headers(response))
        print(body)

        # Close connection
        self.close()
        
        return HTTPResponse(code, body)

    def POST(self, url, args=None):
        # Parse URL
        url_par = urllib.parse.urlparse(url)

        # Unpack the result of urlparse into separate variables
        host, port, scheme = url_par.hostname, url_par.port, url_par.scheme

        # If port not given set default port
        if not port:
            port = self.get_default_port(scheme)

        # Parse post arguments
        en_arguments = urllib.parse.urlencode('')
        if args:
            en_arguments = urllib.parse.urlencode(args)

        # Connect to host
        self.connect(host, port)

        # Set path if its none
        path = '/'
        if url_par.path:
            path = url_par.path

        # Send request
        request = "POST {} HTTP/1.1\r\nHost: {}\r\nContent-Type: application/x-www-form-urlencoded\r\nContent-Length: {}\r\nConnection: close\r\n\r\n{}".format(
            path,
            host,
            len(en_arguments),
            en_arguments
        )
        self.sendall(request)

        # Receive response
        response = self.recvall(self.socket)

        # Parse response
        code, body = self.get_code(response), self.get_body(response)
        print(code)
        print(self.get_headers(response))
        print(body)

        # Close connection
        self.close()
        return HTTPResponse(code, body)

    def get_default_port(self, scheme):
        if scheme == "http":
            return 80
        elif scheme == "https":
            return 443

    def command(self, url, command="GET", args=None):
        if (command == "POST"):
            return self.POST( url, args )
        else:
            return self.GET( url, args )
    
if __name__ == "__main__":
    client = HTTPClient()
    command = "GET"
    if (len(sys.argv) <= 1):
        help()
        sys.exit(1)
    elif (len(sys.argv) == 3):
        print(client.command( sys.argv[2], sys.argv[1] ))
    else:
        print(client.command( sys.argv[1] ))
