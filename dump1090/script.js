// Define our global variables
var GoogleMap     = null;
var Planes        = {};
var PlanesOnMap   = 0;
var PlanesOnTable = 0;
var PlanesToReap  = 0;
var SelectedPlane = null;
var SpecialSquawk = false;
var MetarICAO     = null;
var MetarReset    = true;
var AntennaData     = {};
var AntennaDataPath = null;

// Track all the plane data in a massive array for the html table...
var data_array = [];
var data_table = null;

// These might go away...
var iSortCol=-1;
var bSortASC=true;
var bDefaultSortASC=true;
var iDefaultSortCol=3;

// Get current map settings
var CenterLat = Number(localStorage['CenterLat']) || CONST_CENTERLAT;
var CenterLon = Number(localStorage['CenterLon']) || CONST_CENTERLON;
var ZoomLvl   = Number(localStorage['ZoomLvl']) || CONST_ZOOMLVL;
if (localStorage['markerFLFilter']) {
    var markerFLFilter = JSON.parse(localStorage['markerFLFilter'])
} else {
    var markerFLFilter = [0, 99000];
}


// Set ajax data type. Datatype 'jsonp' is needed when using json from different port or server.
// This way data type can be set from config.js or untracked[...].js files.
if (typeof(ajaxDataType) === 'undefined') {
    ajaxDataType = 'json';
}

var iPlanesTrackable = 0;
var iPlanesTable = 0;
var iPlanesTotal = 0;

function fetchData(entry) {
    $.ajax({
	    url: entry[1],
	    dataType: ajaxDataType,
	    success: function(data) {
		    SpecialSquawk = false;
		
		    // Loop through all the planes in the data packet
		    for (var j=0; j < data.length; j++) {
			    // Do we already have this plane object in Planes?
			    // If not make it.
			    if (Planes[data[j].hex]) {
				    var plane = Planes[data[j].hex];
			    } else {
				    var plane = jQuery.extend(true, {}, planeObject);
			    }
			
			    /* For special squawk tests
				if (data[j].hex == 'xxxxxx') {
                    data[j].squawk = '7700';
		        }*/

			    // Call the function update
			    plane.funcUpdateData(data[j], entry[0]);

			    // Copy the plane into Planes
			    Planes[plane.icao] = plane;
		    }
	    }
    });
}

