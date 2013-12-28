var listKMLType = ['Approch', 'Departure', 'Transit', 'Custom1', 'Custom2'];
var listKMLs = localStorage['listKMLs'] || [];

function optionsInitalize() {
	// Write your initalization here
	// Gets called just before the 1-sec function call loop is setup
	$( "#dialog-modal" ).dialog({
		height: 360,
		width: 600,
		modal: true,
		autoOpen: false,
		closeOnEscape: false,
		title: "Settings",
		buttons: [ 
			{ 
				text: "Ok", click: function() { 
					$( this ).dialog( "close" ); 
				} 
			}
		]
	});

	$( "#tabs" ).tabs();

    // Misc Options,
    $("#labelShow").buttonset();
    if(LabelShow) {
        $('#labelShowOn').prop('checked',true).button("refresh");
    } else {
        $('#labelShowOff').prop('checked',true).button("refresh");
    }

	// Antenna coverage
	$("#antennaShow").buttonset();
	$("#antennaCollect").buttonset();
	$("#downloadBaseCoverage").button();
	$("#antennaShowOpacity").slider({
	     min: 0,
	     max: 100,
	     value: (AntennaDataOpacity*100),
	     slide: function(event, ui) {
	        AntennaDataOpacity = ui.value / 100;
	        drawAntennaData();
	     }
	});
	
	if(AntennaDataShow) {
	    $('#antennaShowOn').prop('checked',true).button("refresh");
	} else {
	    $('#antennaShowOff').prop('checked',true).button("refresh");
	}
	
	if(antennaCollect) {
	    $('#antennaCollectOn').prop('checked',true).button("refresh");
	} else {
	    $('#antennaCollectOff').prop('checked',true).button("refresh");
	}
}

function optionsModal() {
	$( "#dialog-modal" ).dialog( "open");
}

function downloadBaseCoverage() {
    var blob = new Blob([JSON.stringify(AntennaData)], {type: "text/plain;charset=utf-8"});
    saveAs(blob, "antennaBaseCoverage.txt");
}
