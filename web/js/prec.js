if (document.location.protocol == 'file:') {
	alert("The examples might not work properly on the local file system due to security settings in your browser. Please use a real webserver.");
}

function myOnSetupContent(editor_id, body, doc) {
	var el = document.getElementById(editor_id+"_path_row");
	if (el) {el.style.display="none";}
	if (getEditorContent()=="") {setEditorContent(getTypeHere());}
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
	});

//