// Initalizes the map and starts up our timers to call various functions
function initialize() {
	// Make a list of all the available map IDs
	var mapTypeIds = [];
	for(var type in google.maps.MapTypeId) {
		mapTypeIds.push(google.maps.MapTypeId[type]);
	}
	// Push OSM on to the end
	mapTypeIds.push("OSM");
	mapTypeIds.push("dark_map");

	// Styled Map to outline airports and highways
	var styles = [
		{
			"featureType": "administrative",
			"stylers": [
				{ "visibility": "off" }
			]
		},{
			"featureType": "landscape",
			"stylers": [
				{ "visibility": "off" }
			]
		},{
			"featureType": "poi",
			"stylers": [
				{ "visibility": "off" }
			]
		},{
			"featureType": "road",
			"stylers": [
				{ "visibility": "off" }
			]
		},{
			"featureType": "transit",
			"stylers": [
				{ "visibility": "off" }
			]
		},{
			"featureType": "landscape",
			"stylers": [
				{ "visibility": "on" },
				{ "weight": 8 },
				{ "color": "#0F0F0F" }
			]
		},{
			"featureType": "water",
			"stylers": [
			{ "lightness": -74 }
			]
		},{
			"featureType": "transit.station.airport",
			"stylers": [
				{ "visibility": "on" },
				{ "weight": 8 },
				{ "invert_lightness": true },
				{ "lightness": 27 }
			]
		},{
			"featureType": "road.highway",
			"stylers": [
				{ "visibility": "simplified" },
				{ "invert_lightness": true },
				{ "gamma": 0.3 }
			]
		},{
			"featureType": "road",
			"elementType": "labels",
			"stylers": [
				{ "visibility": "off" }
			]
		}
	]

	// Add our styled map
	var styledMap = new google.maps.StyledMapType(styles, {name: "Dark Map"});

	// Define the Google Map
	var mapOptions = {
		center: new google.maps.LatLng(CenterLat, CenterLon),
		zoom: ZoomLvl,
		mapTypeId: google.maps.MapTypeId.ROADMAP,
		mapTypeControlOptions: {
			mapTypeIds: mapTypeIds,
		}
	};

	GoogleMap = new google.maps.Map(document.getElementById("map_canvas"), mapOptions);

    var jQueryLayout = $('body').layout({
        stateManagement__enabled:	true,
        minSize:					100,
        initClosed:                 true,
        east__initClosed:           false,
        defaults: {
        },
        onresize: function () {
            google.maps.event.trigger(GoogleMap, 'resize');
            GoogleMap.setCenter(new google.maps.LatLng(CenterLat, CenterLon));
        },
        east: {
            size:					350,
            spacing_closed:			22,
            togglerLength_open: 	160,
            togglerLength_closed:	160,
            togglerAlign_closed:	"top",
            togglerContent_closed:	"D<br/>a<br/>t<br/>a<br/> <br/>T<br/>a<br/>b<br/>l<br/>e",
            togglerTip_closed:		"Data table",
            fxName:                 "none",
            initClosed:             false,
            onopen_end: function () {
                west.close();
            }
        },
        east__childOptions:	{
            minSize:				50,	// ALL panes
            north__size:			150,
            north: {
                spacing_closed:         15,
                togglerLength_open: 	160,
                togglerLength_closed:	160,
                togglerAlign_closed:	"right",
                togglerContent_closed:	"Selected Data",
                togglerTip_closed:		"Selected Data",
                fxName:                 "none",
                initClosed:             false,
            }
        },
        west: {
            size:					350,
            spacing_closed:			22,
            togglerLength_open: 	160,
            togglerLength_closed:	160,
            togglerAlign_closed:	"top",
            togglerContent_closed:	"S<br/>e<br/>t<br/>t<br/>i<br/>n<br/>g<br/>s",
            togglerTip_closed:		"Settings",
            fxName:                 "none",
            initClosed:                 true,
        },
    });

    $( "#accordion" ).accordion({
        heightStyle: "content"
    });

	//Define OSM map type pointing at the OpenStreetMap tile server
	GoogleMap.mapTypes.set("OSM", new google.maps.ImageMapType({
		getTileUrl: function(coord, zoom) {
			return "http://tile.openstreetmap.org/" + zoom + "/" + coord.x + "/" + coord.y + ".png";
		},
		tileSize: new google.maps.Size(256, 256),
		name: "OpenStreetMap",
		maxZoom: 18
	}));

	GoogleMap.mapTypes.set("dark_map", styledMap);
	
    // Listeners for newly created Map
    google.maps.event.addListener(GoogleMap, 'center_changed', function() {
        localStorage['CenterLat'] = GoogleMap.getCenter().lat();
        localStorage['CenterLon'] = GoogleMap.getCenter().lng();
        CenterLat = localStorage['CenterLat'];
        CenterLon = localStorage['CenterLon'];
    });

    google.maps.event.addListener(GoogleMap, 'zoom_changed', function() {
        localStorage['ZoomLvl']  = GoogleMap.getZoom();
        ZoomLvl = localStorage['ZoomLvl'];
    });
	
	// Add home marker if requested
	if (SiteShow && (typeof SiteLat !==  'undefined' || typeof SiteLon !==  'undefined')) {
	    var siteMarker  = new google.maps.LatLng(SiteLat, SiteLon);
	    
	    var markerImage = {
	        url:    'http://maps.google.com/mapfiles/kml/pal4/icon57.png',
            size:   new google.maps.Size(32, 32),   // Image size
            origin: new google.maps.Point(0, 0),    // Origin point of image
            anchor: new google.maps.Point(16, 16)   // Position where marker should point
        };
             
	    var marker = new google.maps.Marker({
            position: siteMarker,
            map: GoogleMap,
            icon: markerImage,
            title: 'My Radar Site',
            zIndex: -99999
        });
        
        if (SiteCircles) {
            for (var i=0;i<SiteCirclesDistances.length;i++) {
              drawCircle(marker, SiteCirclesDistances[i]); // in meters
            }
        }
        
        if (AntennaDataCollect) {
            if (localStorage.getObject('AntennaData')) {
                AntennaData = localStorage.getObject('AntennaData');
            }
        }
        
        if (AntennaDataShow) {
            // Get AntennaData from localStorage
            if (localStorage['AntennaData']) {AntennaData = localStorage.getObject('AntennaData');}
            
            // Load data from file
            length = Object.size(AntennaData);
            if (length < 270) {
                jQuery.ajaxSetup({async:false});
                $.get('antennaBaseCoverage.txt',  function(data) {
                    if (data.indexOf('Error') == -1) { // no errors
                        localStorage['AntennaData'] = data;
                    }
                });
                jQuery.ajaxSetup({async:true});
            }
            
            if (localStorage['AntennaData']) {
                AntennaData = localStorage.getObject('AntennaData');
                drawAntennaData(siteMarker);
            }
        }
	}
	
	// Ui buttons setup
	btnWidth = "100px";
	$("#resetMap").button({icons: {primary: "ui-icon-arrowrefresh-1-w"}});
	$("#resetMap").width(btnWidth);
	$("#resetMap").css("margin-bottom", "3px");
	$("#resetMap").button().focus(function() {
           $(this).button("widget").removeClass("ui-state-focus");
    });
	
	$("#optionsModal").button({icons: {primary: "ui-icon-gear"}});
	$("#optionsModal").width(btnWidth);
    $("#optionsModal").button().focus(function() {
        $(this).button("widget").removeClass("ui-state-focus");
    });

	// Load up our options page
	optionsInitalize();

	// Did our crafty user need some setup?
	extendedInitalize();
	
	// Setup our timer to poll from the server.
	window.setInterval(function() {
        CONST_JSON.forEach(function(entry) {
            fetchData(entry);
        });

        updateTableOfPlanes();
        refreshSelected();
        reaper();
        extendedPulse();
	}, 5000);
	
	// Refresh metar now and then only once every 5 minutes.
	if (MetarIcaoCode && MetarIcaoCode != "") {
	    getMetar();
	    $("#METAR").on("drag", function(event, ui) {
	        MetarDragged = true;
	});

    window.setInterval(function() {
            getMetar();
        }, 300000);
    }

    data_table = $('#table_of_planes').dataTable( {
        "aaData": data_array,
        "aoColumns": [
            { "sTitle": "Flag",             sDefaultContent: "",    "sWidth": "50px",   "sClass": "col-center",     "bSortable": false, "mData": "flag",            "bVisible": true,},
            { "sTitle": "Reg",              sDefaultContent: "",    "sWidth": "50px",   "sClass": "col-left",       "bSortable": true,  "mData": "registration",    "bVisible": true,},
            { "sTitle": "Operator",    		sDefaultContent: "",    "sWidth": "50px",   "sClass": "col-center",     "bSortable": false, "mData": "operator_logo",   "bVisible": true,},
            { "sTitle": "Silhouette",       sDefaultContent: "",    "sWidth": "50px",   "sClass": "col-center",     "bSortable": false, "mData": "silhouette",      "bVisible": true,},
            { "sTitle": "Flight",           sDefaultContent: "",    "sWidth": "50px",   "sClass": "col-left",       "bSortable": true,  "mData": "flight",          "bVisible": true,},

            { "sTitle": "Alt",              sDefaultContent: "",    "sWidth": "50px",   "sClass": "col-right",      "bSortable": true,  "mData": "altitude",        "bVisible": true,},
            { "sTitle": "Spd",              sDefaultContent: "",    "sWidth": "50px",   "sClass": "col-right",      "bSortable": true,  "mData": "speed",           "bVisible": true,},
            { "sTitle": "Trk",              sDefaultContent: "",    "sWidth": "50px",   "sClass": "col-right",      "bSortable": true,  "mData": "track",           "bVisible": true,},
            { "sTitle": "Latitude",         sDefaultContent: "",    "sWidth": "50px",   "sClass": "col-center",     "bSortable": false, "mData": "latitude",        "bVisible": false, },
            { "sTitle": "Longitude",        sDefaultContent: "",    "sWidth": "50px",   "sClass": "col-center",     "bSortable": false, "mData": "longitude",       "bVisible": false, },

            { "sTitle": "Squawk",           sDefaultContent: "",    "sWidth": "50px",   "sClass": "col-center",     "bSortable": true,  "mData": "squawk",          "bVisible": false, },
            { "sTitle": "ICAO",             sDefaultContent: "",    "sWidth": "50px",   "sClass": "col-center",     "bSortable": true,  "mData": "icao",            "bVisible": true,},
            { "sTitle": "MSGs",             sDefaultContent: "",    "sWidth": "50px",   "sClass": "col-right",      "bSortable": false, "mData": "messages",        "bVisible": false,},
            { "sTitle": "Seen",             sDefaultContent: "",    "sWidth": "50px",   "sClass": "col-right",      "bSortable": false, "mData": "seen",            "bVisible": false,},
            { "sTitle": "Country",          sDefaultContent: "",    "sWidth": "50px",   "sClass": "col-center",     "bSortable": true,  "mData": "country",         "bVisible": false,},
            { "sTitle": "Country",          sDefaultContent: "",    "sWidth": "50px",   "sClass": "col-center",     "bSortable": true,  "mData": "country_short",   "bVisible": true,},
            { "sTitle": "Type",             sDefaultContent: "",    "sWidth": "50px",   "sClass": "col-center",     "bSortable": true,  "mData": "type",            "bVisible": false,},
            { "sTitle": "Operator",         sDefaultContent: "",    "sWidth": "50px",   "sClass": "col-center",     "bSortable": true,  "mData": "operator",        "bVisible": false,},
            { "sTitle": "Source",           sDefaultContent: "",    "sWidth": "50px",   "sClass": "col-center",     "bSortable": true,  "mData": "source",          "bVisible": true,},
        ],
        "asStripeClasses": ["row"],
        "bPaginate": false,
        "bSort": true,
        "bInfo": false,
        "bAutoWidth": false,
        "bStateSave": true,
        "bDeferRender": true,
        "sDom": 'Rlfrtip',
    });

    $("#table_of_planes").on('click', 'tr', function(event) {
        var id = data_table.fnGetData(this);
        onClickPlanes_table(id['icao'])
    });
}

