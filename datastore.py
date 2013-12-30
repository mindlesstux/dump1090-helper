__author__ = 'bdavenport'

from google.appengine.ext import ndb
from base import *

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

class NATFIX(ndb.Model):
    id = ndb.StringProperty()
    geo = ndb.GeoPtProperty()
    artcc = ndb.StringProperty()
    state = ndb.StringProperty()
    type = ndb.StringProperty()

class AirCraft(ndb.Model):
    icao24 = ndb.StringProperty(indexed=True)
    registration = ndb.StringProperty(default="NO-REG")
    manufacture = ndb.StringProperty(default=" ")
    typeCode = ndb.StringProperty(default="@@@", indexed=True)
    model = ndb.StringProperty(default=" ")
    operator = ndb.StringProperty(default="@@@")
    date_update = ndb.DateTimeProperty(auto_now=True)
    date_added = ndb.DateTimeProperty(auto_now_add=True)
    flag_new = ndb.BooleanProperty(default=True)

class InitalizeDSHandler(BasicHandler):
    def get(self):
        tmp = AirCraft()
        tmp.icao24 = "FFDDCC"
        tmp.registration = "TESTTEST"
        tmp.manufacture = "MFG TEST"
        tmp.typeCode = "B737"
        tmp.model = "737-3H4"
        tmp.operator = "TETS"
        tmp.flag_new = False
        tmp.put()
        self.redirect('/dump1090/gmap.html')