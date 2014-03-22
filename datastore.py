__author__ = 'bdavenport'

from google.appengine.ext import db
from google.appengine.ext import ndb
from base import *

import logging

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

class Aircraft(ndb.Model):
	mantma_id = ndb.IntegerProperty(default=-1, indexed=True)

	date_added = ndb.DateTimeProperty(auto_now_add=True)
	date_update = ndb.DateTimeProperty(auto_now=True)

	icao = ndb.StringProperty(indexed=True)
	icao_type = ndb.StringProperty(default="@@@")
	registration = ndb.StringProperty(default="")
	operator_flag = ndb.StringProperty(default="@@@")

	flag_new = ndb.BooleanProperty(default=True, indexed=True)
	flag_updated = ndb.BooleanProperty(default=False, indexed=True)
	flag_reviewed = ndb.BooleanProperty(default=False, indexed=False)
	flag_isMilitary = ndb.BooleanProperty(default=False, indexed=False)

	country = ndb.StringProperty(default="")
	country_short = ndb.StringProperty(default="")
	country_flag = ndb.StringProperty(default="NoFlag.png")

	serialNo = ndb.StringProperty(default="")
	manufacturer = ndb.StringProperty(default="")



class ImportAircraft(BasicHandler):
	def get(self, start=1, max=0):
		start = int(start)
		max = int(max)
		stop = start + 100
		with open('basestation.csv', 'r') as csvfile:
			if start is 1:
				max = len(list(csvfile))
			else:
				if stop > int(max):
					stop = int(max)

			logging.info('%s / %s' % (start, max))

			lines = csvfile.readlines()[start:stop]

			for row in lines:
				split = row.split(',')
				tmp = Aircraft()

				tmp.mantma_id = int(split[0])
				tmp.icao = split[3]
				tmp.registration = split[5]
				tmp.icao_type = split[6]
				tmp.operator_flag = split[8]


				tmp.put()

				del tmp

		stop += 1
		if max > stop:
			self.tohtml['stop'] = int(stop)
			self.tohtml['max'] = int(max)
			self.render_template('secure/ImportAircraft.html')
			#self.response.write("%s/%s/" % (stop, max))
			#self.redirect('/secure/import/basestation/%s/%s/' % (stop, max))
		else:
			self.redirect('http://www.mindlesstux.com')