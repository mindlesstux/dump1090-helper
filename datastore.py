__author__ = 'bdavenport'

from google.appengine.ext import ndb

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
    registration = ndb.StringProperty()
    manufacture = ndb.StringProperty()
    typeCode = ndb.StringProperty(indexed=True)
    model = ndb.StringProperty()
    serialNo = ndb.StringProperty()
    operator = ndb.StringProperty()
    built = ndb.IntegerProperty()
    date_update = ndb.DateTimeProperty(auto_now=True)
    date_added = ndb.DateTimeProperty(auto_now_add=True)
