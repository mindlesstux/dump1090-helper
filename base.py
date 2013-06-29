import re, os, webapp2

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
        self.lastupdate = datetime.utcnow()

        # Is this plane in the KML/JSON?
        self.showKML = True

# Lets group the planes together
class Planes():
    def __init__(self):
        self.planes = []