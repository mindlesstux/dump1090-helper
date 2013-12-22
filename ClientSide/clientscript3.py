__author__ = 'bdavenport'

import csv
import datetime
import json
import socket
import sys
import time
import urllib,urllib2
import yaml

# Attempt to load our configuration
try:
    f = open('config.yaml')
    config = yaml.load(f)
    f.close()
except IOError:
    config = {}

print config

# Lets make a plane
class Plane():
    # This is our plane, there shall be non other like it (hopefully).
    def __init__(self):
        # Session instance of found plane, database driven, int
        self.session = False

        # icao (6) and Flight(8) codes,
        self.icao = False
        self.flightid = False

        # Altitude, GroundSpeed, and Track, ints
        self.altitude = None
        self.groundspeed = None
        self.track = None

        # Where are they? floats
        self.latitude = None
        self.longitude = None

        # Vertical Rate, altitude changes? int
        self.virticalrate = 0

        # Squawk
        self.squawk = False

        # Squawk Alert
        self.squawkalert = False

        # Emergency
        self.emergency = False

        # SPI (Ident) transponder
        self.spi = False

        # On the ground?
        self.isOnGround = False

        # Last time we updated any data
        self.seen_start = datetime.datetime.utcnow()
        self.lastupdate = datetime.datetime.utcnow()

        # This is the number of msgs, JSON count is number of msgs by json...
        self.msgcount = 0
        self.msgcountJSON = 0

        # Is this plane in the KML/JSON?
        self.showKML = True

        self.trail = []

        self.signal = []