// This looks for planes to reap out of the master Planes variable
function reaper() {
	PlanesToReap = 0;
	// When did the reaper start?
	reaptime = new Date().getTime();
	// Loop the planes
	for (var reap in Planes) {
        // Cheat! Seeing how if its version 1/2 there is a seen feild that goes above 60, our cutoff
        // With 0 we need to force a check every time as if it was updated...
        tmp_plane = Planes[reap];
        if (tmp_plane.jsonDataVer == 0) {
            tmp_plane.funcReaperCheck();
        }
        /*
        x = reaptime - tmp_plane.updated;
        if (x > 10000) {
            console.log("Plane " + tmp_plane.icao + " Data version: " + tmp_plane.jsonDataVer +"  reapable? " + tmp_plane.reapable + " lastupdated: " + x);
        }
        */
		// Is this plane possibly reapable?
		if (tmp_plane.reapable == true) {
			// Has it not been seen for 5 minutes?
			// This way we still have it if it returns before then
			// Due to loss of signal or other reasons

			if ((reaptime - tmp_plane.updated) > 30000) {
				// Reap it.
				delete Planes[reap];
			}
			PlanesToReap++;
		}
	};
} 

// Refresh the detail window about the plane
function refreshSelected() {
    var selected = false;
	if (typeof SelectedPlane !== 'undefined' && SelectedPlane != "ICAO" && SelectedPlane != null) {
    	selected = Planes[SelectedPlane];
    }
	
	var columns = 2;
	var html = '';
	
	if (selected) {
    	html += '<table id="selectedinfo" width="100%">';
    } else {
        html += '<table id="selectedinfo" class="dim" width="100%">';
    }
	
	// Flight header line including squawk if needed
	if (selected && selected.flight == "") {
	    html += '<tr><td colspan="' + columns + '" id="selectedinfotitle"><b>N/A (' +
	        selected.icao + ')</b>';
	} else if (selected && selected.flight != "") {
	    html += '<tr><td colspan="' + columns + '" id="selectedinfotitle"><b>' +
	        selected.flight + '</b>';
	} else {
	    html += '<tr><td colspan="' + columns + '" id="selectedinfotitle"><b>DUMP1090</b>';
	}
	
	if (selected && selected.squawk == 7500) { // Lets hope we never see this... Aircraft Hijacking
		html += '&nbsp;<span class="squawk7500">&nbsp;Squawking: Aircraft Hijacking&nbsp;</span>';
	} else if (selected && selected.squawk == 7600) { // Radio Failure
		html += '&nbsp;<span class="squawk7600">&nbsp;Squawking: Radio Failure&nbsp;</span>';
	} else if (selected && selected.squawk == 7700) { // General Emergency
		html += '&nbsp;<span class="squawk7700">&nbsp;Squawking: General Emergency&nbsp;</span>';
	} else if (selected && selected.flight != '') {
	    html += '&nbsp;<a href="http://www.flightstats.com/go/FlightStatus/flightStatusByFlight.do?';
        html += 'flightNumber='+selected.flight+'" target="_blank">[FlightStats]</a>';
	}
	html += '<td></tr>';
	
	if (selected && selected.altitude != '') {
	    if (Metric) {
        	html += '<tr><td>Altitude: ' + Math.round(selected.altitude / 3.2828) + ' m</td>';
        } else {
            html += '<tr><td>Altitude: ' + selected.altitude + ' ft</td>';
        }
    } else {
        html += '<tr><td>Altitude: n/a</td>';
    }
		
	if (selected && selected.squawk != '0000') {
		html += '<td>Squawk: ' + selected.squawk + '</td></tr>';
	} else {
	    html += '<td>Squawk: n/a</td></tr>';
	}
	
	html += '<tr><td>Speed: ' 
	if (selected) {
	    if (Metric) {
	        html += Math.round(selected.speed * 1.852) + ' km/h';
	    } else {
	        html += selected.speed + ' kt';
	    }
	} else {
	    html += 'n/a';
	}
	html += '</td>';
	
	if (selected) {
        html += '<td>ICAO (hex): ' + selected.icao + '</td></tr>';
    } else {
        html += '<td>ICAO (hex): n/a</td></tr>'; // Something is wrong if we are here
    }
    
    html += '<tr><td>Track: ' 
	if (selected && selected.vTrack) {
	    html += selected.track + ' (' + normalizeTrack(selected.track, selected.vTrack)[1] +')';
	} else {
	    html += 'n/a';
	}

	html += '</td><td>Reg: '
	if (selected && selected.registration != '') {
	    html += '<a href="http://www.planespotters.net/Aviation_Photos/search.php?reg='+selected.registration +
	        '&o=14" target="_blank">' + selected.registration + '</a>';
	} else {
	    html += 'n/a';
	}
	html += '</td></tr>';

	html += '<tr><td colspan="' + columns + '" align="center">Lat/Long: ';
	if (selected && selected.vPosition) {
	    html += selected.latitude + ', ' + selected.longitude + '</td></tr>';
	    
	    // Let's show some extra data if we have site coordinates
	    if (SiteShow) {
            var siteLatLon  = new google.maps.LatLng(SiteLat, SiteLon);
            var planeLatLon = new google.maps.LatLng(selected.latitude, selected.longitude);
            var dist = google.maps.geometry.spherical.computeDistanceBetween(siteLatLon, planeLatLon);
            var bearing = google.maps.geometry.spherical.computeHeading(siteLatLon, planeLatLon);
            
            bearing = Math.round(bearing);
            if (bearing < 0) { bearing += 360; }
            
            if (Metric) {
                dist /= 1000;
            } else {
                dist /= 1852;
            }
            
            dist = (Math.round((dist)*10)/10).toFixed(1);
            html += '<tr><td colspan="' + columns + '">Distance from Site: ' + dist +
                (Metric ? ' km' : ' NM') + ' @ ' + bearing + '&deg;</td></tr>';
        } // End of SiteShow
	} else {
	    if (SiteShow) {
	        html += '<tr><td colspan="' + columns + '">Distance from Site: n/a ' + 
	            (Metric ? ' km' : ' NM') + '</td></tr>';
	    } else {
    	    html += 'n/a</td></tr>';
    	}
	}

	html += '</table>';
	
	document.getElementById('plane_detail').innerHTML = html;
}

