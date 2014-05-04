// --------------------------------------------------------
//
// This file is to configure the configurable settings.
// Load this file before script.js file at gmap.html.
//
// --------------------------------------------------------

// -- JSON-feed -------------------------------------------
// Default 'Mine', '/dump1090/data.json'
CONST_JSON = [
    ['KCLT',   '/dynamic/data/kclt.json'],
    ['RTLSDR', '/dynamic/data/rtlsdr.json'],
    ['EFTU',   '/dynamic/data/eftu.json']
];

// -- Output Settings -------------------------------------
// Show metric values
Metric = false; // true or false

// -- Map settings ----------------------------------------
// The Latitude and Longitude in decimal format
CONST_CENTERLAT = 35.21712;
CONST_CENTERLON = -80.94384;

// The google maps zoom level, 0 - 16, lower is further out
CONST_ZOOMLVL   = 9;

// -- Marker settings -------------------------------------
// The default marker color
MarkerColor	  = "rgb(127, 127, 127)";
SelectedColor = "rgb(225, 225, 225)";

// -- Site Settings ---------------------------------------
SiteShow    = true; // true or false
// The Latitude and Longitude in decimal format
SiteLat     = CONST_CENTERLAT;
SiteLon     = CONST_CENTERLON;

SiteCircles = true; // true or false (Only shown if SiteShow is true)
// In nautical miles or km (depending settings value 'Metric')
SiteCirclesDistances = new Array(5,10,30);

// -- METAR data ------------------------------------------
// ICAO codes separated with comma
MetarIcaoCode = "KCLT";

// -- Antenna Data Collection -----------------------------
AntennaDataCollect  = false;
AntennaDataShow     = false;
AntennaDataOpacity  = 0.3;

LabelShow = true;

// -- Put debuging lines into console ---------------------
BOOL_DEBUG = true;