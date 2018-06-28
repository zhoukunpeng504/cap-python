# coding:utf8


import socket
socket.setdefaulttimeout(3)
from twisted.internet import  reactor
from twisted.web.client import getPage,HTTPClientFactory

from twisted.internet.defer import Deferred
from twisted.internet.defer import inlineCallbacks


def startedConnecting(self, connector):
    def timeout():
        connector.stopConnecting()
    timeoutCall = reactor.callLater(self.timeout, timeout)
    self.deferred.addBoth(self._cancelTimeout, timeoutCall)
HTTPClientFactory.startedConnecting = startedConnecting

def callback(*args,**kwargs):
    print "success!!"

def errback(a):
    print "error",a

def test():
    defer = getPage("http://www.wolover.com",timeout=3)
    defer.addCallback(callback)
    defer.addErrback(errback)

@inlineCallbacks
def test1():
    try:
        result = yield getPage("http://www.wolover.com",timeout=3)
    except Exception as e :
        print str(e)


test1()
reactor.run()
