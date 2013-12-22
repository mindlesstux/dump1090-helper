#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
import datetime, json, logging, webapp2

from base import *

from google.appengine.api import taskqueue

PlaneClass = Planes()

# Need to do something nice here so people know what this is, or just make it blank
class MainHandler(BasicHandler):
    def get(self):
        self.redirect('/dump1090/gmap.html')

# Test to do XSS so we can provide JSON to our viewers/clients from an alt domain
class TestSHandler(BasicHandler):
    def get(self):
        self.response.headers.add_header("Access-Control-Allow-Origin", "*")
        self.response.headers['Content-Type'] = 'application/javascript'
        self.response.write('// Hello world!')

class TestJHandler(BasicHandler):
    def get(self):
        self.response.headers.add_header("Access-Control-Allow-Origin", "*")
        self.response.headers['Content-Type'] = 'application/json'
        self.response.write('{}')

class JSONDataHandler(BasicHandler):
    def get(self):
        self.response.headers.add_header("Access-Control-Allow-Origin", "*")
        self.response.headers['Content-Type'] = 'application/json'
        out = PlaneClass.generateJSON()
        self.response.write(out)

class JSONTrailDataHandler(BasicHandler):
    def get(self):
        self.response.headers.add_header("Access-Control-Allow-Origin", "*")
        self.response.headers['Content-Type'] = 'application/json'
        out = PlaneClass.generateJSONTrail(self.request.get('icao'))
        self.response.write(out)

class KMLHandler(BasicHandler):
    def get(self):
        self.response.headers.add_header("Access-Control-Allow-Origin", "*")
        self.response.headers['Content-Type'] = 'application/vnd.google-earth.kml+xml'
        out = PlaneClass.generateKML()
        self.response.write(out)

# Idea to pull the SBS-1 data feed in via 5 second chunks from a client script
# This part is just for fun, and should not be pushed as primary reason
# Though if this app goes paid then there are sockets we can make use of to directly read the data
class MsgPushHandler(webapp2.RequestHandler):
    def post(self):
        taskqueue.add(url='/secure/tasks/processjson', params={'messages': self.request.get('messages')}, queue_name='planeCruncher')

class TaskPlaneJSON(webapp2.RequestHandler):
    def post(self):
        x = str(self.request.get('messages'))
  
        try:
            msgs = json.JSONDecoder().decode(json.loads(x))
            PlaneClass.processJSON(msgs)
        except ValueError, e:
            logging.error("ValueError: %s" % e)
            logging.debug(json.loads(x))
        except:
            logging.error("Problem decoding/processing JSON")

class CronPlaneReaper(webapp2.RequestHandler):
    def get(self):
        PlaneClass.reaper()

# Warms up the python instance, aka pulls the plane lists and sets all the instance variables to everyone is in sync
class WarmupHandler(webapp2.RequestHandler):
    def get(self):
        PlaneClass.Warmup()

app = webapp2.WSGIApplication([
                                  ("/_ah/warmup", WarmupHandler),
                                  ('/', MainHandler),
                                  ('/script.js', TestSHandler),
                                  ('/rnav.json', TestJHandler),
                                  ('/kml/planes.kml', KMLHandler),
                                  ('/json/serverpush', MsgPushHandler),
                                  ('/json/data.json', JSONDataHandler),
                                  ('/json/trail.json', JSONTrailDataHandler),
                                  ('/secure/cron/reaper', CronPlaneReaper),
                                  ('/secure/tasks/processjson', TaskPlaneJSON),
                              ], debug=True)
