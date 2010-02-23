// TODO - move "page" functions to vertex.pages[page_id] = ...

var vertex = {

    register: function(path) {
        var elements = path.split('.');
        var object = window;
        var element = null;

        for (var k in elements) {
            if (elements.hasOwnProperty(k)) {
                element = elements[k];
                if (object[element] === undefined) {
                    object[element] = {};
                }
                object = object[element];
            }
        }
    },

    get: function(path) {
        var elements = path.split('.'),
            object = window,
            element = null;
        for (var i in elements) {
            if (elements.hasOwnProperty(i)) {
                element = object[elements[i]];
                if (element === undefined) {
                    return null;
                }
                object = element;
            }
        }
        return object
    },

    msg : function(m,t) {vertex.messages.flash(m,t);},

    debug: false
};

(function($){

// Form handling
vertex.forms = {

    defaults: {
        clearForm: false,
        resetForm: false,
        disableSubmit: true,
        submitAltText: null,
        callback: null
    },

    init: function(options) {
        options = $.extend({}, vertex.forms.defaults, options);
        setTimeout(function() {
            var form = $('#' + options.id);
            if (form.length > 0) {
                form.ajaxForm({
                    'beforeSubmit': function(v, f, o) {
                        vertex.forms.ajaxform_presubmit(form, options);
                    },
                    'success': function(response, s) {
                        vertex.forms.handle_response(form, response, options);
                    },
                    'dataType': 'json',
                    'clearForm': false,
                    'resetForm': false,
                    'url': options.action,
                    'type': 'POST',
                    'target': null
                });
            } else {
                // try again in 0.1 seconds
                setTimeout(arguments.callee, 100);
            }
        }, 1);
    },

    ajaxform_presubmit: function(form, options) {
        form.find('.invalid').removeClass('invalid');
        form.find('.fielderror').remove();

        if (options.disableSubmit) {
            form.find('[type=submit]').attr('disabled', 'disabled');
        }
    },

    handle_response: function(form, response, options) {
        if (options.disableSubmit) {
            form.find('[type=submit]').removeAttr('disabled');
        }

        if (response._status != 'ok') {
            if (response.form_errors) {
                // TODO: better integration with all kinds of errors from TW
                $.each(response.form_errors, function(k,v){
                    form.find('[name="' + k + '"]').addClass('invalid');
                    form.find('[name="' + k + '"]').closest('td').append($('<span>').addClass('fielderror').html(v));
                });
            }
        } else {
            var redirect = true
            if (options.callback) {
                var fn = surimi.get(options.callback);
                if (fn !== null) {
                    // functionreference.call(thisArg, arg1, arg2, ...)
                    redirect = fn.call(form, options.id, response) !== false ? true : false;
                }
            }

            if (redirect && response._redirect) {
                location.href = response._redirect;
                return;
            } else {
                if (options.resetForm) {
                    form.resetForm();
                }
                if (options.clearForm) {
                    form.clearForm();
                }
            }
        }

        vertex.messages.flash(response._msg, response._status);
    }

};


// Utilities
vertex.util = {

    nocache: function() {return '?t=' + (new Date()).getTime();},

    center_on_screen: function(jq_obj) {
        jq_obj.css('top', $(window).height()/2 - jq_obj.height()/2);
        jq_obj.css('left', $(window).width()/2 - jq_obj.width()/2);
    }

};


// Messages
vertex.messages = {
    defaults: {
        speed: 'slow',
        animate: true,
        onClose: function(){}
    },

    // FIXME: stack of messages
    flash: function(msg, type, options) {
        type = type || 'ok';
        options = $.extend({}, vertex.messages.defaults, options);
        
        // Remove previous waiting messages
        $('div#flash div.waiting').closest('div#flash').remove();

        var $obj = $('<div>').attr('id', 'flash').html($('<div>').addClass(type).html(msg)).hide(),
            callback = options.onClose;

        options.onClose = function() {
            callback();
            $('#flash').remove();
        }

        $('body').prepend($obj);
        vertex.util.center_on_screen($obj);
        $('#flash').fadeIn(options.speed, function() {
            if (options.animate) {
                $('#flash').animate({'top': '0px'}, options.speed, 'linear', function(){
                    setTimeout(function(){
                        $('#flash').fadeOut(options.speed, options.onClose);
                    }, 3000);
                });
            } else {
                setTimeout(options.onClose, 2000);
            }
        });
    }
};

//Editor
vertex.editor = {};

vertex.editor.insert_latex = function(latex, offset) {
    var offset = !offset ? 0 : offset;
    var pos = vertex.editor.instance.cursorPosition();
    var line = pos.line == false ? vertex.editor.instance.nthLine(1) : pos.line;
    var char = pos.character;
    vertex.editor.instance.insertIntoLine(line, char, latex);
    vertex.editor.instance.selectLines(line, offset);    
};

vertex.editor.save = function(url) {
    if (!vertex.editor.instance) return;
    
    vertex.messages.flash('Saving...', 'waiting');
    
    $.post(url, {file_id: $('#editor-file-id').val(),
                 revid: $('#editor-file-last-revision').val(),
                 content: vertex.editor.instance.getCode()},
           function(res) {
                     vertex.messages.flash(res._msg, res._status);
    }, 'json');
};

vertex.editor.compile = function(url) {
    if (!vertex.editor.instance) return;
    
    vertex.messages.flash('Compiling...', 'waiting');
    $.post(url, {file_id: $('#editor-file-id').val(),
                 content: vertex.editor.instance.getCode()},
           function(res){
                     vertex.messages.flash(res._msg, res._status);
                     $('div#editor-misc-output div.output_content').html(res._msg);
                     
                     if (res._status == 'ok') {
                         $('div#editor-misc-output div.output_content').append('<ul>' + 
                                 '<li><a href="' + res.pdf_url + '">Download PDF file</a></li>' +
                                 '<li><a href="' + res.ps_url + '">Download PS file</a</li>' + 
                                 '<li><a href="' + res.dvi_url + '">Download DVI file</a</li>' +
                                 '</ul>');
                     }
                     
                     $('div#editor-misc-output div.log_content').html('<pre>' + res.latex_log + '</pre>');
                     $('div#editor-misc-output').fadeIn();
    }, 'json');
};

vertex.editor.delete_file = function(url) {
//  FIXME: do right (in -binary) also
    window.location.href = url + '/' + $('#editor-file-id').val();
};

vertex.editor.edit = {
        onLoad: function() {
            vertex.editor.instance = CodeMirror.fromTextArea('editor_area', {
                height: '80%',
                path: '/js/CodeMirror-0.65/js/',
                parserfile: '../contrib/latex/js/parselatex.js',
                stylesheet: '/js/CodeMirror-0.65/contrib/latex/css/latexcolors.css',
                lineNumbers: true,
                readOnly: $('#editor_area').attr('readonly') ? true : false,
                //textWrapping: false
            });
            
            $('a.symbols-button').vDropDownMenu('#editor-latex-symbols');
            
            $('#editor-latex-symbols').load($('a.symbols-button').attr('href'), {},
            function(){
                $('#editor-latex-symbols a').click(function(e){
                    e.preventDefault();
                    vertex.editor.insert_latex($(this).attr('title'));
                });
            });
            
            $('a.bold-button').click(function(e){
                e.preventDefault();
                vertex.editor.insert_latex('\\textbf{}', 8);
            });
            $('a.italic-button').click(function(e){
                e.preventDefault();
                vertex.editor.insert_latex('\\textit{}', 8);
            });
            $('a.underline-button').click(function(e){
                e.preventDefault();
                vertex.editor.insert_latex('\\underline{}', 11);
            });
            $('a.item-button').click(function(e){
                e.preventDefault();
                vertex.editor.insert_latex('\\begin{itemize}\n\t\\item \n\\end{itemize}', 23);
            });
            $('a.enum-button').click(function(e){
                e.preventDefault();
                vertex.editor.insert_latex('\\begin{enumerate}\n\t\\item \n\\end{enumerate}', 25);
            });
            
            $('a.save-button').click(function(e){
                e.preventDefault();
                vertex.editor.save($(this).attr('href'));
            });
            $('a.compile-button').click(function(e){
                e.preventDefault();
                vertex.editor.compile($(this).attr('href'));
            });
            $('a.delete-button').click(function(e){
                e.preventDefault();
                vertex.editor.delete_file($(this).attr('href'));
            });
            
            var $output = $('div#editor-misc-output');

            $output.find('a.output-link').click(function(e){
                e.preventDefault();
                $output.find('ul li').removeClass('active');
                $(this).parent('li').addClass('active');
                $output.find('div.log_content').hide();
                $output.find('div.output_content').show();
            });
            $output.find('a.log-link').click(function(e){
                e.preventDefault();
                $output.find('ul li').removeClass('active');
                $(this).parent('li').addClass('active');
                $output.find('div.output_content').hide();
                $output.find('div.log_content').show();
            });
            $output.find('li.close-link > a').click(function(e){
                e.preventDefault();
                $output.fadeOut();
            });
            
        }

};

vertex.revisions = {};
vertex.revisions.index = {
        onLoad: function() {
            $('#revisions-index .revisions-list ul li a').click(function(e){
                e.preventDefault();
                var rie = $(this).siblings('div.revision-inline-editor');

                if (rie.is(':visible')) {
                    rie.slideUp();
                } else {
                    $('div.revision-inline-editor').not(rie).slideUp();
                    $('div.editor').not(rie.find('div.editor')).html('');
                    $(this).siblings('div.revision-inline-editor').find('div.editor').load($(this).attr('href'), {}, function(){
                        vertex.editor.edit.onLoad();
                    });
                    $(this).siblings('div.revision-inline-editor').slideDown();
                }
            });
            
          $('a.compare-button').click(function(e){
              e.preventDefault();
              var rev1 = $('input[name=rev1]:checked');
              var rev2 = $('input[name=rev2]:checked');
              
              if (rev1.length > 0 && rev2.length > 0) {
                  $.post($(this).attr('href'), {rev1: rev1.val(), rev2: rev2.val()}, function(res){
                      $('div#compare-window').html(res).fadeIn();
                  }, 'html');
              }
        });            
            
        }
};

$(function() {
    var body = $('body');

    if (body.attr('id') === undefined) {return;}

    var elements = body.attr('id').split('-');
    var object = vertex;
    var path = 'vertex';

    //TODO: wrap in a function
    for (var k in elements) {
        if (elements.hasOwnProperty(k)) {
            path += '.' + elements[k];
            if (object[elements[k]] !== undefined) {
                object = object[elements[k]];
            } else {
                //console.error(path + ' is undefined!');
                object = null;
                break;
            }
        }
    }


    if (object !== null && object.onLoad) {
        object.onLoad.call(object);
    }
});

$(function(){
    if ($('#flash').length > 0) {
        var content = $('#flash > div').html();
        var type = $('#flash > div').attr('class');
        $('#flash').remove();
        vertex.messages.flash(content, type);
    }
    
    $('#menu a.projects-menu-link').vDropDownMenu('#menu div.projects-menu-list');
   
});

})(jQuery);