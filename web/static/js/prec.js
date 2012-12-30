
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
			dataType: 'json',
			async : false,
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
			dataType: 'json',
			async : false,
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
		var txt = ed.getContent({format:'text'});

		if (myBuffer != txt){ //text is changed
			console.log("changed!\nold: [" + myBuffer + "] new: [" + txt + "]");
			myBuffer = txt; //update buffer
			var spans = split_text(txt);
			var new_txt = txt; //copy
			for (var i=spans.length-1; i>=0 ; --i){ //for each sentence
				var beg = spans[i][0];
				var end = spans[i][1];
				var str = txt.substr(beg, end -  beg );

				var new_str = '';
				if (str in myDecorationBank){
					new_str = myDecorationBank[str];
				}
				else{
					new_str = str; //copy
					var spell_errors = spell_check(str);
					for (var j=spell_errors.length-1; j>=0; --j){
						var err = spell_errors[j];
						console.log(err);
						new_str = new_str.substr(0, err.begin) 
							+ err.description
							+ new_str.substr(err.end);
					};
					myDecorationBank[str] = new_str;
				};

				//replace
				new_txt = new_txt.substr(0, beg) 
					+ new_str
					+ new_txt.substr(end)
			};

			if (new_txt != txt){
				var sel = ed.selection.getSel();
				var range = ed.selection.getRng();

				var basenode = sel.baseNode;
				var position = 0;
				function getDom1(node){ //node, last_length){
					if(node.data){
						if (node == basenode){
							position += sel.baseOffset;
							return true;
						}
						else{
							position += node.data.length;
						};
					};
					node = node.firstChild;
					while(node){
						var f = getDom1(node);
						if (f)
							return true;
						node = node.nextSibling;
					};
					return false;
				};
				var iframeElement = $("#elm1_ifr")[0];
				var contentDoc = iframeElement.contentDocument;
				var firstnode = contentDoc.body.firstChild;
				getDom1(firstnode);
				console.log(position);
				

				ed.setContent(new_txt);
					
				var iframeElement = $("#elm1_ifr")[0];
				var contentDoc = iframeElement.contentDocument;
				var range = contentDoc.createRange();
				var firstnode = contentDoc.body.firstChild;
				var last_length = position;
				var mynode = firstnode;

				function getDom(node){ //node, last_length){
					if(node.data){
						if (last_length <= node.data.length){
							mynode = node;
							return true;
						}
						else{
							last_length -= node.data.length;
						};
					};
					node = node.firstChild;
					while(node){
						var f = getDom(node);
						if (f)
							return true;
						node = node.nextSibling;
					};
					return false;
				};
				
				getDom(firstnode);
				range.setStart(mynode, last_length);
				range.setEnd(mynode, last_length);

				var selection = iframeElement.contentWindow.getSelection();
				selection.removeAllRanges();
				selection.addRange(range);

//                                return false;
			};
		};

		return true; // Continue handling
	};


		myBuffer = ''; //save old plain text
		myDecorationBank = []; //save old plain sentences


