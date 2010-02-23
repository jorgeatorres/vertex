/*
    @author Jorge Torres <jtorresh@gmail.com>
*/
var LaTeXParser = Editor.Parser = (function() {
    
    function tokenizeLaTeX(source) {
        var ch = source.next();

        if (ch == '{' || ch == '}' || ch == '$' || ch == '[' || ch == ']') {
            return 'latex-delimiter';
        } else if (ch == '%') {
            while (!source.endOfLine()) source.next();
            return 'latex-comment';
        } else if (ch == '\\' && source.matches(/[a-zA-Z0-9]/)) {
            source.nextWhileMatches(/[a-zA-Z0-9]/);
            return 'latex-command';
        } else {
            // FIXME include spaces but not eols
            source.nextWhileMatches(/[\w\d\.]/); //        ^\s\u00a0>
            return 'latex';
        }
    }
  
    return {
        make: function(source) {
            source = tokenizer(source, tokenizeLaTeX);
        
            var iter = {
                next: function() {
                    var token = source.next();
                    
                    if(token.value == '\n')
                        token.indentation = function() { return 0; };

                    return token;
                },
            
                copy: function() {
                    return function(_source) {
                        source = tokenizer(_source, tokenizeLaTeX);
                        return iter;
                    };
                }
            };
            return iter;
        }
    };
})();
