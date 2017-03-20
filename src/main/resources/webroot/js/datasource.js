(function ($) {
	'use strict';

	var eb = new vertx.EventBus("http://" + location.host + "/eventbus");
	eb.onopen = function() {
		console.log("open");
		eb.registerHandler("dashboard", function(data) {
			var entry = JSON.parse(data);
			var dobj = new Date();
			var ts = dobj.getTime();
			console.log(entry);
			switch (entry.mac) {
				case '18-FE-34-1A-49-B6':
				console.log("mac hit" + ts + entry.amplitude / 100);
				$('.jke-ecgChart').ecgChart('addDataPoint', { x: ts, y: entry.amplitude / 100});
			}

			//var array = JSON.parse(data);
			//demoData.forEach(function(entry) {
			//	//console.log({ x: entry[0], y: entry[1]/100});
			//	console.log(entry);
			//	//$('.jke-ecgChart').ecgChart('addDataPoint', { x: entry.ts, y: entry.value/100});
			//});
		});
	};


})($);