// Returns back a long string, short string, and the track if we have a vaild track path
function normalizeTrack(track, valid){
	x = []
	if ((track > -1) && (track < 22.5)) {
		x = ["North", "N", track]
	}
	if ((track > 22.5) && (track < 67.5)) {
		x = ["North East", "NE", track]
	}
	if ((track > 67.5) && (track < 112.5)) {
		x = ["East", "E", track]
	}
	if ((track > 112.5) && (track < 157.5)) {
		x = ["South East", "SE", track]
	}
	if ((track > 157.5) && (track < 202.5)) {
		x = ["South", "S", track]
	}
	if ((track > 202.5) && (track < 247.5)) {
		x = ["South West", "SW", track]
	}
	if ((track > 247.5) && (track < 292.5)) {
		x = ["West", "W", track]
	}
	if ((track > 292.5) && (track < 337.5)) {
		x = ["North West", "NW", track]
	}
	if ((track > 337.5) && (track < 361)) {
		x = ["North", "N", track]
	}
	if (!valid) {
		x = [" ", "n/a", ""]
	}
	return x
}

function updateTableOfPlanes() {
    // Blank array
    data_tmp = [];

    // Planes on the table
    iPlanesTable = 0;

    // Planes that can be tracked to a lat/long
    iPlanesTrackable = 0;

    // Loop through all the planes
    for (var tablep in Planes) {
        // Pluck our plane
        var tableplane = Planes[tablep];

        // If the plane is not beyond 60 seconds, basically
        if (!tableplane.reapable) {
            // Count it on the table
            iPlanesTable++;

            // Data array for this plane to be passed to the table
            var tmp = {
                "altitude": tableplane.altitude,
                "speed": tableplane.speed,
                "track": tableplane.track,
                "latitude": tableplane.latitude,
                "longitude": tableplane.longitude,
                "flight": tableplane.flight,
                "icao": tableplane.icao,
                "messages": tableplane.messages,
                "seen": tableplane.seen,
                "country": tableplane.country,
                "country_short": tableplane.country_short,
                "type": tableplane.type,
                "operator": tableplane.operator,
                "registration": tableplane.registration,
                "squawk": tableplane.squawk,

                "source": tableplane.source,

                "flag": '<img src="' + remote_imgdir + 'Small_Flags/' + tableplane.country_flag + '" title="' + tableplane.country + ' (' + tableplane.country_short + ')"  alt="' + tableplane.country + ' (' + tableplane.country_short + ')" />',
                "operator_logo": '<img src="' + remote_imgdir + 'OperatorLogos/' + tableplane.operator + '.png" title="' + tableplane.operator + '"  alt="' + tableplane.operator + '" height="20" width="85" />',
                "silhouette": '<img src="' + remote_imgdir + 'SilhouettesLogos/' + tableplane.type + '.png" title="' + tableplane.type + '"  alt="' + tableplane.type + '" height="20" width="85" />',

                "DT_RowId":	tableplane.icao,
                "DT_RowClass":	tableplane.specialStyle,
            };

            // Have to put this here to track it
            if (tableplane.vPosition == true) {
                iPlanesTrackable++;
            }

            // If all 0's then it is not something we want to show
            if (tableplane.squawk == '0000') {
                tmp["squawk"] = "";
            }
            if (tableplane.type == '') {
                tmp["silhouette"] = '<img src="' + remote_imgdir + 'SilhouettesLogos/@@@.png" title="' + tableplane.type + '"  alt="' + tableplane.type + '" height="20" width="85" />';
            }


            // Push the data array to the tmp data table
            data_tmp.push(tmp);
        }

    };

    // Rebuild the table
    data_array = data_tmp;
    data_table.fnClearTable();
    data_table.fnAddData(data_array);

    // Update the document title to be something like "Dump1090 (1/2/3)"
    // 1 = Planes able to be tracked via Lat/Long
    // 2 = Planes that are shown on the table
    // 3 = All planes, including the ones preping to be reaped
    document.title = "Dump1090 (" + iPlanesTrackable + "/" + iPlanesTable + "/" + Planes.length + ")";

    // If there is a squawk that is to be noted...
    if (SpecialSquawk) {
    	$('#SpecialSquawkWarning').css('display', 'inline');
    } else {
        $('#SpecialSquawkWarning').css('display', 'none');
    }
}

