__author__ = 'bdavenport'

from base import *
from planes import Planes

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

planes = Planes()

app = webapp2.WSGIApplication([
                                  ("/_ah/warmup", WarmupHandler),
                                  ('/', MainHandler),
                                  ('/secure/initalizeDS', "datastore.InitalizeDSHandler"),
                                  ('/search/icao24/(.*).json', JSONDataHandler),
                              ], debug=True)