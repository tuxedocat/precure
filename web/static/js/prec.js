
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
				sent : _text
			},
			dataType: 'json',
			async : false
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
		if (_text == undefined || _text.length < 0){
			return undefined;
		};

		$.ajax({
			url: '/split',
			type: 'GET',
			data: {
				text : _text
			},
			dataType: 'json',
			async : false
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




	function setContentForNonIE(ed, new_decorated_txt){
		var sel = ed.selection.getSel();
		var range = ed.selection.getRng();

		var basenode = sel.baseNode;
		var baseOffset = sel.baseOffset;
		if (baseOffset !=0 && basenode.hasChildNodes() && basenode.childNodes.length > baseOffset){
			basenode = basenode.childNodes[baseOffset];
			baseOffset = 0;
		};
		var position = 0;
		function getDom1(node){
			if (node.nodeName == "BR"){
				if (node == basenode){
					return true;
				};
				position += 1;
			}
			else if(node.data){
				if (node == basenode){
					position += baseOffset;
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

		ed.setContent(new_decorated_txt); //REPLACE !
			
		var iframeElement = $("#elm1_ifr")[0];
		var contentDoc = iframeElement.contentDocument;
		var range = contentDoc.createRange();
		var firstnode = contentDoc.body.firstChild;
		var last_length = position;
		var mynode = firstnode;

		function getDom(node){
			if (node.nodeName == "BR"){
				if (last_length == 0){
					mynode = node;
					return true;
				};
				last_length -= 1;
			}
			else if (node.data){
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
	};

	function setContentForIE(ed, new_decorated_txt){
//                var iframeElement = $("#elm1_ifr")[0];
//                var selection = iframeElement.document.selection;
//                var range = selection.createRange();
//                var sm1 = range.startContainer;
//                var sm2 = range.startOffset;
		var bm = ed.selection.getBookmark(2);

		new_decorated_txt = new_decorated_txt.replace(/ /g, "&nbsp;");
		new_decorated_txt = new_decorated_txt.replace(/\r\n/g, "<br />");
		ed.setContent(new_decorated_txt); //REPLACE !

//                range.move("character", 1);
//                ed.selection.moveToBookmark(bm);
	};

	function setContent(ed, new_decorated_txt){
		if (document.selection) { // IE
			console.log("[" + new_decorated_txt + "]");
			setContentForIE(ed, new_decorated_txt);
		}
		else{
			new_decorated_txt = new_decorated_txt.replace(/\r\n/g, "<br />");
			new_decorated_txt = new_decorated_txt.replace(/(\r|\n)/g, "<br />");
			new_decorated_txt = "<p>" + new_decorated_txt + "</p>";
			var current_decorated_text = ed.getContent();
			if (new_decorated_txt != current_decorated_text){
				setContentForNonIE(ed, new_decorated_txt);
			};
		};
	};

	function myHandleEvent(e) {

		var ed = tinyMCE.get('elm1');
		var txt = ed.getContent({format:'text'});

		if (myBuffer != txt){ //text is changed
			myBuffer = txt; //update buffer
			var spans = split_text(txt);
			if (spans == undefined){
				return true;
			};
			var new_decorated_txt = txt; //copy
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

					//SPELL CHECK!
					var spell_errors = spell_check(str);
					for (var j=spell_errors.length-1; j>=0; --j){
						var err = spell_errors[j];
//                                                console.log(err);
						new_str = new_str.substr(0, err.begin) 
							  + "<u>"
							  + new_str.substr(err.begin, err.end - err.begin) 
							  + "</u>"
							  + new_str.substr(err.end);
					};
					myDecorationBank[str] = new_str;
				};

				//replace
				new_decorated_txt = new_decorated_txt.substr(0, beg) 
					+ new_str
					+ new_decorated_txt.substr(end)
			};
			setContent(ed, new_decorated_txt);
		};

		return true; // Continue handling
	};


		myBuffer = ''; //save old plain text
		myDecorationBank = []; //save old plain sentences


