
function hpLib_getEvent (e, inwin) {
	if (e && e.target) {return e;}
	if (inwin && inwin.event) {return inwin.event;}
	else if (window.event) {return window.event;}
	return null;
}

function hpLib_getElementFromEvent (e) {
	var el = null;
	if (e && e.target) {
		el=e.target;
  		e.cancelBubble = true;
	}
	else if (e && e.srcElement) {
		el = e.srcElement;
  		e.cancelBubble = true;
	}
	else if (window.event) {
		el = window.event.srcElement;
  		window.event.cancelBubble = true;
	}
	return el;
}

function hpLib_getMousePositionFromEvent (e) {
	var el = hpLib_getElementFromEvent(e);
	var win = hpLib_getWinFromElement(el);
	var mousePosition = new Array(2);
	mousePosition[0] = 0;
	mousePosition[1] = 0;
	if (e && e.type) {}
	else if (win.event) {e = win.event;}
	if (e) {
		if (false && e.pageX != undefined) {
			mousePosition[0] = e.pageX;
			mousePosition[1] = e.pageY;
		}
		else if (e.clientX != undefined) {
			var winScroll = hpLib_getWindowScroll(win);
			mousePosition[0] = e.clientX + winScroll[0];
			mousePosition[1] = e.clientY + winScroll[1];
		}
	}
	return mousePosition;
}

function hpLib_getWindowDimensions (win) {
	win = win ? win : window;
	var winDimensions = new Array(2);
	winDimensions[0] = 0;
	winDimensions[1] = 0;
	if (window.innerWidth) {
		winDimensions[0] = win.innerWidth;
		winDimensions[1] = win.innerHeight;
	}
	else if (document.body) {
		winDimensions[0] = win.document.body.scrollWidth;
		winDimensions[1] = win.document.body.scrollHeight;
    }
    return winDimensions;
}

function hpLib_getWindowScroll (win) {
	win = win ? win : window;
	doc = win.document;
	var winScroll = new Array(2);
	winScroll[0] = 0;
	winScroll[1] = 0;
	if (window.scrollX != undefined) {
 		winScroll[0] = win.scrollX;
		winScroll[1] = win.scrollY;
	}
	else if (window.pageXOffset!= undefined) {
 		winScroll[0] = win.pageXOffset;
		winScroll[1] = win.pageYOffset;
	}
	else if (document.documentElement && document.documentElement.scrollTop) {
		winScroll[0] = doc.documentElement.scrollLeft;
		winScroll[1] = doc.documentElement.scrollTop;
	}
	else if (document.body) {
		winScroll[0] = doc.body.scrollLeft;
		winScroll[1] = doc.body.scrollTop;
    }
    return winScroll;
}

// to facilitate XHTML Strict conformance, look for form ID, and then name
function hpLib_getForm(named) {
	var theForm = document.getElementById(named);
	if (theForm) {return theForm;}
	return document.forms[named];
}

function hpLib_getWinFromElement(el) {
	var doc = el.ownerDocument;
	if (doc.defaultView) {return doc.defaultView;}
	else if (doc.parentWindow) {return doc.parentWindow;}
	return null;
}

/**
 * Functions to dynamically create hovering tips.
 *
 * If an element contains a title attribute, the title contents will be displayed in a
 * hovering tip (this works better than the title attribute since you can't 
 * control how the title will appear and you can't have formatting in a title).
 * @author Stéfan Sinclair
 * @version 0.1
 */
 
var currentTip = null;

function hpTips () {
}

function hpTips_showTip (el,e,mode) {

	if (el.nodeType==3) {el=el.parentNode;} // Safari seems to return text nodes as well
	var tip = null;

	if (el.getAttribute("title")) { // does title contain something?
		tip = el.getAttribute("title");
		el.setAttribute("hpTip",tip); // for next time
		if (tip=='') {
			if (el.getAttribute("hpTip")) {
				tip = el.getAttribute("hpTip");
			}
		}
		else {
			el.removeAttribute("title"); // remove the tip so that the browser doesn't show it
			el.title = ""; // for the benefit of MSIE?
		}
	}
	else if (el.getAttribute("hpTip")) {tip=el.getAttribute("hpTip");}

	if (tip!=null) {

		hpTips_removeCurrentTip();
		if (mode=="hover") {
			
			var tipEl = document.createElement("div");
			// for the benefit of MSIE?
			tipEl.style.position = "absolute";
			tipEl.className = "hpTipBox";
			
//			tipEl.setAttribute("style","position: absolute;");
			tipEl.setAttribute("class","hpTipBox");
			tipEl.innerHTML = tip;
			tipEl.style.visibility = "hidden";
			document.getElementsByTagName("body")[0].appendChild(tipEl);
			hpTips_setPosition(el, tipEl, e);
			tipEl.style.visibility = "visible";
			currentTip = tipEl;
		}
		else {
			hpTipWindow = window.open("","hpTipWindow","scrollbars=yes,width=300,height=300");
			hpTipWindow.document.open();
			hpTipWindow.document.write(tip);
			hpTipWindow.document.close();
			hpTipWindow.focus();
		}
	}
}

