function _timeout_cb(){
    $('#flash').animate({'top': '2px'}, 'slow', 'linear', function(){
        setTimeout("$('#flash').fadeOut('slow', function(){ $('#flash').remove(); });", 3000);
    });
}

function flashmsg(msg, type) {
	console.log('deprecated!');
	vertex.flashmsg(msg, type);
}

function center_on_screen(obj) {
    obj.css('top', $(window).height()/2 - obj.height()/2);
    obj.css('left', $(window).width()/2 - obj.width()/2);
}

function TabSet(s, o) {
	var ts = this;
	
	ts.selector = $(s).find('li');
	ts.options = $.extend({output: '#output',
							 default_tab: null}, o);
	ts.output = $(ts.options.output);
	ts.tabs = new Array();
	
	if (ts.selector.length == 0)
		return;
	
	ts.selector.each(function(i,v) {
		var _li = $(v);
		var _a = $(v).children('a');
		var tab = ts.tabs[ts.tabs.length] = {li: _li,
								   a: _a,
								   url: _a.attr('href'),
								   rel: _a.attr('rel').toLowerCase()};
		
		_a.click(function(){
			ts.selector.removeClass('active');
			_li.addClass('active');
			ts.output.load(tab.url);
			
			var _numpos = window.location.href.indexOf('#');
			
			/*if (tab.rel == "" && _numpos >= 0) {
			} else {
				window.location.href = window.location.href.substr(0, _numpos) + '#' + tab.rel;
			}*/
			
			return false;
		});
	});
	
	this.load_by_name = function(name) {
		name = name.toLowerCase();
		
		for (i = 0; i < this.tabs.length; i++) {
			if (this.tabs[i].rel == name) {
				this.tabs[i].a.click();
				return;
			}
		}
	};
	
	if (ts.options.default_tab)
		this.load_by_name(ts.options.default_tab);
}

// FIXME: utilizar clases precisas para el editor (con prototype, etc.) para
// que una "instancia" del editor sea unica y no se termine mostrando una salida
// en un editor que no corresponde al archivo, etc.
// usar timestamps para garantizar unicidad

