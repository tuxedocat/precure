if (document.location.protocol == 'file:') {
	alert("The examples might not work properly on the local file system due to security settings in your browser. Please use a real webserver.");
}

function myOnSetupContent(editor_id, body, doc) {
	var el = document.getElementById(editor_id+"_path_row");
	if (el) {el.style.display="none";}
	if (getEditorContent()=="") {setEditorContent(getTypeHere());}
}


var SPELL_ERRORS = [];
function spell_check(_text) {
	$.ajax({
		url: '/spell',
		type: 'GET',
		data: {
			sent : _text,
		},
		dataType: 'json'
		})
		.success(function( data ) {
			SPELL_ERRORS = data.errors;
		})
		.error(function( data ) {
		})
		.complete(function( data ) {
		});
	return SPELL_ERRORS;
};


var SPANS = {spans : []}
function split_text(_text) {
	$.ajax({
		url: '/split',
		type: 'GET',
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

	var ed = tinyMCE.get('elm1');
	txt = ed.getContent({format:'text'});


	if (myBuffer != txt){ //text is changed
		myBuffer = txt;
		tmp = new Array(0);
		tmpMod = new Array(0);
		spans = split_text(txt);
		for (var i=spans.length-1; i>=0 ; --i){
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
				var spell_errors = spell_check(txt);
				for (var j=0; j<spell_errors.length; ++j){
					var err = spell_errors[j];
					_info = [beg + err.begin, beg+err.end, err.description];
					tmpMod.unshift(_info);
				};
			};
		};
		//replace! Do from the last
		newtxt = txt
		for (var j=0; j<tmpMod.length; ++j){
			var _info = tmpMod[j];
			beg = _info[0];
			end = _info[1];
			html = _info[2];

			newtxt = newtxt.substr(0, beg) 
				+ html 
				+ newtxt.substr(end)
		};

	
	 var bm = tinyMCE.activeEditor.selection.getBookmark(2);
//         var bm = tinyMCE.activeEditor.selection.getBookmark(2, true);
	 tinyMCE.activeEditor.setContent(newtxt);
	 tinyMCE.activeEditor.selection.moveToBookmark(bm);

		console.log(newtxt);	
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
