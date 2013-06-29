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

class MainHandler(BasicHandler):
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