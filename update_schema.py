import logging
import datastore

from datastore import Aircraft
from google.appengine.ext import deferred
from google.appengine.ext import ndb
from plane import icaoArray

BATCH_SIZE = 100  # ideal batch size may vary based on entity size.

def countryLookup(tmp, split):
	x = {}
	x['country'] = ''
	x['country_short'] = ''
	x['country_flag'] = 'NoFlag.png'
	x['flag_isMilitary'] = False

	newStr = str(split[4]).replace('"', '')
	for country in icaoArray:
		if country[3] == newStr:
			x['country'] = country[3]
			x['country_short'] = country[1]
			x['country_flag'] = country[4]
			x['flag_isMilitary'] = bool(country[2])
			return x

	logging.warning('Deferred Status: [%s] country not found: %s' % (tmp.icao, split[4]))
	return x

def UpdateSchema(start=1, linemax=0):
	# The array of puts to put!
	to_put = []

	# Do our start/stop math
	start = int(start)
	linemax = int(linemax)
	stop = start + BATCH_SIZE

	# Open the basestation file
	with open('basestation.csv', 'r') as csvfile:
		# If start is 1, set max to total lines in the file
		if start is 1:
			linemax = len(list(csvfile))
		else:
			if stop > int(linemax):
				stop = int(linemax)

		# Grab the BATCH_SIZE number of lines
		lines = csvfile.readlines()[start:stop]

		# For each line, find the existing, then update it!
		for row in lines:
			split = row.split(',')
			mantma_id = int(split[0])

			query = Aircraft().query(Aircraft.mantma_id == mantma_id).get()

			if (query == None):
				tmp = datastore.Aircraft()
			else:
				tmp = query

			try:
				tmp.mantma_id = mantma_id
				tmp.icao = split[3]
				tmp.registration = split[5]
				tmp.icao_type = split[6]
				if str(split[7]).replace('"', '') != " ":
					tmp.serialNo = split[7]
				else:
					tmp.serialNo = ''
				tmp.operator_flag = split[8]

				x = countryLookup(tmp, split)
				tmp.country = x['country']
				tmp.country_short = x['country_short']
				tmp.country_flag = x['country_flag']
				tmp.flag_isMilitary = x['flag_isMilitary']
				tmp.flag_new = False
				tmp.flag_reviewed = False
				tmp.flag_updated = False

				tmp.put()
			except:
				logging.warning('Deferred Status: [%s] fails somehow' % (split[3]))

		csvfile.close()

	if (linemax > start):
		logging.info('Deferred Status: %s / %s' % (start, linemax))
		deferred.defer(UpdateSchema, start=stop, linemax=linemax)
	else:
		logging.info('Deferred Status: Done! (%s lines checked)' % (linemax))