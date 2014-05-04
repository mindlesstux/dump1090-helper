function optionsInitalize() {

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

    $(function() {
        $( "#slider-range" ).slider({
            range: true,
            min: 0,
            max: 99000,
            step: 1000,
            values: [ markerFLFilter[0], markerFLFilter[1] ],
            slide: function( event, ui ) {
                $( "#amount" ).val( "FL" + zeroPad(ui.values[0], 5).slice(0, 3) + " - FL" + zeroPad(ui.values[1], 5).slice(0, 3) );
                markerFLFilter[0] = ui.values[0];
                markerFLFilter[1] = ui.values[1];
                localStorage['markerFLFilter'] = JSON.stringify(markerFLFilter);
            }
        });
        $( "#amount" ).val( "FL" + zeroPad($( "#slider-range" ).slider( "values", 0 ), 5).slice(0, 3) + " - FL" + zeroPad($( "#slider-range" ).slider( "values", 1) , 5).slice(0, 3) );
    });

}

function downloadBaseCoverage() {
    var blob = new Blob([JSON.stringify(AntennaData)], {type: "text/plain;charset=utf-8"});
    saveAs(blob, "antennaBaseCoverage.txt");
}

function zeroPad(num, numZeros) {
    var n = Math.abs(num);
    var zeros = Math.max(0, numZeros - Math.floor(n).toString().length );
    var zeroString = Math.pow(10,zeros).toString().substr(1);
    if( num < 0 ) {
        zeroString = '-' + zeroString;
    }

    return zeroString+n;
}