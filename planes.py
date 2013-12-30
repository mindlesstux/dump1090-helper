__author__ = 'bdavenport'

import datetime
import json
import logging
import re
import os

from plane import Plane
from google.appengine.api import memcache
from datastore import AirCraft

# Lets group the planes together
class Planes():
    def __init__(self):
        # Our planes
        self.planes = {}
        self.planeicaos = []

        self.datacenter = os.environ['DATACENTER']
        self.server_instance = os.environ['INSTANCE_ID']
        self.server_version = os.environ['SERVER_SOFTWARE']
        self.code_version = re.sub("([a-z0-9]*)\.([0-9]*)", "\g<1>""", os.environ['CURRENT_VERSION_ID'])


    def Warmup(self):
        data = memcache.get('planeicaos')
        if data is not None:
            for icao in data:
                self.planes[icao] = self.pullPlane(icao)

    def newPlane(self, icao):
        plane = Plane()
        plane.icao = icao
        query = AirCraft.query(AirCraft.icao24 == icao).fetch()
        if (query == []):
            tmp = AirCraft()
            tmp.icao24 = icao
            tmp.put()
            del tmp
            del query
        else:
            del query
        self.pushPlane(icao, plane)
        return plane

    def checkLocalPlane(self, icao):
        if icao in self.planes:
            return True
        else:
            return False

    def checkMemcachePlane(self, icao):
        data = memcache.get(icao)
        if data is not None:
            return True
        else:
            return False

    # TODO: Make this purge out planeicaos properly
    def reaper(self):
        logging.debug("Planes before reap: %s" % len(self.planeicaos))
        to_pop = []
        for x in self.planes:
            plane = self.planes[x]
            now = datetime.datetime.now()
            planedate = plane.lastupdate
            timedelta = now - planedate
            if timedelta.total_seconds() > 90:
                plane.seen_stop = datetime.datetime.utcnow()
                to_pop.append(x)

        for x in to_pop:
            logging.debug("Removing '%s' from list" % x)
            self.planes.pop(x)
            self.planeicaos.remove(x)
            memcache.delete(key=plane.icao)
            memcache.set(key='planeicaos', value=self.planeicaos, time=1800)

        logging.debug("Planes after reap:  %s" % len(self.planeicaos))

    # Update our local array of planes and update memcache for other instances
    def pushPlane(self, icao, plane):
        plane.lastupdate = datetime.datetime.utcnow()
        self.planes[icao] = plane
        memcache.set(key=icao, value=plane, time=900)
        if icao not in self.planeicaos:
            self.planeicaos.append(str(icao))
            memcache.set(key='planeicaos', value=self.planeicaos, time=1800)

    # Grab this plane somehow...
    def pullPlane(self, icao):
        # Does the plane exist in memcache?
        if self.checkMemcachePlane(icao):
            remoteplane = memcache.get(icao)
            return remoteplane
        else:
            # Do we have this plane locally already? (aka pushed out of memcache...)
            if self.checkLocalPlane(icao):
                localplane = self.planes[icao]
                return localplane
            else:
                plane = self.newPlane(icao)
                return plane

    def processJSON(self, msgs):
        for msg in msgs:
            plane = self.pullPlane(msg['hex'])

            # Need to change this to last updated w/ GMT/UTC conversion
            if plane.msgcountJSON is not msg['messages']:
                if bool(msg['validaltitude']) is True:
                  plane.altitude = msg['altitude']

                if bool(msg['validtrack']) is True:
                    plane.track = int(msg['track'])
                else:
                    plane.track = None

                if bool(msg['validposition']) is True:
                    if plane.latitude != float(msg['lat']) or plane.longitude != float(msg['lon']):
                        plane.latitude = float(msg['lat'])
                        plane.longitude = float(msg['lon'])
                        if plane.latitude > 90 or plane.latitude < -90 or plane.longitude > 180 or plane.longitude < -180:
                            logging.error("Plane out of bounds: %s @ %s, %s" % (plane.icao, msg['lat'], msg['lon']))
                            plane.latitude = None
                            plane.longitude = None
                            moved = False
                        else :
                            moved = True
                    else:
                        moved = False
                else:
                    plane.latitude = None
                    plane.longitude = None
                    moved = False

                if plane.squawk is not msg['squawk']:
                    plane.squawk = msg['squawk']

                if plane.flightid is not msg['flight']:
                    plane.flightid = msg['flight']

                if int(msg['speed']) is not 0:
                    plane.groundspeed = int(msg['speed'])

                plane.msgcountJSON = msg['messages']
                plane.msgcount += 1

                plane.signal = msg['signal']

                if plane.latitude is not None and plane.longitude is not None and moved is True:
                    plane.trail.append({'latitude': plane.latitude, 'longitude': plane.longitude, 'altitude': plane.altitude, 'track': plane.track})

                self.pushPlane(msg['hex'], plane)

            del plane

    def generateJSON(self):
        jsonstr = []
        serverstr = {"server_info": {"datacenter": self.datacenter, "instance": self.server_instance, "version_server": self.server_version, "version_software": self.code_version}}
        jsonstr.append(serverstr)

        planesstr = []
        try:
            for x in self.planes:
                plane = self.pullPlane(x)
                planestr = {}
                planestr['hex'] = plane.icao
                planestr['squawk'] = plane.squawk
                planestr['flight'] = plane.flightid

                if plane.latitude is not None and plane.longitude is not None:
                    planestr['validposition'] = 1
                    planestr['lat'] = plane.latitude
                    planestr['lon'] = plane.longitude
                else:
                    planestr['validposition'] = 0
                    planestr['lat'] = ""
                    planestr['lon'] = ""

                if plane.altitude is not None:
                    planestr['validaltitude'] = 1
                    planestr['altitude'] = plane.altitude
                else:
                    planestr['validaltitude'] = 0
                    planestr['altitude'] = ""

                if plane.groundspeed is not None:
                    planestr['speed'] = plane.groundspeed
                else:
                    planestr['speed'] = ""

                if plane.track is not None:
                    planestr['validtrack'] = 1
                    planestr['track'] = plane.track
                else:
                    planestr['validtrack'] = 0
                    planestr['track'] = ""

                planestr['signal'] = plane.signal

                now = datetime.datetime.now()
                planedate = plane.lastupdate
                timedelta = now - planedate
                planestr['seen'] = "%s" % int(timedelta.total_seconds())

                planestr['messages'] = plane.msgcount


                planesstr.append(planestr)
        except:
            planestr = []

        jsonstr.append(planesstr)

        jsondump = json.dumps(jsonstr)
        return jsondump


    def generateJSONTrail(self, icao):
        plane = self.pullPlane(icao)
        jsondump = json.dumps(plane.trail)
        return jsondump

    def generateKML(self):
        kmlstr = ""

        kmlheader = '''<?xml version="1.0" encoding="UTF-8"?>
<kml xmlns="http://www.opengis.net/kml/2.2" xmlns:gx="http://www.google.com/kml/ext/2.2" xmlns:kml="http://www.opengis.net/kml/2.2" xmlns:atom="http://www.w3.org/2005/Atom">
    <Document>
        <name>Dump1090-Helper</name>
        <Style id="plane">
            <IconStyle>
                <color>ff00ffff</color>
                <scale>1.4</scale>
                <Icon>
                    <href>http://maps.google.com/mapfiles/kml/shapes/airports.png</href>
                </Icon>
                <hotSpot x="0.5" y="0" xunits="fraction" yunits="fraction"/>
            </IconStyle>
            <ListStyle>
            </ListStyle>
            <PolyStyle>
			    <color>4cffaa55</color>
		    </PolyStyle>
        </Style>
'''
        kmlstr += kmlheader
        del kmlheader

        for x in self.planes:
            plane = self.pullPlane(x)
            if plane.latitude is not None and plane.longitude is not None:
                kmltmp = '''
        <Folder>
            <name>%s (%s)</name>
            <open>1</open>''' % (plane.flightid, plane.icao)
                kmlstr += kmltmp
                del kmltmp

                kmltmp = '''
            <Placemark>
                <name>%s (%s)</name>
                <description></description>
                <LookAt>
                    <longitude>%s</longitude>
                    <latitude>%s</latitude>
                </LookAt>
                <Point>
                    <extrude>1</extrude>
                    <altitudeMode>absolute</altitudeMode>
                    <coordinates>%s,%s,%s</coordinates>
                </Point>
                <styleUrl>#plane</styleUrl>
            </Placemark>
                ''' % (plane.flightid, plane.icao, plane.longitude, plane.latitude, plane.longitude, plane.latitude, (plane.altitude * 0.3048))
                kmlstr += kmltmp
                del kmltmp

                tmp_trail = plane.trail
                tmp = ""
                for x in tmp_trail:
                    tmp += '''%s,%s,%s
                    ''' % (x['longitude'], x['latitude'], (x['altitude'] * 0.3048))
                del tmp_trail

                kmltmp = '''
            <Placemark>
                <name>Trail</name>
                <LineString>
                    <extrude>1</extrude>
                    <tessellate>1</tessellate>
                    <altitudeMode>absolute</altitudeMode>
                    <coordinates>
                        %s
                    </coordinates>
                </LineString>
                <styleUrl>#plane</styleUrl>
            </Placemark>
        </Folder>
                ''' % (tmp)
                kmlstr += kmltmp
                del kmltmp

        kmlfooter = '''
    </Document>
</kml>'''
        kmlstr += kmlfooter
        del kmlfooter
        return kmlstr