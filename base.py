import datetime
import re
import os
import logging
import webapp2

from google.appengine.api import memcache
from webapp2_extras import jinja2

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
        self.altitude = 0
        self.groundspeed = 0
        self.track = 0

        # Where are they? floats
        self.latitude = 0
        self.longitude = 0

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

        # Is this plane in the KML/JSON?
        self.showKML = True

# Lets group the planes together
class Planes():
    def __init__(self):
        # Our planes
        self.planes = {}
        self.planeicaos = []

    def Warmup(self):
        data = memcache.get(planeicaos)
        if data is not None:
            for icao in data:
                self.planes[icao] = self.pullPlane(icao)

    def newPlane(self, icao):
        plane = Plane()
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

    # Update our local array of planes and update memcache for other instances
    def pushPlane(self, icao, plane):
        self.planes[icao] = plane
        self.planeicaos.append(str(icao))
        memcache.set(key=icao, value=plane, time=900)

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

    def processBasestation(self, msgs):
        for msg in msgs:
            tmp = msg.split(',')
            # logging.info(tmp)
