import datetime
import json
import re
import os
import logging
import webapp2

from google.appengine.api import memcache
from google.appengine.ext import ndb
from webapp2_extras import jinja2

# RNAV WPTs
class WPT_RNAV(ndb.Model):
    name = ndb.StringProperty()
    location = ndb.GeoPtProperty()
    state = ndb.StringProperty()
    country = ndb.StringProperty()

# Multiple RNAV WPTs make a route
# Schema prefered, 1-1 all till common then common-out
class WPT_RNAV_ROUTE(ndb.Model):
    airport = ndb.StringProperty()
    name = ndb.StringProperty()
    sequence = ndb.PickleProperty()

# Log the trails that the planes make once they are reaped off
class PLN_TRAIL(ndb.Model):
    time = ndb.DateTimeProperty(auto_now=True, auto_now_add=True)
    plane = ndb.StringProperty()
    trail = ndb.JsonProperty(compressed=True)

class PLN_LOG(ndb.Model):
    icao = ndb.StringProperty()
    flightid = ndb.StringProperty()
    seen_start = ndb.DateTimeProperty()
    seen_stop = ndb.DateTimeProperty()
    trail = ndb.KeyProperty(kind=PLN_TRAIL)


# Handles a bit more than standard webapp2 server
class BasicHandler(webapp2.RequestHandler):
    def __init__(self, request=None, response=None):
        self.initialize(request, response)

        # If we are running on dev, make it so, otherwise use production info
        if os.environ['SERVER_SOFTWARE'].startswith('Dev'):
            self.is_dev = True
            self.datacenter = "dev"
        else:
            self.is_dev = False
            self.datacenter = os.environ['DATACENTER']

        self.server_version = os.environ['SERVER_SOFTWARE']

        self.code_version = re.sub("([a-z0-9]*)\.([0-9]*)", "\g<1>""", os.environ['CURRENT_VERSION_ID'])

        # Prep an array for use in passing to the render
        self.tohtml = {
            # About our environment
            'is_dev': self.is_dev,
            'datacenter': self.datacenter,
            'server_version': self.server_version,
            'code_version': self.code_version,
        }

        @webapp2.cached_property
        def jinja2(self):
            return jinja2.get_jinja2(app=self.app)

        def render_template(self, filename):
            template_args = self.tohtml
            self.response.write(self.jinja2.render_template(filename, **template_args))

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
        self.planeicaos = []

        self.datacenter = os.environ['DATACENTER']
        self.server_instance = os.environ['INSTANCE_ID']
        self.server_version = os.environ['SERVER_SOFTWARE']
        self.code_version = re.sub("([a-z0-9]*)\.([0-9]*)", "\g<1>""", os.environ['CURRENT_VERSION_ID'])


    def Warmup(self):
        data = memcache.get('planeicaos')
        if data is not None:
            for icao in data:
                self.planes[icao] = self.pullPlane(icao)

    def newPlane(self, icao):
        plane = Plane()
        plane.icao = icao
        self.pushPlane(icao, plane)
        return plane

    def checkLocalPlane(self, icao):
        if icao in self.planes:
            return True
        else:
            return False

    def checkMemcachePlane(self, icao):
        data = memcache.get(icao)
        if data is not None:
            return True
        else:
            return False

    def reaper(self):
        logging.debug("Planes before reap: %s" % len(self.planeicaos))
        to_pop = []
        for x in self.planes:
            plane = self.planes[x]
            now = datetime.datetime.now()
            planedate = plane.lastupdate
            timedelta = now - planedate
            if timedelta.total_seconds() > 300:
            	plane.seen_stop = datetime.datetime.utcnow()
            	if len(plane.trail) > 0:
                    tmp_trl = PLN_TRAIL(plane=plane.icao, trail=plane.trail)
                    tmp_trl.put()
                    tmp_pln = PLN_LOG(icao=plane.icao, flightid=plane.flightid, seen_start=plane.seen_start, seen_stop=plane.seen_stop, trail=tmp_trl.key)
                    tmp_pln.put()
                    del tmp_trl
                else:
                    tmp_pln = PLN_LOG(icao=plane.icao, flightid=plane.flightid, seen_start=plane.seen_start, seen_stop=plane.seen_stop)
                    tmp_pln.put()

                del tmp_pln

                to_pop.append(x)

        for x in to_pop:
            logging.debug("Removing '%s' from list" % x)
            self.planes.pop(x)
            self.planeicaos.remove(x)
            memcache.delete(key=plane.icao)
            memcache.set(key='planeicaos', value=self.planeicaos, time=1800)

        logging.debug("Planes after reap:  %s" % len(self.planeicaos))

    # Update our local array of planes and update memcache for other instances
    def pushPlane(self, icao, plane):
        plane.lastupdate = datetime.datetime.utcnow()
        self.planes[icao] = plane
        memcache.set(key=icao, value=plane, time=900)
        if icao not in self.planeicaos:
            self.planeicaos.append(str(icao))
            memcache.set(key='planeicaos', value=self.planeicaos, time=1800)

    # Grab this plane somehow...
    def pullPlane(self, icao):
        # Do we have this plane locally already?
        if self.checkLocalPlane(icao):
            localplane = self.planes[icao]
        else:
            localplane = None

        # Does the plane exist in memcache?
        if self.checkMemcachePlane(icao):
            remoteplane = memcache.get(icao)
        else:
            remoteplane = None

        # If we have both local and remote
        if localplane is not None and remoteplane is not None:
            # If the local copy is newer, push it
            if localplane.lastupdate > remoteplane.lastupdate:
                self.pushPlane(icao, localplane)
                return localplane
            else:
                return remoteplane
        elif localplane is None and remoteplane is not None:
            # Add localally and run with it
            self.pushPlane(icao, remoteplane)
            return remoteplane
        elif localplane is not None and remoteplane is None:
            # Should only happen if the key expires in memcache
            self.pushPlane(icao, localplane)
            return localplane
        else:
            plane = self.newPlane(icao)
            return plane

    def processJSON(self, msgs):
        for msg in msgs:
            plane = self.pullPlane(msg['hex'])

            # Need to change this to last updated w/ GMT/UTC conversion
            if plane.msgcountJSON is not msg['messages']:
                if bool(msg['validaltitude']) is True:
                    plane.altitude = msg['altitude']

                if bool(msg['validtrack']) is True:
                    plane.track = int(msg['track'])
                else:
                    plane.track = None

                if bool(msg['validposition']) is True:
                    if plane.latitude != float(msg['lat']) or plane.longitude != float(msg['lon']):
                        plane.latitude = float(msg['lat'])
                        plane.longitude = float(msg['lon'])
                        if plane.latitude > 90 or plane.latitude < -90 or plane.longitude > 180 or plane.longitude < -180:
                            logging.error("Plane out of bounds: %s @ %s, %s" % (plane.icao, msg['lat'], msg['lon']))
                            plane.latitude = None
                            plane.longitude = None
                            moved = False
                        else :
                            moved = True
                    else:
                        moved = False
                else:
                    plane.latitude = None
                    plane.longitude = None
                    moved = False

                if plane.squawk is not msg['squawk']:
                    plane.squawk = msg['squawk']

                if plane.flightid is not msg['flight']:
                    plane.flightid = msg['flight']

                if int(msg['speed']) is not 0:
                    plane.groundspeed = int(msg['speed'])

                plane.msgcountJSON = msg['messages']
                plane.msgcount += 1

                plane.signal = msg['signal']

                if plane.latitude is not None and plane.longitude is not None and moved is True:
                    plane.trail.append({'latitude': plane.latitude, 'longitude': plane.longitude, 'altitude': plane.altitude, 'track': plane.track})

                self.pushPlane(msg['hex'], plane)

            del plane

    def generateJSON(self):
        jsonstr = []
        serverstr = {"server_info": {"datacenter": self.datacenter, "instance": self.server_instance, "version_server": self.server_version, "version_software": self.code_version}}
        jsonstr.append(serverstr)

        planesstr = []
        for x in self.planes:
            plane = self.pullPlane(x)
            planestr = {}
            planestr['hex'] = plane.icao
            planestr['squawk'] = plane.squawk
            planestr['flight'] = plane.flightid

            if plane.latitude is not None and plane.longitude is not None:
                planestr['validposition'] = 1
                planestr['lat'] = plane.latitude
                planestr['lon'] = plane.longitude
            else:
                planestr['validposition'] = 0
                planestr['lat'] = ""
                planestr['lon'] = ""

            if plane.altitude is not None:
                planestr['validaltitude'] = 1
                planestr['altitude'] = plane.altitude
            else:
                planestr['validaltitude'] = 0
                planestr['altitude'] = ""

            if plane.groundspeed is not None:
                planestr['speed'] = plane.groundspeed
            else:
                planestr['speed'] = ""

            if plane.track is not None:
                planestr['validtrack'] = 1
                planestr['track'] = plane.track
            else:
                planestr['validtrack'] = 0
                planestr['track'] = ""

            planestr['signal'] = plane.signal

            now = datetime.datetime.now()
            planedate = plane.lastupdate
            timedelta = now - planedate
            planestr['seen'] = "%s" % int(timedelta.total_seconds())

            planestr['messages'] = plane.msgcount


            planesstr.append(planestr)

        jsonstr.append(planesstr)

        jsondump = json.dumps(jsonstr)
        #logging.info(jsondump)
        return jsondump


    def generateJSONTrail(self, icao):
        plane = self.pullPlane(icao)
        jsondump = json.dumps(plane.trail)
        return jsondump

    def generateKML(self):
        kmlstr = ""

        kmlheader = '''<?xml version="1.0" encoding="UTF-8"?>
<kml xmlns="http://www.opengis.net/kml/2.2" xmlns:gx="http://www.google.com/kml/ext/2.2" xmlns:kml="http://www.opengis.net/kml/2.2" xmlns:atom="http://www.w3.org/2005/Atom">
    <Document>
        <name>Dump1090-Helper</name>
        <Style id="plane">
            <IconStyle>
                <color>ff00ffff</color>
                <scale>1.4</scale>
                <Icon>
                    <href>http://maps.google.com/mapfiles/kml/shapes/airports.png</href>
                </Icon>
                <hotSpot x="0.5" y="0" xunits="fraction" yunits="fraction"/>
            </IconStyle>
            <ListStyle>
            </ListStyle>
            <PolyStyle>
			    <color>4cffaa55</color>
		    </PolyStyle>
        </Style>
'''
        kmlstr += kmlheader
        del kmlheader

        for x in self.planes:
            plane = self.pullPlane(x)
            if plane.latitude is not None and plane.longitude is not None:
                kmltmp = '''
        <Folder>
            <name>%s (%s)</name>
            <open>1</open>''' % (plane.flightid, plane.icao)
                kmlstr += kmltmp
                del kmltmp

                kmltmp = '''
            <Placemark>
                <name>%s (%s)</name>
                <description></description>
                <LookAt>
                    <longitude>%s</longitude>
                    <latitude>%s</latitude>
                </LookAt>
                <Point>
                    <extrude>1</extrude>
                    <altitudeMode>absolute</altitudeMode>
                    <coordinates>%s,%s,%s</coordinates>
                </Point>
                <styleUrl>#plane</styleUrl>
            </Placemark>
                ''' % (plane.flightid, plane.icao, plane.longitude, plane.latitude, plane.longitude, plane.latitude, (plane.altitude * 0.3048))
                kmlstr += kmltmp
                del kmltmp

                tmp_trail = plane.trail
                tmp = ""
                for x in tmp_trail:
                    tmp += '''%s,%s,%s
                    ''' % (x['longitude'], x['latitude'], (x['altitude'] * 0.3048))
                del tmp_trail

                kmltmp = '''
            <Placemark>
                <name>Trail</name>
                <LineString>
                    <extrude>1</extrude>
                    <tessellate>1</tessellate>
                    <altitudeMode>absolute</altitudeMode>
                    <coordinates>
                        %s
                    </coordinates>
                </LineString>
                <styleUrl>#plane</styleUrl>
            </Placemark>
        </Folder>
                ''' % (tmp)
                kmlstr += kmltmp
                del kmltmp

        kmlfooter = '''
    </Document>
</kml>'''
        kmlstr += kmlfooter
        del kmlfooter
        return kmlstr