// allow this setting position to be overrriden
function hpTips_setPosition(el, tipEl, e) {
	hpTips_setPositionDefault(el, tipEl, e);
}

function hpTips_setPositionDefault(el, tipEl, e) {
	var maxWidth = el.ownerDocument.body.offsetWidth;
	var win = hpLib_getWinFromElement(tipEl);
	var winDimensions = hpLib_getWindowDimensions(win);
	var winScroll = hpLib_getWindowScroll(win);
	var mousePosition = hpLib_getMousePositionFromEvent(e);
//	window.status=winScroll[1]+' '+mousePosition[1];
//console.warn(winDimensions,winScroll,mousePosition)
	if (tipEl.offsetWidth>maxWidth/2) {
		tipEl.style.width=(maxWidth/2)+"px";
	}
	if (mousePosition[0]>maxWidth/2) { // right side of the page
		var left = mousePosition[0];
		if (left+tipEl.offsetWidth>maxWidth) {
			var all = left+tipEl.offsetWidth;
			left -= (all-maxWidth);
		}
		tipEl.style.left = left+"px";
//		tipEl.style.left = (mousePosition[0]-tipEl.offsetWidth+el.offsetWidth)+"px";
//		tipEl.style.left = (mousePosition[0]-tipEl.offsetWidth)+"px";
	}
	else {
		tipEl.style.left = mousePosition[0]+"px";
	}
	if (mousePosition[1]-winScroll[1]>winDimensions[1]/2) { // bottom part of page
		tipEl.style.top = (mousePosition[1]-tipEl.offsetHeight-el.offsetHeight)+"px";
	}
	else {
		tipEl.style.top = (25+mousePosition[1]+(el.offsetHeight*1.5))+"px";
	}
	if (parseInt(tipEl.style.top)<1) {
		tipEl.style.top='1px'
	}

}

function hpTips_removeCurrentTip () {
	if (currentTip!=null) {
		document.getElementsByTagName("body")[0].removeChild(currentTip);
		currentTip=null;
	}
}

function hpTips_onMouseOver (e, inwin) {
	ev = hpLib_getEvent(e, inwin);
	el = hpLib_getElementFromEvent(e);
	if (el && el.className.indexOf('mceButton')==-1) {hpTips_showTip(el,ev,'hover');}
}

function hpTips_onMouseOut (e) {
	ev = hpLib_getEvent(e);
	el = hpLib_getElementFromEvent(e);
	if (el && el.getAttribute('hpTip')) {
		hpTips_removeCurrentTip();
	}
}

