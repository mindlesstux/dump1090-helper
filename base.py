__author__ = 'bdavenport'

import re
import os
import webapp2

from google.appengine.ext import ndb
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