function onClickPlanes_table (hex) {
    if (hex && hex != '' && hex != "ICAO") {
		selectPlaneByHex(hex);
	}
}

function selectPlaneByHex(hex) {
	// If SelectedPlane has something in it, clear out the selected
	if (SelectedPlane != null) {
		Planes[SelectedPlane].is_selected = false;
		Planes[SelectedPlane].funcClearLine();
		Planes[SelectedPlane].markerColor = MarkerColor;
		// If the selected has a marker, make it not stand out
		if (Planes[SelectedPlane].marker) {
			Planes[SelectedPlane].marker.setIcon(Planes[SelectedPlane].funcGetIcon());
		}
        Planes[SelectedPlane].funcUpdateStyle();
	}

	// If we are clicking the same plane, we are deselected it.
	if (String(SelectedPlane) != String(hex)) {
		// Assign the new selected
		SelectedPlane = hex;
		Planes[SelectedPlane].is_selected = true;
		// If the selected has a marker, make it stand out
		if (Planes[SelectedPlane].marker) {
			Planes[SelectedPlane].funcUpdateLines();
			Planes[SelectedPlane].marker.setIcon(Planes[SelectedPlane].funcGetIcon());
		}
        Planes[SelectedPlane].funcUpdateStyle();
	} else { 
		SelectedPlane = null;
	}

    refreshSelected();
    updateTableOfPlanes();
}