function hpTips_onClick (e) {
	ev = hpLib_getEvent(e, inwin);
	el = hpLib_getElementFromEvent(e);
	if (el) {hpTips_showTip(el,ev,'click');}
}


	var elements = document.getElementsByTagName('script');
	var baseUrl = window.defaultBaseUrl || document.location.href;
	for (var i=0;i<elements.length;i++) {
		if (elements[i].src.indexOf("nadaclair.js")) {
			baseUrl = elements[i].src.substring(0, elements[i].src.lastIndexOf("/"));
			baseUrl = baseUrl.substring(0, baseUrl.lastIndexOf("/")+1);
		}
	}

	var noLogs = ""; // we'll track here in case people are editing example text
	var iLang = window.defaultInterfaceLanguage || "fr";
	var docLang = window.defaultDocumentLanguage || "fr";
	var origTime = window.defaultOrigTime || new Date().getTime();
	var langVars = {
		"typeHere_en" :
		{
		"en" : 'Type or paste your English text here and click on the "Check Text" button.',
		"fr" : 'Taper ou collez votre texte en anglais ici et cliquez le bouton "Vérifier le texte".',
		"es" : 'Escriba o pegue su texto en inglés aquí y haga clic en el botón "Verificar el texto".'
		},
		"typeHere_es" :
		{
		"en" : 'Type or paste your Spanish text here and click on the "Check Text" button.',
		"fr" : 'Taper ou collez votre texte en espagnol ici et cliquez le bouton "Vérifier le texte".',
		"es" : 'Escriba o pegue su texto en español aquí y haga clic en el botón "Verificar el texto".'
		},
		"typeHere_fr" :
		{
		"en" : 'Type or paste your French text here and click on the "Check Text" button.',
		"fr" : 'Tapez ou collez votre texte en français ici et cliquez le bouton "Vérifier le texte".',
		"es" : 'Escriba o pegque su texto en francés aquí y haga clic en el botón "Verificar el texto".'
		},
		"ajaxResponseError" :
		{
		"en" : "Sorry, an error has occurred in attempting to retrieve results. Please try reloading the page.",
		"fr" : "Désolé, une erreur est survenue. Veuillez essayer d'actualiser la page.",
		"es" : "Lo sentimos, un error ha ocurrido mientras recuperar los resultados. Por favor vuelva a actualizar la página."
		},
		"resetConfirm" :
		{
		"en" : "Are you sure that you want to erase the current text?",
		"fr" : "Êtes-vous sûr de vouloir effacer votre texte?",
		"es" : "¿Está usted seguro que desea borrar su texto?"
		},
		"exampleConfirm" :
		{
		"en" : "Showing an example text will erase the current text - are you sure you want to continue?",
		"fr" : "Afficher un exemple remplacera le texte qui est actuellement dans la boîte - êtes-vous sûr de vouloir continuer ?",
		"es":  "Mostrar un ejemplo reemplazará el texto actual que está en le ventana - ¿está seguro usted que desea continuar?"
		},
		"adsBlocker" :
		{
		"en" : "You appear to be using a blocker of ads. Access to this site remains free in large part because of revenue generated by ads. Please consider paying a nominal fee for the Pro version which doesn't have ads (see the link in the upper right-hand corner of the page). Thank you for your understanding.",
		"fr" : "Il semble que vous utilisez un bloqueur de publicités. L'accès à ce site demeure gratuit en grande partie grâce aux publicités. Veuillez considérer vous abonner à la version Pro qui n'a pas de publicités (voir le lien en haut à gauche de la page). Merci !",
		"es" : "Parece que usted usa un bloqueador de anuncios. El acceso a este sitio es gratis en gran parte por el ingreso generado por los anuncios. Por favor considere pagar una cuata baja por la versión Pro que no tiene anuncios (véase el enalce arriba y a la derecha). ¡Gracias!"
		},
		"progress" :
		{
		"en" : "checking in progress, please wait",
		"fr" : "vérification en cours, veuillez patienter",
		"es" : "verificación en progreso, por favor espere"
		},
		"example" :
		{
		"en" : "My freind wanted too go see a movie last saturday. I told her I culdn't go with out my sister and that made her mad. She said its not really fare that my mom and dad make me take her. My mom said their are times when i have to act like a big sister and take responsability. I told her somtimes it's more better to leave her at home. Anyway, afder we had went to the movies, I said that next time she could take her.",
		"fr" : "Le nom de mon mère est Linda et elle est 40 ans. Elle etait née au Chine et a imigrée ici au Edmonton en 1959, où elle a rencontré mon père. J\'ai un soeur et deux frère. Pendant 5 ans, on a resté dans une petit maison au centre ville. Il y a cinq ans, mes parents ont décidé de déménagé et ils ont nous dit qu´on va changer de maison. J´étais peur parce que je voulais pas perdre mes amis. C´était dificile au début. Un jour, mon père m´a dit: \"il faut que tu fais plus d´effort pour rencontrer des amis, essaye de faire parti d´un club à l´école. J´ai décider d´essayer le club de danse. Toute de suite, j´ai rencontré ma ami Paul et maintenant nous passons beaucoup des jours ensemble. Chaque samedi on va ensembles au centre d´achat et on a un bon temps! Je suis content d\'avoir démenagé ! ",
		"es" : "Soy una estudiante y estoy veinte años. Hace unos anos, viajé a Francia con una amiga por trabajar. Estaba la primera tiempo que estaba en Europa. Estuvo afligada un poco, pero experimenté una cultura diferente. Tenia muy buenos recuerdos de ese tiempo. Me gusto mucho las viajes. Cuando viajaba, encontré muchos personas diferentes. Todos las personas son despreocupada. Soy físicamente activo. Participé en los equipos del voleibo. Sin embargo soy el mas apasionada del baloncesto. Participé en lo equipo del baloncesto en la escuela universitaria. Vencimos muchos de los otros equipo. No me gustar perder. Siempre intenté como mejor puedo. Ahora, solamente jugo el baloncesto para me divertio. Me pongo dichosa. Además soy ordenada. cuando estaba ir al escuela universitaria, equilibrada mucho. Fui al escuela, jugué baloncesto, y trabajé a tiempo parcial. Ahora, trabajo a tiempo completo y tomo un clase con muchas y muchas de tareas."
		},
		"exercisesCorrect" :
		{
		"en" : "Congratulations - that is correct!",
		"fr" : "Félicitations ! C'est la bonne réponse ! ",
		"es" : "Felicidades. ¡Eso es correcto!"
		},
		"exercisesIncorrect" :
		{
		"en" : "Unfortunately that is not the correct answer - please try again.",
		"fr" : "Malheureusement cela n'est pas la bonne réponse - veuillez essayer encore.",
		"es" : "Desafortunadamente eso no es la respuesta correcta – por favor vuelva a intentar."
		},
		"popNoReceiver" :
		{
		"en" : "The window that opened this window does not have a necessary function; please check the documentation.",
		"fr" : "Une fonction nécessaire n'a pas été trouvée dans la fenêtre cible ; veuillez vérifier le mode d'emploi.",
		"es" : "Se necesita una función que la ventana actual no tiene; por favor verifique la documentación."
		},
		"popNoOpener" :
		{
		"en" : "This page is meant to be used as a module for another window, but no such window was detected.",
		"fr" : "Cette page est conçue comme module pour une autre fenêtre, mais aucune fenêtre convenable n'a été trouvée.",
		"es" : "Esta página es usa como módulo para otra ventana, pero no se encuentra tal ventana."
		},
		"textTooLong" :
		{
		"en" : "The free version of this site has a maximum text length of 2000 characters (about 250 words). Your text has the following number of characters:",
		"fr" : "Dans la version gratuite de ce site, les textes ne peuvent pas dépasser 2 000 caractères (environ 250 mots). Votre texte a le nombre de caractères suivant :",
		"es" : "La versión gratis de este sitio puede manejar los textos de un máximo de 2000 caracteres (aproximadamente 250 palabras). Su texto tiene el siguiente número de caracteres:"
		},
		"textTooLongTrial" :
		{
		"en" : "This trial Pro account has all of the functionality of a regular Pro account except that there's a maximum text length of 2000 characters (about 250 words). Your text has the following number of characters:",
		"fr" : "Ce compte d'essai de la version Pro a toute la fonctionnalité de la version Pro sauf que les textes ne peuvent pas dépasser 2 000 caractères (environ 250 mots). Votre texte a le nombre de caractères suivant :",
		"es" : "Esta cuenta a prueba de la versión Pro tiene toda la funcionalidad de la versión Pro menos que hay límite de 2000 caracteres (aproximadamente 250 palabras) que puede manejar. Su texto tiene el siguiente número de caracteres:"
		},
		"redirectToPro" :
		{
		"en" : "You cannot submit the current text without making it shorter. The Pro version of the site doesn't not have any length restrictions. Do you wish to visit the Pro site (where you can create a free trial account)?",
		"fr" : "Vous ne pouvez pas soumettre ce texte sans le raccourcir. La version Pro du site n'a pas de contraintes de longueur. Désirez-vous visiter la version Pro du site (où vous pourrez créer un compte d'essai gratuitement) ?",
		"es" : "No puede presentar el texto actual sin hacerlo más corto. La versión Pro del sitio no tiene límite de caracteres. ¿Desea usted visitar el sitio de la versión Pro (donde podrá crear una cuenta a prueba gratis)?"
		},
		"inProgress" :
		{
		"en" : "Text correction is already in progress. Do you wish to continue?",
		"fr" : "La correction du texte est déjà en cours ; désirez-vous continuer ?",
		"es" : "La corrección del texto ya está en progreso. ¿Desea continuar?"
		},
		"tryPro" :
		{
		"en" : "\nWe are delighted that you are finding our site useful. Please consider showing your support for this project by becoming a Pro subscriber; advantages include:\n\t* no ads\n\t* no imposed limit on text length\n\t* resizable editor\n\t* personal writing portfolio\n\t* interactive grammar exercises\n\t* integrated vocabulary tools\nOnly €11,99 per year (about $15) - create a free trial account!",
		"fr" : "\nNous sommes ravis que vous trouviez notre site utile. Si vous désirez appuyer le projet, veuillez considérer un abonnement à la version Pro ; parmi les avantages : \n\t* aucune publicité\n\t* aucune restriction de longueur\n\t* éditeur redimensionnable\n\t* dossier d'écriture personnel\n\t* exercices de grammaire interactifs\n\t* outils de vocabulaire intégrés\nSeulement 11,99 € par année (environ 15 $) - créez gratuitement un compte d'essai !",
		"es" : "\nNos da mucho gusto que usted encuentre el sitio tan útil. Por favor considere apoyar este proyecto e inscribirse a la versión Pro; las ventajas incluyen:\n\t* no hay anuncios\n\t* no hay límite de caracteres en el texto\n\t* editor redimensionable\n\t* portafolio personal\n\t* ejercicios interactivos de gramática\n\t* herramienta integrada de vocabulario\nSólo 11,99 € por año (más o menos 15 $) –¡crear una cuenta gratis!"
		},
		"proOnlyFunction" :
		{
		"en" : "This function is only available in the Pro version.", // Do you wish to visit the Pro site (where you can create a free trial account)?",
		"fr" : "Cette fonction n'est disponible que dans la version Pro.", // Désirez-vous visiter la version Pro du site (où vous pourrez créer un compte d'essai gratuitement) ?"
		"es" : "Esta opción sólo está disponible de la versión Pro."//¿Desea visitar el sitio de la versión Pro (donde podrá crear una cuenta a prueba gratis)?"
		}

	}
	
	var currentEditorId = null;
	function getEditor(ev) {
		return tinyMCE.activeEditor
//		var id = getEditorId(ev);
//		return tinyMCE.getInstanceById(id);
	}
	function getEditorId(ev) {
		return getEditor().id;
//		return currentEditorId;
	}
	function myOnKeyDown(e) {
		e = e ? e : window.event;

		// FIXME : make sure this works in IE
		// ignore for login field
		var el = hpLib_getElementFromEvent(e);
		if (el && (el.tagName=="INPUT" || (el.tagName=='TEXTAREA' && el.className=='question'))) {return;}
		// try to avoid delete key changing pages
		var editor = getEditor(e);
		if (editor) {	
			if (e && (e.keyCode && e.keyCode==8) || (e.which && e.which==8)) {
				window.status=e.which;
				// when selecting all in Safari the parent window is selected, so ask for deletion
				if (navigator.userAgent.indexOf("Safari")>-1) {confirmReset();}
				return false;
			}
			editor.getWin().focus();
		}
		return true;
	}
	function myCustomOnChangeHandler(inst) {
		var el = inst.selection.getNode();
		if (el && el.tagName=="SPAN" && (el.className=="ver" || el.className=="mod" || el.className=="spellmod" || el.className=="spellver")) {
			el.className+="updated";
		}
	}
	
	function myCustomSetup(ed) {
		ed.onInit.add(function(ed) {
			var doc = ed.getDoc();
			Event.observe(doc, 'mouseover', myTips_onMouseOver);
			Event.observe(doc, 'mouseout', hpTips_onMouseOut);
			Event.observe(doc, 'click', editorClick);
			Event.observe(doc, 'click', myTips_onMouseOver);
			
		})
	}
	function myCustomInitInstance() {

		var inst = getEditor();
		var o = inst.getDoc();
		
		Event.observe(o, 'mouseover', myTips_onMouseOver);
		Event.observe(o, 'mouseout', hpTips_onMouseOut);
		Event.observe(o, 'click', editorClick);
		Event.observe(o, 'click', myTips_onMouseOver);
		inst.focus();
//		tinyMCE.execCommand('mceFocus',false,inst.id);
		
// TODO: test in Opera
		// report of a clicking problem in Opera
//		if (navigator.userAgent.indexOf("Opera")==-1) {tinyMCE.addEvent(o, "click", editorClick);}
		customInitEditorInstance(inst);
	}
	
	// intended to be overridend
	function customInitEditorInstance(inst) {}
	
	function getLangVar(key) {
		return langVars[key][iLang];
	}
	function getTypeHere() {
		return getLangVar("typeHere_"+docLang)
	}
	
	function editorClick(e) {
		if (tinyMCE.activeEditor.getContent().replace(/&quot;/g,'"')==getTypeHere()) {tinyMCE.activeEditor.setContent("");}
		return true;
	}
	function myTips_onMouseOver(e) {
		// capture event so that iFrame event can be passed to IE
		if (e && e.target) {hpTips_onMouseOver(e);}
		else {
			var el = getEditor(e).getDoc().parentWindow;
			if (el && el.event) {hpTips_onMouseOver(el.event)}
		}
	}
	
	function getFrameWidth() {
		if (self.innerWidth) {return self.innerWidth;}
		else if (document.documentElement && document.documentElement.clientWidth) {return document.documentElement.clientWidth;}
		else if (document.body) {return document.body.clientWidth;}
		return 1;
	}
	
	// override default tip location
	function hpTips_setPosition(el, tipEl, e) {
		var editor = getEditor(e);
		if (editor && el.ownerDocument==editor.getDoc()) {
			var feedback = $("feedback");
			if (feedback && false /* avoid layering issue with flash-baed google ads */) {
				var pos = feedback.cumulativeOffset();
				var left = pos[0];
				var top = pos[1];
				if (tipEl.offsetWidth>editor.offsetWidth) {
					tipEl.style.width=(editor.offsetWidth>80 ? editor.offsetWidth-50 : 80)+"px";
				}
				tipEl.style.top = (top+10)+"px"; // top of editor
				tipEl.style.left = (left+10)+"px"; // top of editor
			}
			else { // pro – we'll use this for all because of google ad problems
				hpTips_setPositionDefault(el, tipEl, e);
				if (getEditor().id=='mce_fullscreen') {
					tipEl.style.zIndex = "4000000";
				}
				else { //firefox & chrome
					
					var pos = editor.getContainer().cumulativeOffset ? editor.getContainer().cumulativeOffset() : findPos(editor.getContainer());
					var editorScroll = hpLib_getWindowScroll(editor.getWin())
					tipEl.style.top = (parseInt(tipEl.style.top)+pos[1]-editorScroll[1])+"px"
					//window.status=pos[1]+' '+editorScroll[1]
return					
//					var maxWidth = el.ownerDocument.body.offsetWidth;
//					var win = hpLib_getWinFromElement(tipEl);
//					var winDimensions = hpLib_getWindowDimensions(win);
//					var winScroll = hpLib_getWindowScroll(win);
//					var mousePosition = hpLib_getMousePositionFromEvent(e);
//					var editorScroll = hpLib_getWindowScroll(editor.getWin())
//					
//					var pos = editor.getContainer().cumulativeOffset ? editor.getContainer().cumulativeOffset() : findPos(editor.getContainer());
//			if (window.console) {console.warn(pos[1],mousePosition[1],winScroll[1],editorScroll[1])}
//			else {window.status=pos[1]+' '+mousePosition[1]+' '+winScroll[1]+' '+editorScroll[1]}
//					tipEl.style.top = ((pos[1]+mousePosition[1])-editorScroll[1])+"px"
//					return
					
					
					
					var editorWinScroll = hpLib_getWindowScroll(editor.getWin())
					if (editor.getContainer().cumulativeOffset) {
						var pos = editor.getContainer().cumulativeOffset()
						var left = pos[0];
						var top = pos[1];
						var editorWinScroll = hpLib_getWindowScroll(editor.getWin())
						tipEl.style.top = ((parseInt(tipEl.style.top)+top)-editorWinScroll[1])+"px";
					}
					else { // windows
						//var pos = findPos(editor.getContainer());
						//tipEl.style.top = (pos[1]-editorWinScroll[1])+"px";
						
					}
//					var pos = editor.getContainer().cumulativeOffset ? editor.getContainer().cumulativeOffset() : [0,0] ; //findPos(editor.getContainer());
//					var left = pos[0];
//					var top = pos[1];
//					var editorWinScroll = hpLib_getWindowScroll(editor.getWin())
//					window.status= parseInt(tipEl.style.top)+" "+top+" "+editorWinScroll[1]
//console.warn(parseInt(tipEl.style.top), top, editorWinScroll, editor.getWin())
//					tipEl.style.left = el.style.offsetLeft;
//					tipEl.style.left = (parseInt(tipEl.style.left) > (editor.offsetWidth/2) ? (left+10) : parseInt(tipEl.style.left))+"px"; // top of editor
//					tipEl.style.top = ((parseInt(tipEl.style.top)+top)-editorWinScroll[1])+"px";
//					tipEl.style.top = top+"px";
//					tipEl.style.left = ($(currentEditorId).offsetWidth-tipEl.offsetWidth)+"px";
	//				var pos = tinyMCE.getAbsPosition(getEditor().getData('fullscreen').enabled ? document.body : $(currentEditorId), document.body);
	//				tipEl.style.top = (parseInt(tipEl.style.top)+pos.absTop-20)+"px";
				}
			}
		}
		else {hpTips_setPositionDefault(el, tipEl, e);}
	}
	
	// http://stackoverflow.com/questions/1910113/offset-height-using-prototype
	function findPos(obj) {
	    //find coordinates of a DIV
	    var curleft = curtop = 0;
	    if (obj.offsetParent) {
	        curleft = obj.offsetLeft
	        curtop = obj.offsetTop
	        while (obj = obj.offsetParent) {
	            curleft += obj.offsetLeft
	            curtop += obj.offsetTop
	        }
	    }
	    return [curleft, curtop];
	}


	function myOnSetupContent(editor_id, body, doc) {
		var el = document.getElementById(editor_id+"_path_row");
		if (el) {el.style.display="none";}
//		if (getEditorContent()=="") {setEditorContent(getTypeHere());}
	}

	
	var inProgress = null;
	function revertInProgress() {
		if (inProgress!=null) {
			tinyMCE.activeEditor.setContent(inProgress);
			inProgress = null;							
		}
	}
	var submissionCounter = 0;
	
	function isPro() {
		return !window.defaultResizableEditor && (!$("summarycontainer") || $("ist")) ? false : true;
	}
	function ajaxCorrect(editor_id, additionalParams) {
		if (inProgress!=null) {
			if (!confirm(getLangVar("inProgress"))) {
				setTimeout("revertInProgress()", 10); // may have changed since confirmation
			}
			return false;
		}
		var editor = getEditor();
		if (!editor) {return true;} // tinyMCE not working
		var content = tinyMCE.activeEditor.getContent();
		inProgress = content;
		content = encodeURIComponent(content).replace(/^%C2%A0/, ""); // remove initial bizarre space
		if (!window.defaultResizableEditor && (!$("summarycontainer") || $("ist"))) { // not pro
			var contentLength = tinyMCE.activeEditor.getContent().replace(/<.*?>/g,"").replace(/&.+?;/g,"e").length;
			if (contentLength>2000) {
				alert(getLangVar("textTooLong" + ($("ist") ? "Trial" : ""))+" "+contentLength+"\n\n"+getLangVar("tryPro"))
				inProgress = null;
				return false;
			}
			else if (!$("ist") && submissionCounter==0 || submissionCounter==4) {
				alert(getLangVar("tryPro"));
			}
			submissionCounter++;
		}
		params = "isAjax=true&origTime="+origTime+"&docLang="+docLang+"&iLang="+iLang
		var inForm = document.content;
		if (inForm) {
			if (inForm.sex) {params += "&sex="+(inForm.sex.checked ? "f" : "m");}
			if (inForm.isL1) {params += "&isL1="+ (inForm.isL1.checked ? "1" : "");}
			if (inForm.noSpacePunct) {params += "&noSpacePunct="+(inForm.noSpacePunct.checked ? "1" : "");}
			if (inForm.passive) {params += "&passive="+(inForm.passive.checked ? "1" : "");}
			if (inForm.spellchecker) {params += "&spellchecker="+inForm.spellchecker.value;}
		}
		
		if (noLogs==1) {params+="&noLogs=1";}
		if (additionalParams) {params+="&"+additionalParams;}
		// alert(params)
		params +="&typedText="+content+"&referer="+encodeURI(baseUrl)
		var url = getAjaxProxy();
		var progress = '<div style="text-align: center;padding-top:10px;"><img src="'+baseUrl+'Resources/indicator.white.gif" width="16" height="16" alt="working" /> '+getLangVar("progress")+'</div>';
		var myAjax = new Ajax.Request( 
			url,
			{ 
				method : "post",
				parameters : params,
				onLoading: tinyMCE.activeEditor.setContent(progress),
				onComplete: showResponse,
				onFailure: showFailure
			});
		if (window.urchinTracker) {urchinTracker(url);}
		return false;
	}
	function getAjaxProxy() {
		return baseUrl+"ajax";
	}
	
	function showResponse(originalRequest) {
		if (inProgress==null) {return;} // in case it's been cancelled
		var matches = originalRequest.responseText.match(/.*?<text>(.*?)<\/text>.*?<summary>(.*?)<\/summary>.*?<mark>(.*?)<\/mark><words>(.*?)<\/words/m);
		if (matches) {

			// if $withPro && !$isPro
			// if (!window.urchinTracker && $("feedback")) {alert(getLangVar("adsBlocker"));}

			tinyMCE.activeEditor.setContent(matches[1]);
			//tinyMCE.execCommand("mceStartTyping");
			
			// additional fields
			if ($("summarycontainer")) {
				$("summarycontainer").style.display = "";
				$("summary").innerHTML = matches[2];
				if ($("mark")) {$("mark").innerHTML = matches[3];}
				if ($("words")) {$("words").innerHTML = matches[4];}
				if ($("show-explanations-toggle") && window.showExplanationsShow) {$("show-explanations-toggle").innerHTML=showExplanationsShow}
			}
			if ($("uppersubmit") && getFrameWidth()<800) {$("uppersubmit").style.display="none";}
			if ($("legend")) {$("legend").style.display = "";}
			if ($("questions")) {$("questions").style.display = "";}
		}
		else {
			matches = originalRequest.responseText.match(/.*?<error>(.*?)<\/error>/m);
			if (matches) {tinyMCE.activeEditor.setContent("<span class='spellmod'>"+matches[1]+"</span><br /><br />"+inProgress);}
			else {tinyMCE.activeEditor.setContent(getLangVar("ajaxResponseError")+inProgress);}
		}
		inProgress = null;
 		tinyMCE.execCommand("mceFocus",false,getEditorId());
 	}
	
	function showFailure() {
		if (inProgress==null) {return;} // in case it's been cancelled
		tinyMCE.activeEditor.setContent(getLangVar("ajaxResponseError")+inProgress);
		inProgress = null;
		tinyMCE.execCommand("mceFocus",false,getEditorId());
 	}

	function confirmShowExample() {
		if (getEditorContent().length==0 || confirm(getLangVar('exampleConfirm'))) {
			setEditorContent(langVars["example"][docLang]);
			noLogs=1;
			if (document.content) {document.content.submitbutton.click();}
		}
	}
	function confirmReset() {
		if (confirm(getLangVar("resetConfirm"))) {
			noLogs = "";
			setEditorContent("");
		}
	}
	function setEditorContent(newcontent) {
		var editor = getEditor();
		if (editor) {tinyMCE.activeEditor.setContent(newcontent);}
		else if (document.content) {document.content.typedText.value=newcontent;}
	}
	
	function setEditorFocus() {
		var editor = getEditor();
		if (editor) {	
			tinyMCE.execCommand("mceFocus",false,getEditorId());
		}
		else if (document.content) {
			document.content.typedText.focus();
		}
	}
	
	function getEditorContent() {
		var editor = getEditor();
		if (editor) {return tinyMCE.activeEditor.getContent();}
		else if (document.content) {
			return document.content.typedText.value;
		}
		return "";
	}
	function insertChar(chr) {
		if (!isPro()) {
			alert(getLangVar('proOnlyFunction'));
			return false;
		}
		var editor = getEditor();
		var hasUpdated = false;
		if (editor) {
			var before = tinyMCE.activeEditor.getContent();
			var inst = tinyMCE.selectedInstance;
			//this.restoreSelection();
			inst.execCommand("mceInsertContent", false, chr);
			hasUpdated = before!=tinyMCE.activeEditor.getContent();
		}
		if (document.content && !hasUpdated) {
			inText = document.content.typedText;
			if (document.selection) {
				try {inText.focus();} catch (e) {}
				selected = document.selection.createRange();
				selected.text = chr;
			} else if (inText.selectionStart || inText.selectionStart == '0') {
				var startPos = inText.selectionStart;
				var endPos = inText.selectionEnd;
				inText.value = inText.value.substring(0, startPos) + chr + inText.value.substring(endPos, inText.value.length);
				inText.selectionStart = startPos+1;
				inText.selectionEnd = inText.selectionStart;
			} else {
					inText.value += chr;
			}
			try {inText.focus();} catch (e) {}
	        var ua = navigator.userAgent.toLowerCase();
	        var isIE8 = /msie /.test(ua);
	        if (isIE8) { // huge hack because of problem with IE8
	        	setTimeout(function() {
	        		var t = document.getElementById('top')
	        		if (t.innerText.charAt(0)==chr) {
	        			t.firstChild.deleteData(0,1);
	        		}
	        		else {alert(document.getElementById('top').innerText.charAt(0))}
	        	},1)
	        }
			var t = document.getElementById('top').innerHTML;
			return false
		}
	}
	function cleanNadaclairEditor(editor_id) {
		setEditorContent(getEditorContent().replace(/<span\b.*?>/,"").replace(/<\/span>/,""))
	}
	
	function handleExercise (userAnswer, evalString) {
		evalString = evalString.replace(/’/,"'");
		var parts = evalString.split(';');
		userAnswer = userAnswer.replace(/^\s*(.+?)\s*$/,'$1');
		for (var i=0;i<parts.length;i++) {
			var answer = parts[i].split('=');
			reg = new RegExp('^'+answer[0]+'$');
			if (userAnswer.match(reg)) {
				if (answer[1]=='true') {getLangVar("exerciseCorrect");}
				else if (answer[1]=='false') {getLangVar("exerciseIncorrect");}
				else {alert(answer[1]);}
				break;
			}
		}
	}
	
	function doneClose() {
		var text = getEditorContent()
		text = text.replace(/<br\b.*?>/g, "\n");
		text = text.replace(/<\/p\b.*?>/g, "\n\n");
		text = text.replace(/<.*?>/g, "");
		if (window.opener) {
			if (window.opener.nadaclairReceiveText) {
				window.opener.nadaclairReceiveText(text);
				window.close();
			}
			else {alert(getLangVar("popNoReceiver"));}
		}
		else {alert(getLangVar("popNoOpener"));}
	}
