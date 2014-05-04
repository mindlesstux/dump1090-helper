__author__ = 'bdavenport'

from base import *
from planes import Planes
from google.appengine.api import urlfetch
from google.appengine.api import memcache

import logging

# Need to do something nice here so people know what this is, or just make it blank
class MainHandler(BasicHandler):
    def get(self):
        self.redirect('/dump1090/gmap.html')


class JSONDataHandler(BasicHandler):
    def get(self, icao):
        self.response.headers.add_header("Access-Control-Allow-Origin", "*")
        self.response.headers['Content-Type'] = 'application/json'
        plane = planes.pullPlane(str(icao).upper())
        out = plane.generateJSON()
        self.response.write(str(out))

# Warms up the python instance, aka pulls the plane lists and sets all the instance variables to everyone is in sync
class WarmupHandler(webapp2.RequestHandler):
    def get(self):
        pass

class TestHandler(BasicHandler):
    def get(self, start=0, max=0):
        self.tohtml['start'] = int(start)
        self.tohtml['max'] = int(max)
        self.render_template('secure/ImportAircraft.html')

class DynamicData(BasicHandler):
    def get(self, source):
        # This is a hack till there is a backend to update
        DataLocations = {}
        DataLocations["kclt"]   = "http://chronos.rpi.mindlesstux.com/dump1090/data.json"
        DataLocations["rtlsdr"] = "http://adsb.rtlsdr.org/data.json"
        DataLocations["eftu"]   = "http://map.ideat.eu:2095/data"

        if source in DataLocations:
            memKey = "source-%s" % source
            x = memcache.get(key=memKey)
            if x is None:
                result = urlfetch.fetch(DataLocations[source])
                if result.status_code == 200:
                    memcache.set(key=memKey, time=6, value=result.content)
                    self.response.write(str(result.content))
                else:
                    logging.warn(result.status_code)
                    self.error(502)
            else:
                self.response.write(str(x))
        else:
            self.error(404)



planes = Planes()

app = webapp2.WSGIApplication([
                                  ("/_ah/warmup", WarmupHandler),
                                  ('/', MainHandler),
                                  ('/test/(.*)/(.*)/', TestHandler),
                                  ('/secure/importAircraft', "datastore.ImportAircraft"),
                                  ('/dynamic/data/(.*).json', DynamicData),
                                  ('/search/icao24/(.*).json', JSONDataHandler),
                              ], debug=True)