function resetMap() {
    // Reset localStorage values
    localStorage['CenterLat'] = CONST_CENTERLAT;
    localStorage['CenterLon'] = CONST_CENTERLON;
    localStorage['ZoomLvl']   = CONST_ZOOMLVL;
    
    // Try to read values from localStorage else use CONST_s
    CenterLat = Number(localStorage['CenterLat']) || CONST_CENTERLAT;
    CenterLon = Number(localStorage['CenterLon']) || CONST_CENTERLON;
    ZoomLvl   = Number(localStorage['ZoomLvl']) || CONST_ZOOMLVL;
    
    // Set and refresh
	GoogleMap.setZoom(parseInt(ZoomLvl));
	GoogleMap.setCenter(new google.maps.LatLng(parseFloat(CenterLat), parseFloat(CenterLon)));
	
	if (SelectedPlane) {
	    selectPlaneByHex(SelectedPlane);
	}
	
	// Set reset METAR-flag
	MetarReset = true;

	refreshSelected();
    updateTableOfPlanes();
	getMetar();
}

function drawCircle(marker, distance) {
    if (typeof distance === 'undefined') {
        return false;
        
        if (!(!isNaN(parseFloat(distance)) && isFinite(distance)) || distance < 0) {
            return false;
        }
    }
    
    distance *= 1000.0;
    if (!Metric) {
        distance *= 1.852;
    }
    
    // Add circle overlay and bind to marker
    var circle = new google.maps.Circle({
      map: GoogleMap,
      radius: distance, // In meters
      fillOpacity: 0.0,
      strokeWeight: 1,
      clickable: false,
      strokeOpacity: 0.3
    });
    circle.bindTo('center', marker, 'position');
}

