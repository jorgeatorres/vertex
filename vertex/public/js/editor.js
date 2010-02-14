/*Considerations:
 *This file use JQuery library versión 1.7.2; you must include JQuery in yout html files before including this.  
 */
 
/***********************************************************************************************************/
/* Button  
/*                                                                                                */
/* -> Create a interactive button with hover and pulsed effects
/* -> Usage example: 
/* HTML CODE: <div id="button1"> button text </div>
/* JAVASCRIPT CODE: Button('button1', 100, 20, EventHandler);
/* where 'button1' is the id of the div, 100 and 20 are the desired width and height respectively, and
/* EventHandler is a function that is executes when the click event occurs 
/***********************************************************************************************************/

function Button(ElementID,width,height,onClickFunction,borderColor,borderResaltedColor,backgroundColor,backgroundResaltedColor)
{
	//We get the element first
	var El = $('#' + ElementID);
	
	//We apply the main css style for the button component
	El.addClass('Button');	
	El.css('background-color',backgroundColor);
	El.css('border-color',borderColor);
	
	//Width and Height customized	
	El.css('width', width + 'px');
	El.css('height', height + 'px');
	
	//When the mouse stands over the button, the border becomes
	//brighter and the pointer changes to a hand pointer. When
	//the mouse leaves the button area, the border becomes darker.
	El.hover(function(){
	 El.css('border-color',borderResaltedColor);	 
	 El.css('cursor','pointer');
	},function(){
	 El.css('border-color',borderColor);	 
	});
	
	//Whe the mouse is pressed, the background color change;
	//when the mouse is released, the background color is re-established
	El.mousedown(function(){		
		El.css('background-color',backgroundResaltedColor);
	});
	El.mouseup(function(){
		El.css('background-color',backgroundColor);
	});
	
	//This segment of code assign the given function to the event handler
	//of the div
	El.click(onClickFunction);
}


function InsertSymbol(symbol_command)
{
	editAreaLoader.insertTags("file-" + file_id +"-editor",symbol_command,"");
}

//Inicializa Los diferentes componentes del Editor
$(function(){
	
	var $editor = $('.editor');
	
	var $toolbar = $editor.find('.toolbar');
	var $area = $editor.find('textarea.editor-area');
	var $sidebar = $editor.find('.editor-sidebar');
	
	$toolbar.find('.save-button').click(function(){
		//FIXME: la variable file_id es una variable creada fuera de este ámbito, en el archivo edit.html; esta variable
		//almacena el id del archivo que se está editando, para luego ser utilizado en la función editAreaLoader, que es la forma
		//en la que la documentación del editor propone para obtener el texto de que se está editando.  Si hay una mejor forma de
		//hacer esto (seguramente) hay que cambiarlo, yo pensaría que llamando explicitamente el código de este archivo, y pasando
		//Como parámetro el id del archivo, o finalmente el id construido del textarea, que es lo que EditAreaLoader.getValue necesita.
		$.post($(this).attr('href'), {'content': editAreaLoader.getValue("file-" + file_id +"-editor")}, function(res) {
			alert(res._status);
			
			if (!res._error) {
				$toolbar.find('.download-buttons').css('visibility', 'hidden');
			}			
		}, 'json');
		return false;
	});
	
	$toolbar.find('.compile-button').click(function(){
		$.post($(this).attr('href'), {}, function(res) {
			
			if (!res._error) {
				$toolbar.find('.download-buttons').css('visibility', 'visible');
			}
			
			error_text = "";
			for ( i = 0; i < res.errors.length; i++ )				
				error_text += "Line: " + res.errors[i].line_number + "\nMessage: " + res.errors[i].message + "\n\n";
				
			alert(error_text);
			
		}, 'json');
		return false;
	});
	
	/* Load LaTeX symbols */
	var $symbol_list = $sidebar.find('.editor-symbol-list');
	//NOTE: (BORRAR EN CUENTA QUEDE CLARO) Se usa la variable "symbols_inner_html" en vez de
	//ir realizando 'append' pues de esta última los símbolos quedaban fuera de la div para cada
	//elemento del accordion.
	var symbols_inner_html = "";
	num_symbols = 1;
	$.get('/extras/latex_get_symbols', {}, function(res){		
			
		$.each(res, function(k,v){			
			symbols_inner_html += '<h3><a href="#">' + k + '</a></h3><div><table cellspacing="0"><tr>';

			SymbolsPerRow = 4;			
			row_counter = 0;
			$.each(v, function(ks, vs){			
				if ( row_counter == SymbolsPerRow )
				{
					symbols_inner_html += "</tr><tr>";
					row_counter = 0;
				}				
				symbols_inner_html += '<td><div OnClick=InsertSymbol("\\' + vs.command + '") id="symbol_' + num_symbols + '"><img src="' + vs.thumb_url + '" title="' + vs.command + '"/></div></td>';				
				row_counter++;																
				num_symbols++;
			});	
			symbols_inner_html += "</tr></table></div>";
		});	
		$symbol_list.append(symbols_inner_html);		
		//Activamos el accordion para los símbolos
		$symbol_list.accordion({ autoHeight: false });
		
		
		//Llamamos la rutina que crea el botón para cada uno de los símbolos
		/*for (i = 1; i <= num_symbols; i++)
		{			
			Button("symbol_" + i,20,20,function(){				
				editAreaLoader.insertTags("file-" + file_id +"-editor","\\alpha", "")
			},'#777777','#444444','#ffffff','#dddddd');
		}*/
		
		for (i = 1; i <= num_symbols; i++)
		{			
			Button("symbol_" + i,20,20,function(){}
			,'#777777','#444444','#ffffff','#dddddd');
		}
	}, 'json');
	
});

function testButton (cmd){
   
    //alert ("Button  is selected " +a);

	//open tag
	var otag ="";
	var ctag ="";

	switch(cmd){
		case "B":
			otag="\\textbf{";
			ctag="}";
		break;
		case "I":
			otag="\\textit{";
			ctag="}";
		break;
		case "U":
			otag="\\underline{";
			ctag="}";
		break;
		//Align
		case "C":		
		break;
		case "L":
		break;
		case "J":
		break;
		
		//list environment
		case "item":
			otag="\\begin{itemize}\n\t\\item ";
			ctag="\n\\end{itemize}";
		break;
		case "enum":
			otag="\\begin{enumerate}\n\t\\item ";
			ctag="\n\\end{enumerate}";
		break;
	}
	editAreaLoader.insertTags("file-" + file_id +"-editor", otag, ctag);
}	

