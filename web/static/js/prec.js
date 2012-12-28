if (document.location.protocol == 'file:') {
	alert("The examples might not work properly on the local file system due to security settings in your browser. Please use a real webserver.");
}

function myOnSetupContent(editor_id, body, doc) {
	var el = document.getElementById(editor_id+"_path_row");
	if (el) {el.style.display="none";}
	if (getEditorContent()=="") {setEditorContent(getTypeHere());}
}


var SPANS = {spans : []}
function split_text(_text) {
	$.ajax({
		url: '/split',
		type: 'POST',
		data: {
			text : _text,
		},
		dataType: 'json'
		})
		.success(function( data ) {
			SPANS = data.spans;
		})
		.error(function( data ) {
		})
		.complete(function( data ) {
		});
	return SPANS;
};


function myHandleEvent(e) {

	txt = tinyMCE.get('elm1').getContent({format:'text'});

	if (myBuffer != txt){ //text is changed
		myBuffer = txt;
		tmp = new Array(0);
		spans = split_text(txt);
		for (var i=0; i<spans.length; ++i){
			beg = spans[i][0];
			end = spans[i][1];
			str = txt.substr(beg, end-  beg + 1)
			myline = [beg, end, str]
			tmp.push(myline)
			if(mySentBuffer.length > i && mySentBuffer[i][0] == myline[0] &&
				       	mySentBuffer[i][1] == myline[1] && mySentBuffer[i][2] == myline[2]
					){
			}
			else{
				//XXX do something
				console.log(myline);
			};
		};
		mySentBuffer = tmp;
	};

	return true; // Continue handling
}


//MCE
	tinyMCE.init({
		mode : "textareas",
		theme : "advanced",

		height : "480",
		content_css : "custom.css",
		plugins : "print,searchreplace,paste,fullscreen",
		theme_advanced_buttons1 : "selectall,pastetext,pasteword,"+
		"separator,separator," +
		"search,replace," +
		"charmap,separator," +
		"print," + 
		(window.defaultResizableEditor ? ",separator,fullscreen" : ""),
		theme_advanced_buttons2 : "",
		theme_advanced_buttons3 : "",
		theme_advanced_toolbar_location : "top",
		theme_advanced_toolbar_align : "left",

		handle_event_callback : "myHandleEvent"
	});

	myBuffer = '';
	mySentBuffer = [];
