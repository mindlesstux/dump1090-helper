__author__ = 'bdavenport'

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