from twisted.internet import reactor, threads
from twisted.internet.protocol import Protocol, ReconnectingClientFactory
from twisted.python import log
import time
import urllib, urllib2
import json
import sys

log.startLogging(sys.stdout)

def push(funcdata):
	log.msg("Msgs: %s" % len(funcdata))
		
	data = urllib.urlencode(dict(messages=json.dumps(funcdata)))
	request = urllib2.Request("http://dump1090-helper.appspot.com/postmessages", data)
	request.add_header('User-agent', 'dumpHelper/0.1 (%s)' % ('UserKeyHere') )
	response = urllib2.urlopen(request)

class Echo(Protocol):
    def __init__(self):
        self.messages = []
        self.last_push = time.time()

    def dataReceived(self, data):
        self.messages.append([str(time.time()), data.rstrip('\n')])
        #stdout.write("Msg: %s -- Data: %s" % (self.messages, data))
	if time.time() > self.last_push + 5:
		push(self.messages)
		self.messages = []
		self.last_push = time.time()

		
class EchoClientFactory(ReconnectingClientFactory):
    def startedConnecting(self, connector):
        log.msg('Started to connect.')

    def buildProtocol(self, addr):
        log.msg('Connected.')
        log.msg('Resetting reconnection delay')
        self.resetDelay()
        return Echo()

    def clientConnectionLost(self, connector, reason):
        log.msg('Lost connection.  Reason:', reason)
        ReconnectingClientFactory.clientConnectionLost(self, connector, reason)

    def clientConnectionFailed(self, connector, reason):
        log.msg('Connection failed. Reason:', reason)
        ReconnectingClientFactory.clientConnectionFailed(self, connector, reason)

reactor.connectTCP("127.0.0.1", 30002, EchoClientFactory())
reactor.run()