(function(){
    var _vertex = new Object();
    _vertex.forms = {};
    _vertex.tabs = {};
    _vertex.workspace = {_initialized: false};
    _vertex.editor = {};
    
    _vertex.flashmsg = function(msg, type) {
        var type = !type ? 'ok' : type;
        var $obj = $('<div>').attr('id', 'flash').html($('<div>').addClass(type).html(msg)).hide();
        $('body').prepend($obj);
        center_on_screen($obj);
        $('#flash').fadeIn('slow', function(){ setTimeout("_timeout_cb();", 1500); });            
    };
    
    // Form handling (requires jquery.form)
    _vertex.forms.ajaxform_presubmit = function(form_id) {
        var $form = $('#' + form_id);
        $form.find('.invalid').removeClass('invalid');
        $form.find('.fielderror').remove();
    };
    
    _vertex.forms.handle_form_basic = function(form_id, res, callback) {
        var $form = $('#' + form_id);
        
    	if (res._status != 'ok') {
            if (res.form_errors) {
                // TODO: better integration with all kinds of errors from TW
                $.each(res.form_errors, function(k,v){
                    $form.find('[name="' + k + '"]').addClass('invalid')
                                                    .after($('<span>').addClass('fielderror').html(v));
                });
            }
    	} else {
    		// FIXME: handle redirects to the same page we are in!
    		if (res._redirect) {
    			location.href = res._redirect;
    			//location.reload(true);
    		}
    	}
    	
    	_vertex.flashmsg(res._msg, res._status);
    };
    
    // Tabset
    _vertex.tabs.tabset = function(s, o) {
    	return new TabSet(s, o);
    };
    
    // Workspace
    _vertex.workspace.init = function() {
    	if (_vertex.workspace._initialized) {
    		alert('error');
    		return;
    	}
    	
    	_vertex.workspace.main_tabset = vertex.tabs.tabset('div.project-sidebar',
    													   {output: 'div.workspace-editing-area',
    													   	default_tab: 'project_settings'});
    	_vertex.workspace._initialized = true;
    	
    };
    
    // Editor
    _vertex.editor.save = function() {
    	_vertex.editor.jq.block({message: 'GUARDANDO...'});
    	$.post(_vertex.editor.urls.save,
    			{file_id: _vertex.editor.file_id,
    			 revid: $('#editor-file-last-revision').val(),
    			 content: _vertex.editor.get_content()}, function(res){
    				 _vertex.editor.jq.unblock();
    				 $('#_eamenu li a:first').click(); // FIXME - ugly hack! reload form & "tab" info
    				 vertex.flashmsg(res._msg, res._status);
    			 }, 'json');
    };

    _vertex.editor.compile = function() {
    	_vertex.editor.jq.block({message: 'COMPILANDO...'});
    	$.post(_vertex.editor.urls.compile,
    			{file_id: _vertex.editor.file_id,
    			 content: _vertex.editor.get_content()}, function(res){
    				 _vertex.editor.jq.unblock();
    				 _vertex.editor.jq_output.hide();
    				 _vertex.flashmsg(res._msg, res._status);
    				 
    				 _vertex.editor.jq_output.find('div.output_content').html(res._msg);
    				 
    				 if (res._status == 'ok') {
    					 _vertex.editor.jq_output.find('div.output_content').append('<ul>' + 
    						'<li><a href="' + res.pdf_url + '">Descargar PDF</a></li>' +
    						'<li><a href="' + res.ps_url + '">Descargar PS</a</li>' + 
    						'<li><a href="' + res.dvi_url + '">Descargar DVI</a</li>' +
    						'</ul>');
    				 }
    				 
    				 _vertex.editor.jq_output.find('div.log_content').html('<pre>' + res.latex_log + '</pre>');
    				 
    				 _vertex.editor.jq_output.fadeIn();
    				 
    			 }, 'json');
    };
    
    _vertex.editor.delete_file = function() {
    	// FIXME: do right (in -binary) also
    	location.href = _vertex.editor.urls.delete + '/' + _vertex.editor.file_id;
    };    
   
    _vertex.editor.init = function(opts) {
    	_vertex.editor.file_id = opts.file_id;
    	_vertex.editor.urls = opts.urls;
    	_vertex.editor.jq = $('div#editor_' + opts.file_id);
    	_vertex.editor.jq_area = $('textarea#editor_area');
    	_vertex.editor.jq_actions_toolbar = $('ul#editor-toolbar-main-actions');
    	_vertex.editor.jq_editor_toolbar = $('ul#editor-toolbar-editing-actions');
    	_vertex.editor.jq_output = $('div#editor-misc-output');
    	
    	_vertex.editor.jq_actions_toolbar.find('a.save-button').click(function(){
    		_vertex.editor.save();
    		return false;
    	});
    	
    	_vertex.editor.jq_actions_toolbar.find('a.compile-button').click(function(){
    		_vertex.editor.compile();
    		return false;
    	});
    	
    	_vertex.editor.jq_actions_toolbar.find('a.delete-button').click(function(){
    		_vertex.editor.delete_file();
    		return false;
    	});
    	
    	_vertex.editor.get_content = function() {
    	    return editAreaLoader.getValue('editor_area');
    		//return _vertex.editor.jq_area.val();
    	};
    	
    	/* Symbols */
    	$('#editor-latex-symbols').load('/editor/latex_symbols/', [], function(){
            $('#editor-latex-symbols a').click(function(){
                editAreaLoader.insertTags('editor_area', $(this).attr('title'), '');
                return false;
            });
    	});
        
    	$('.symbols-button').click(function(e){
            $('#editor-latex-symbols').css({'left': e.pageX, 'top': e.pageY}).toggle();
            return false;
        });
        
        $('.bold-button').click(function(){
            editAreaLoader.insertTags('editor_area', '\\textbf{', '}');
            return false;
        });
        $('.italic-button').click(function(){
            editAreaLoader.insertTags('editor_area', '\\textit{', '}');
            return false;
        });
        $('.underline-button').click(function(){
            editAreaLoader.insertTags('editor_area', '\\underline{', '}');
            return false;
        });
        $('.item-button').click(function(){
            editAreaLoader.insertTags('editor_area', "\\begin{itemize}\n\t\\item ", "\n\\end{itemize}");
            return false;
        });
        $('.enum-button').click(function(){
            editAreaLoader.insertTags('editor_area', "\\begin{enumerate}\n\t\\item ", "\n\\end{enumerate}");
            return false;
        });        

    	
    	$.getScript('/js/jquery.blockUI.js');
    	
    	/* Output stuff */
        var $outul = _vertex.editor.jq_output.find('ul');
        
        $outul.find('a.output-link').click(function(){
            $outul.find('li').removeClass('active');
            $(this).parent('li').addClass('active');
            _vertex.editor.jq_output.find('div.log_content').hide();
            _vertex.editor.jq_output.find('div.output_content').show();
            return false;
        });
        
        $outul.find('a.log-link').click(function(){
            $outul.find('li').removeClass('active');
            $(this).parent('li').addClass('active');
            _vertex.editor.jq_output.find('div.output_content').hide();
            _vertex.editor.jq_output.find('div.log_content').show();
            return false;
        });
        
        $outul.find('li.close-link > a').click(function(){
        	/*_vertex.editor.jq_output.find('div.output_content').show();
        	_vertex.editor.jq_output.find('div.output_content').hide();*/
        	_vertex.editor.jq_output.fadeOut();
            
            return false;
        }); 
        
        /* Editor area */
        editAreaLoader.init({
            id: _vertex.editor.jq_area = $('textarea#editor_area').attr('id'),
            start_highlight: true,
            allow_resize: 'both',
            allow_toggle: false,
            word_wrap: true,
            language: 'en',
            syntax: 'latex',
            is_multi_files: false
        });

    };
    
    // Comparison
    _vertex.revisioncompare = {};
    
    _vertex.revisioncompare.init = function(){
	    $('div#revisions-index ul li a').click(function(){
	        var rie = $(this).siblings('div.revision-inline-editor');
	        
	        if (rie.is(':visible')) {
	        	rie.slideUp();
	        } else {
		        $('div.revision-inline-editor').not(rie).slideUp();
		        $('div.editor').not(rie.find('div.editor')).html('');
		        $(this).siblings('div.revision-inline-editor').find('div.editor').load($(this).attr('href'));
		        $(this).siblings('div.revision-inline-editor').slideDown();
	        }
	        return false;
	    });
	    
	    $('a.compare-button').click(function(){
	    	var rev1 = $('input[name=rev1]:checked');
	    	var rev2 = $('input[name=rev2]:checked');
	    	
	    	if (rev1.length > 0 && rev2.length > 0) {
	    		
	    		$.post($(this).attr('href'), {rev1: rev1.val(), rev2: rev2.val()}, function(res){
	    			$('div#compare-window').html(res).fadeIn();
	    		}, 'html');
	    	}
	    	
	        return false;
	    });
    }
	    
    var vertex = window.vertex = _vertex;
})();

$(function(){
    if ($('#flash').length > 0) {
        var content = $('#flash > div').html();
        var type = $('#flash > div').attr('class');
        $('#flash').remove();
        vertex.flashmsg(content, type);
    }
    
    if ($('#top').length > 0) {
	    $.get('/projects/mine_list', {}, function(res){
	        $.each(res.projects, function(i,v){
	            $('#project-selector').append('<option value="' + v.id + '">' + v.title + '</option>');
	        });
	    }, 'json');
	    
	    $('#project-selector').change(function(){
	        var val = $(this).children(':selected').val();
	        
	        if (val == 0) {
	            location.href = '/projects/add';
	        } else if (val > 0) {
	            location.href = '/editor/workspace/' + val;
	        }
	    });    
    }
});