# Lets group the planes together
class Planes():
    def __init__(self):
        # Our planes
        self.planes = {}
        self.lastreap = datetime.datetime.utcnow()

    def checkLocalPlane(self, icao):
        if icao in self.planes:
            return True
        else:
            return False

    def newPlane(self, icao):
        plane = Plane()
        plane.icao = icao
        self.pushPlane(plane=plane)
        #print "Adding new plane %s, now tracking %s planes" % (plane.icao, self.planes.__len__())

    def pushPlane(self, plane):
        plane.lastupdate = datetime.datetime.utcnow()
        self.planes[plane.icao] = plane

    def pushTrail(self, plane):
        pass

    def pullPlane(self, icao):
        del self.planes[icao]
        #print "Removing %s" % icao

    def getPlane(self, icao):
        return self.planes[icao]

    # DECRYPT THE SBS - http://www.homepages.mcb.net/bones/SBS/Article/Barebones42_Socket_Data.htm
    def handleMSG1(self, msg, plane):
        pushThis = False
        if plane.flightid != msg[10]:
            plane.flightid = msg[10]
            pushThis = True

        if pushThis:
            self.pushPlane(plane)

    def handleMSG2(self, msg, plane):
        pushThis = False
        if plane.altitude != msg[11]:
            plane.altitude = msg[11]
            pushThis = True

        if plane.groundspeed != msg[12]:
            plane.groundspeed = msg[12]
            pushThis = True

        if plane.track != msg[13]:
            plane.track = msg[13]
            pushThis = True

        # Lat/Long
        moved = False
        if plane.latitude != msg[14]:
            plane.latitude = msg[14]
            moved = True
            pushThis = True
        if plane.longitude != msg[15]:
            plane.longitude = msg[15]
            moved = True
            pushThis = True

        if plane.isOnGround != msg[21]:
            plane.isOnGround = msg[21]
            pushThis = True

        if pushThis:
            self.pushPlane(plane)

        if moved:
            self.pushTrail(plane)

    def handleMSG3(self, msg, plane):
        pushThis = False
        if plane.altitude != msg[11]:
            plane.altitude = msg[11]
            pushThis = True

        # Lat/Long
        moved = False
        if plane.latitude != msg[14]:
            plane.latitude = msg[14]
            moved = True
            pushThis = True
        if plane.longitude != msg[15]:
            plane.longitude = msg[15]
            moved = True
            pushThis = True

        if plane.squawkalert != msg[18]:
            plane.squawkalert = msg[18]
            pushThis = True

        if plane.emergency != msg[19]:
            plane.emergency = msg[19]
            pushThis = True

        if plane.spi != msg[20]:
            plane.spi = msg[20]
            pushThis = True

        if plane.isOnGround != msg[21]:
            plane.isOnGround = msg[21]
            pushThis = True

        if pushThis:
            self.pushPlane(plane)

        if moved:
            self.pushTrail(plane)

    def handleMSG4(self, msg, plane):
        pushThis = False
        if plane.groundspeed != msg[12]:
            plane.groundspeed = msg[12]
            pushThis = True

        if plane.track != msg[13]:
            plane.track = msg[13]
            pushThis = True

        if plane.virticalrate != msg[16]:
            plane.virticalrate = msg[16]
            pushThis = True

        if pushThis:
            self.pushPlane(plane)

    def handleMSG5(self, msg, plane):
        pushThis = False
        if plane.altitude != msg[11]:
            plane.altitude = msg[11]
            pushThis = True

        if plane.squawkalert != msg[18]:
            plane.squawkalert = msg[18]
            pushThis = True

        if plane.spi != msg[20]:
            plane.spi = msg[20]
            pushThis = True

        if plane.isOnGround != msg[21]:
            plane.isOnGround = msg[21]
            pushThis = True

        if pushThis:
            self.pushPlane(plane)

    def handleMSG6(self, msg, plane):
        pushThis = False
        if plane.altitude != msg[11]:
            plane.altitude = msg[11]
            pushThis = True

        if plane.squawk != msg[17]:
            plane.squawkt = msg[17]
            pushThis = True

        if plane.squawkalert != msg[18]:
            plane.squawkalert = msg[18]
            pushThis = True


        if plane.emergency != msg[19]:
            plane.emergency = msg[19]
            pushThis = True

        if plane.spi != msg[20]:
            plane.spi = msg[20]
            pushThis = True

        if plane.isOnGround != msg[21]:
            plane.isOnGround = msg[21]
            pushThis = True

        if pushThis:
            self.pushPlane(plane)

    def handleMSG7(self, msg, plane):
        pushThis = False
        if plane.altitude != msg[11]:
            plane.altitude = msg[11]
            pushThis = True

        if plane.isOnGround != msg[21]:
            plane.isOnGround = msg[21]
            pushThis = True

        if pushThis:
            self.pushPlane(plane)

    def handleMSG8(self, msg, plane):
        pushThis = False

        if plane.isOnGround != msg[21]:
            plane.isOnGround = msg[21]
            pushThis = True

        if pushThis:
            self.pushPlane(plane)

    def handleMSG(self, msg):
        msg[0] = str(msg[0])        # MSG
        msg[1] = int(msg[1])        # Type
        msg[4] = str(msg[4])        # ICAO
        try:
            msg[10] = str(msg[10])      # CallSign
        except:
            pass
        try:
            msg[11] = int(msg[11])      # Altitude
        except:
            pass
        try:
            msg[12] = int(msg[12])      # Ground Speed
        except:
            pass
        try:
            msg[13] = int(msg[13])      # Track
        except:
            pass
        try:
            msg[14] = float(msg[14])    # LAT
        except:
            pass
        try:
            msg[15] = float(msg[15])    # LNG
        except:
            pass
        try:
            msg[17] = int(msg[17])      # Squawk
        except:
            pass
        try:
            msg[18] = bool(int(msg[18]))     # Squawk Change!
        except:
            pass
        try:
            msg[19] = bool(int(msg[19]))     # Emergency
        except:
            pass
        try:
            msg[20] = bool(int(msg[20]))     # SPI Ident
        except:
            pass
        try:
            msg[21] = bool(int(msg[21]))     # Is Ground?
        except:
            pass

        if not self.checkLocalPlane(msg[4]):
            self.newPlane(icao=msg[4])

        plane = self.getPlane(icao=msg[4])

        if msg[0] == "MSG":
            if msg[1] == 1:
                self.handleMSG1(msg, plane)
            elif msg[1] == 3:
                self.handleMSG3(msg, plane)
            elif msg[1] == 4:
                self.handleMSG4(msg, plane)
            elif msg[1] == 5:
                self.handleMSG5(msg, plane)
            elif msg[1] == 6:
                self.handleMSG6(msg, plane)
            elif msg[1] == 7:
                self.handleMSG7(msg, plane)
            elif msg[1] == 8:
                self.handleMSG8(msg, plane)
            else:
                print "Unknown MSG#: %s" % msg[1]
                print msg
        else:
                print "Unknown Type: %s" % msg[0]

        self.reaper()

        del plane

    def reaper(self):
        now = datetime.datetime.utcnow()
        timedelta =  now - self.lastreap
        if int(timedelta.total_seconds()) > config['reap']['interval']:
            pullList = []
            #print "----------------------------------------------------"
            for icao in self.planes:
                plane = self.getPlane(icao)
                timedelta = now - plane.lastupdate
                #print "%s %s" % (icao, int(timedelta.total_seconds()))
                if int(timedelta.total_seconds()) > config['reap']['hide']:
                    plane.showKML = False
                    self.planes[plane.icao] = plane

                if int(timedelta.total_seconds()) > config['reap']['remove']:
                    pullList.append(str(plane.icao))
                    #print "Adding %s to pullList: %s" % (plane.icao, pullList)


            if pullList != []:
                for icao in pullList:
                    self.pullPlane(icao)


            self.lastreap = datetime.datetime.utcnow()


'''
# This is for STDIN usage, socket would be better.
try:
    buff = ''
    while True:
        buff += sys.stdin.read(1)
        if buff.endswith('\n'):
            msg = str(buff[:-2]).split(',')
            planes.handleMSG(msg=msg)
            del msg
            del plane
            buff = ''
except KeyboardInterrupt:
   sys.stdout.flush()
   pass
'''


def get_constants(prefix):
    """Create a dictionary mapping socket module constants to their names."""
    return dict( (getattr(socket, n), n)
                 for n in dir(socket)
                 if n.startswith(prefix)
                 )

planes = Planes()

try:
    while True:
        families = get_constants('AF_')
        types = get_constants('SOCK_')
        protocols = get_constants('IPPROTO_')

        # Create a TCP/IP socket
        sock = socket.create_connection((str(config['host']), int(config['port'])))

        print >>sys.stderr, 'Family  :', families[sock.family]
        print >>sys.stderr, 'Type    :', types[sock.type]
        print >>sys.stderr, 'Protocol:', protocols[sock.proto]
        print >>sys.stderr

        try:
            buff = ''
            while True:
                buff += sock.recv(1)
                if buff.endswith('\n'):
                    msg = str(buff[:-2]).split(',')
                    planes.handleMSG(msg=msg)
                    del msg
                    buff = ''

        finally:
            sock.close()

except KeyboardInterrupt:
    sys.stdout.flush()
    pass