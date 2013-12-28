
// This is the master lookup
function regLookup(plane) {
	trigger_lookup = false;
	if (plane.country == null)
		trigger_lookup = true;
	if (plane.type == null)
		trigger_lookup = true;
	if (plane.owner == null)
		trigger_lookup = true;
	if (plane.registration == null)
		trigger_lookup = true;

	if (trigger_lookup = true) {
		url_string = "http://dump1090-helper.appspot.com/planesearch/icao24/" + plane.icao.toUpperCase() + ".json"
		$.ajax({
			url: url_string,
			dataType: ajaxDataType,
			success: function(data) {
				//Nothing to see here right now...
			},
		});
		plane.lookedup = true;
	}
}
