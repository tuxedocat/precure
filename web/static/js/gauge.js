

google.load('visualization', '1', {packages:['gauge']});
google.setOnLoadCallback(drawChart);
function drawChart() {
var data = google.visualization.arrayToDataTable([
['Label', 'Value'],
['Fluency', 80],
]);

var options = {
	width: 180, height: 180,
	redFrom: 0, redTo: 33.3,
	yellowFrom:33.3, yellowTo: 66.6,
	greenFrom:66.6, greenTo: 100,
	minorTicks: 5
};

var chart = new google.visualization.Gauge(document.getElementById('fluency_chart'));
chart.draw(data, options);
}
