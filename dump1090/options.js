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
}

function optionsModal() {
	$( "#dialog-modal" ).dialog( "open");
}