function drawAntennaData(marker) {
    if (!AntennaDataShow) {
        if (AntennaDataPath && typeof AntennaDataPath !== 'undefined') {
            AntennaDataPath.setMap(null);
            AntennaDataPath = null;
        }
        return false;
    }    
    
    if (!marker && (SiteLat && SiteLon)) {
        marker = new google.maps.LatLng(parseFloat(SiteLat), parseFloat(SiteLon));
    }
    
    path = new Array();
    for (var i=0;i<360;i++) {
        if (typeof AntennaData[i] !== 'undefined') {
            var metricDist = AntennaData[i] * 1.852;
            path[i] = google.maps.geometry.spherical.computeOffset(marker, metricDist, i);
        } else {
            path[i] = marker;
        }
    }
    
    if (AntennaDataPath && typeof AntennaDataPath !== 'undefined') {
        AntennaDataPath.setMap(null);
        AntennaDataPath = null;
    }
    
    AntennaDataPath = new google.maps.Polygon({
        paths: path,
        fillColor: '#7f7f7f',
        fillOpacity: AntennaDataOpacity,
        strokeColor: '#7f7f7f',
        strokeWeight: 1,
        strokeOpacity: AntennaDataOpacity,
        clickable: false,
        zIndex: -99998
    });
    AntennaDataPath.setMap(GoogleMap);
}

