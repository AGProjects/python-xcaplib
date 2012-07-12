# Copyright (C) 2008-2012 AG Projects. See LICENSE for details.
#

from eventlet.green import socket, httplib, urllib2
from xcaplib import httpclient
from xcaplib import client


class HTTPConnection(httplib.HTTPConnection):
    def connect(self):
        address = httpclient.HostCache.get(self.host)
        self.sock = socket.create_connection((address, self.port), self.timeout)

class HTTPSConnection(httplib.HTTPSConnection):
    def connect(self):
        address = httpclient.HostCache.get(self.host)
        sock = socket.create_connection((address, self.port), self.timeout)
        ssl = socket.ssl(sock, self.key_file, self.cert_file)
        self.sock = httplib.FakeSocket(sock, ssl)

class HTTPHandler(urllib2.HTTPHandler):
    def http_open(self, req):
        return self.do_open(HTTPConnection, req)

class HTTPSHandler(urllib2.HTTPSHandler):
    def https_open(self, req):
        return self.do_open(HTTPSConnection, req)


class HTTPClient(httpclient.HTTPClient):
    def __init__(self, base_url, username, domain, password=None, auth=None):
        self.base_url = base_url
        if self.base_url[-1:] != '/':
            self.base_url += '/'
        handlers = [HTTPHandler, HTTPSHandler]
        password_manager = urllib2.HTTPPasswordMgr()
        password_manager.add_password(domain, self.base_url, username, password)
        if auth in ('digest', None):
            handlers.append(urllib2.HTTPDigestAuthHandler(password_manager))
        if auth in ('basic', None):
            handlers.append(urllib2.HTTPBasicAuthHandler(password_manager))
        self.opener = urllib2.build_opener(*handlers)


class XCAPClient(client.XCAPClient):
    HTTPClient = HTTPClient

