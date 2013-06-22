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

class MainHandler(webapp2.RequestHandler):
    def get(self):
        self.response.write('Hello world!')

class MsgPushHandler(webapp2.RequestHandler):
    def post(self):
	msgs = json.loads(self.request.get('messages'))
	logging.debug(msgs)
        logging.debug("Messages: %s" % len(msgs))
	del msgs

app = webapp2.WSGIApplication([
    ('/', MainHandler),
    ('/postmessages', MsgPushHandler),
], debug=True)