/** gets csv of requested airport ICAOs as parameter **/
function getMetar(pMetarICAO) {
    if (!pMetarICAO || typeof pMetarICAO === 'undefined') { // as parameter
        if (!MetarIcaoCode || typeof MetarIcaoCode === 'undefined') { // from config.js
            return; // No metar to show
        } else {
            pMetarICAO = MetarIcaoCode;
        }
    }
    
    pMetarICAO = pMetarICAO.replace(/\s/g, "");
    url = 'http://weather.aero/dataserver_current/httpparam?dataSource=metars&' +
            'requestType=retrieve&format=csv&hoursBeforeNow=1&fields=raw_text&' +
            'mostRecentForEachStation=postfilter&stationString=' + pMetarICAO;
     
    //url = 'http://aviationweather.gov/adds/dataserver_current/httpparam?dataSource=metars&' +
    //        'requestType=retrieve&format=csv&hoursBeforeNow=1&fields=raw_text&' +
    //        'mostRecentForEachStation=postfilter&stationString=KCLT';
       
    xReader(url, function(data) {
        if (data.status == Number(200)) {
            csv = data.content.split("\n");
            csv.splice(0,6);
            html = "";
            for(i=0;i<csv.length;i++) {
                csv[i] = csv[i].replace(/,/g,"");
                html += csv[i];
                if (i < csv.length - 1) {
                    html += "<br>";
                }
            }
            document.getElementById('METAR').innerHTML = html;
            if (MetarReset) {
                $("#METAR").position({ my: "left bottom", at: "left+5 bottom-30", of: "#map_canvas" });
                $("#METAR").draggable({ containment: "document" });
                $("#METAR").addClass('ui-state-highlight');
                $('#METAR').show();
                MetarReset = false;
            }
        }
    });
}

/* Store objects as string to localStorage */
Storage.prototype.setObject = function(key, value) {
    this.setItem(key, JSON.stringify(value));
}

/* Get string objets from localStorage */
Storage.prototype.getObject = function(key) {
    var value = this.getItem(key);
    return value && JSON.parse(value);
}

/* Get size of object */
Object.size = function(obj) {
    var size = 0, key;
    for (key in obj) {
        if (obj.hasOwnProperty(key)) size++;
    }
    return size;
};
