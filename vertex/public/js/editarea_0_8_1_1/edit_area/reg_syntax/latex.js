editAreaLoader.load_syntax["latex"] = {
	'COMMENT_SINGLE' : {1 : '%'}
	,'COMMENT_MULTI' : {}

	//,'QUOTEMARKS' : ['"', "'"]
	,'KEYWORD_CASE_SENSITIVE' : true
	,'KEYWORDS' : {
		'attributes' : [
			'addlinespace','address','appendix','author','backmatter',
	            'bfseries','bibitem','bigskip','blindtext','caption','captionabove',
        	    'captionbelow','cdot','centering','cite','color','colorbox','date',
        	    'def','definecolor','documentclass','edef','eqref','else','email','emph','fbox',
        	    'fi','flushleft','flushright','footnote','frac','frontmatter','graphicspath','hfill',
        	    'hline','hspace','huge','include','includegraphics','infty','input','int','ifx',
        	    'item','label','LaTeX','left','let','limits','listfiles','listoffigures',
        	    'listoftables','mainmatter','makeatletter','makeatother','makebox',
        	    'makeindex','maketitle','mbox','mediumskip','newcommand',
        	    'newenvironment','newpage','nocite','nonumber','pagestyle','par','paragraph','parbox',
        	    'parident','parskip','partial','raggedleft','raggedright','raisebox','ref',
        	    'renewcommand','renewenvironment','right','rule','section','setlength',
        	    'sffamily','subparagraph','subsection','subsubsection','sum','table',
        	    'tableofcontents','textbf','textcolor','textit','textnormal',
        	    'textsuperscript','texttt','title','today','ttfamily','urlstyle',
        	    'usepackage','vspace'
		]

		,'values' : [
			'above', 'absolute', 'always', 'armenian', 'aural', 'auto', 'avoid',
			'baseline', 'behind', 'below', 'bidi-override', 'black', 'blue', 'blink', 'block', 'bold', 'bolder', 'both',
			'capitalize', 'center-left', 'center-right', 'center', 'circle', 'cjk-ideographic', 
            'close-quote', 'collapse', 'condensed', 'continuous', 'crop', 'crosshair', 'cross', 'cursive',
			'dashed', 'decimal-leading-zero', 'decimal', 'default', 'digits', 'disc', 'dotted', 'double',
			'e-resize', 'embed', 'extra-condensed', 'extra-expanded', 'expanded',
			'fantasy', 'far-left', 'far-right', 'faster', 'fast', 'fixed', 'fuchsia',
			'georgian', 'gray', 'green', 'groove', 'hebrew', 'help', 'hidden', 'hide', 'higher',
			'high', 'hiragana-iroha', 'hiragana', 'icon', 'inherit', 'inline-table', 'inline',
			'inset', 'inside', 'invert', 'italic', 'justify', 'katakana-iroha', 'katakana',
			'landscape', 'larger', 'large', 'left-side', 'leftwards', 'level', 'lighter', 'lime', 'line-through', 'list-item', 'loud', 'lower-alpha', 'lower-greek', 'lower-roman', 'lowercase', 'ltr', 'lower', 'low',
			'maroon', 'medium', 'message-box', 'middle', 'mix', 'monospace',
			'n-resize', 'narrower', 'navy', 'ne-resize', 'no-close-quote', 'no-open-quote', 'no-repeat', 'none', 'normal', 'nowrap', 'nw-resize',
			'oblique', 'olive', 'once', 'open-quote', 'outset', 'outside', 'overline',
			'pointer', 'portrait', 'purple', 'px',
			'red', 'relative', 'repeat-x', 'repeat-y', 'repeat', 'rgb', 'ridge', 'right-side', 'rightwards',
			's-resize', 'sans-serif', 'scroll', 'se-resize', 'semi-condensed', 'semi-expanded', 'separate', 'serif', 'show', 'silent', 'silver', 'slow', 'slower', 'small-caps', 'small-caption', 'smaller', 'soft', 'solid', 'spell-out', 'square',
			'static', 'status-bar', 'super', 'sw-resize',
			'table-caption', 'table-cell', 'table-column', 'table-column-group', 'table-footer-group', 'table-header-group', 'table-row', 'table-row-group', 'teal', 'text', 'text-bottom', 'text-top', 'thick', 'thin', 'transparent',
			'ultra-condensed', 'ultra-expanded', 'underline', 'upper-alpha', 'upper-latin', 'upper-roman', 'uppercase', 'url',
			'visible',
			'w-resize', 'wait', 'white', 'wider',
			'x-fast', 'x-high', 'x-large', 'x-loud', 'x-low', 'x-small', 'x-soft', 'xx-large', 'xx-small',
			'yellow', 'yes'
		]
		,'specials' : [
			'important'
		]
	}
	,'OPERATORS' :[
		':', ';', '!', '.', '#'
	]
	,'DELIMITERS' :[
		'{', '}','$'
	]
	,'REGEXPS' : {			// advance syntax highlight through regexp
		'latexcommand' : {		// the name 'doctype' can be changed with no problem.
			'search' : '()(\\\\[a-zA-Z]+[a-zA-Z0-9]*)()'	// the regexp			
			,'class' : 'cmd'			// the css class
			,'modifiers' : 'g'			// the modifier ("g" and/or "i")
			,'execute' : 'before'			// "before" or "after". Determine if the regexp must 
								// be done before or after the main highlight process
		}
		,'math_enviroment' : {		// the name 'doctype' can be changed with no problem.
			'search' : '([$])([^$]*)([$])'	// the regexp			
			,'class' : 'math'			// the css class
			,'modifiers' : 'g'			// the modifier ("g" and/or "i")
			,'execute' : 'before'			// "before" or "after". Determine if the regexp must 
								// be done before or after the main highlight process
		}
	}

	,'STYLES' : {
		'COMMENTS': 'color: #AAAAAA;'
		,'QUOTESMARKS': 'color: #6381F8;'
		,'KEYWORDS' : {
			'attributes' : 'color: #48BDDF;'
			,'values' : 'color: #2B60FF;'
			,'specials' : 'color: #FF0000;'
			}
		,'OPERATORS' : 'color: #FF00FF;'
		,'DELIMITERS' : 'color: #0060CA;'
		,'REGEXP'	: {
			'cmd' : 'color: #964848;'
			,'math' : 'color: #60CA00;'
		}
				
	}
};
