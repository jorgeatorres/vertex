# -*- coding: utf-8 -*-
import logging, os, subprocess

log = logging.getLogger(__name__)

LATEX_COMMAND = 'latex -interaction=batchmode -outputformat=dvi'
ALLOWED_FORMATS = ['pdf', 'dvi', 'ps', 'png']

def compile(file_, dir):
    fname_noext = os.path.splitext(file_)[0]
    
    log.debug('Compiling %s' % os.path.join(dir, file_))

    cmd = subprocess.Popen(LATEX_COMMAND + ' ' + file_, shell=True, stdin=subprocess.PIPE,
                           stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                           close_fds=True, cwd=dir)
    cmd_stdout = cmd.stdout
    cmd.wait()
    log.debug('LaTeX exited with status %d' % cmd.returncode)
    
    log_file = open(os.path.join(dir, fname_noext + '.log'))
    log_ = log_file.read()
    log_file.close()

    res = None
    
    if cmd.returncode == 0:
        res_file = open(os.path.join(dir, fname_noext + '.dvi'), mode='rb')
        res = res_file.read()
        res_file.close()
    
    return (cmd.returncode == 0, res, log_)

def compile_latex(latex, filename=None):
    import tempfile, shutil
    
    compiledir = tempfile.mkdtemp()
    
    if filename is None:
        (fd, filename) = tempfile.mkstemp(dir=compiledir)
        filename = os.path.basename(filename)
    
    texfname = os.path.join(compiledir, filename)
    texfile = open(texfname, 'w')
    texfile.write(latex)
    texfile.close()

    (success, res, log_) = compile(os.path.basename(texfname), compiledir)

    shutil.rmtree(compiledir)
    
    return (success, res, log_)

def convert_dvi(dvi, format='pdf'):
    format = format.lower()
    if format not in ALLOWED_FORMATS:
        raise Exception('Invalid format for conversion: %s' % format)

    if format == 'dvi':
        return dvi
    else:
        cmdname = 'dvi%s' % format
        
        import tempfile, shutil
        
        convdir = tempfile.mkdtemp()
        tempfd, tempfilename = tempfile.mkstemp(dir=convdir)
        tempfile_ = os.fdopen(tempfd, 'w+b')
        tempfile_.write(dvi)
        tempfile_.flush()

        if format == 'png':
            cmdname = cmdname + ' -T tight -D 150 -o %s.png' % tempfilename        
        
        log.debug('Executing %s' % cmdname)
        cmd = subprocess.Popen(cmdname + ' ' + tempfilename, shell=True, stdin=subprocess.PIPE,
                               stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                               close_fds=True, cwd=convdir)
        cmd.wait()
        
        if cmd.returncode != 0:
            raise Exception('Conversion failed!')

        resfile = open(os.path.join(convdir, tempfilename + ('.%s' % format)))
        res = resfile.read()
        resfile.close()

        # Cleanup
        tempfile_.close()
        shutil.rmtree(convdir)
        
        return res
    
# Generalizar a latex_to_png y formula_to_png simplemente esta en un env displaymath
# resolution es en DPI (TODO - implementar!)
def formula_to_png(formula, resolution=250):
    template = r'''\documentclass[fleqn]{article}
\usepackage{amssymb,amsmath}
\usepackage[latin1]{inputenc}
\begin{document}
\thispagestyle{empty} \mathindent0cm \parindent0cm
\begin{displaymath} 
%(eqn)s
\end{displaymath}
\end{document}
'''
    latex = template % {'eqn': formula}
    (success, dvi, log_) = compile_latex(latex)
    
    if not success:
        raise Exception('no se pudo compilar latex %s' % formula)
    
    return convert_dvi(dvi, 'png')    
    
def simplify_log(entire_log):
	S1 = 1;		#Buscando el caracter: !
	S2 = 2;		#Buscando el texto de error.
	STATE = S1;
	
	#Lista de diccionarios donde cada diccionario es un error del proceso de compilacion de latex
	simplified_log = ();
	#Diccionario que representa cada error
	error = {}
	#Variable para almacenar el mensaje asociado a cada error
	error_message = "";
	#Almacena como una cadena de texto el numero de linea donde se produjo el error
	linenumber = "";
		
	#Dividimos el log en lineas para poder analizarlo facilmente
	for line in entire_log.split('\n'):
				
		#si una linea comienza con !, se anuncia que se va a describir el error
		if  line.startswith("!") :			
			STATE = S2;			
		#si comienza con l., se anuncia la linea en la que se encuentra el error
		elif  line.startswith("l.") :
		
			for c in line[2:len(line)] :
				if c.isdigit() :
					linenumber += c;
				else :
					error_message += c;
					
			#Guardamos el error en el "simplified_log"
			error = { "type" : "Error", "message" : error_message, "line_number" : int(linenumber)} 
			simplified_log = simplified_log + (error,);
			
			#limpiamos la variables
			error = {}
			error_message = "";
			linenumber = "";
			STATE = S1;
			
		if ( STATE == S2 ) :
			error_message += line;					
		
	return simplified_log

