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
        self.lastupdate = datetime.datetime.utcnow()

        # This is the number of msgs, JSON count is number of msgs by json...
        self.msgcount = 0
        self.msgcountJSON = 0

        # Is this plane in the KML/JSON?
        self.showKML = True

# Lets group the planes together
class Planes():
    def __init__(self):
        # Our planes
        self.planes = {}
        self.planeicaos = []

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

            if plane.msgcountJSON is not msg['messages']:
                if bool(msg['validaltitude']) is True:
                    plane.altitude = msg['altitude']

                if bool(msg['validtrack']) is True:
                    plane.track = int(msg['track'])
                else:
                    plane.track = None

                if bool(msg['validposition']) is True:
                    plane.latitude = msg['lat']
                    plane.longitude = msg['lon']
                else:
                    plane.latitude = None
                    plane.longitude = None

                if plane.squawk is not msg['squawk']:
                    plane.squawk = msg['squawk']

                if plane.flightid is not msg['flight']:
                    plane.flightid = msg['flight']

                if int(msg['speed']) is not 0:
                    plane.groundspeed = int(msg['speed'])

                plane.msgcountJSON = msg['messages']
                plane.msgcount += 1

                self.pushPlane(msg['hex'], plane)

            del plane

    def generateJSON(self):
        jsonstr = []
        for plane in self.planes:
            planestr = {}
            planestr['hex'] = self.planes[plane].icao
            planestr['squawk'] = self.planes[plane].squawk
            planestr['flight'] = self.planes[plane].flightid

            if self.planes[plane].latitude is not None and self.planes[plane].longitude is not None:
                planestr['validposition'] = 1
            else:
                planestr['validposition'] = 0
            planestr['lat'] = self.planes[plane].latitude
            planestr['lon'] = self.planes[plane].longitude

            if self.planes[plane].altitude is not None:
                planestr['validaltitude'] = 1
                planestr['altitude'] = self.planes[plane].altitude
            else:
                planestr['validaltitude'] = 0
                planestr['altitude'] = ""

            if self.planes[plane].groundspeed is not None:
                planestr['speed'] = self.planes[plane].groundspeed
            else:
                planestr['speed'] = ""

            if self.planes[plane].track is not None:
                planestr['validtrack'] = 1
                planestr['track'] = self.planes[plane].track
            else:
                planestr['validtrack'] = 0
                planestr['track'] = ""

            now = datetime.datetime.now()
            planedate = self.planes[plane].lastupdate
            timedelta = now - planedate
            planestr['seen'] = "%s" % int(timedelta.total_seconds())

            planestr['messages'] = self.planes[plane].msgcount

            jsonstr.append(planestr)
        jsondump = json.dumps(jsonstr)
        #logging.info(jsondump)
        return jsondump
