# -*- coding: utf-8 -*-
from tg import expose, url, response, flash, tmpl_context
from tg.controllers import CUSTOM_CONTENT_TYPE
from vertex.model import DBSession, Project, File, LaTeXCompileRun, \
                             LaTeXSymbolGroup, LaTeXSymbol
from vertex.widgets.forms import add_blank_file_form, import_file_form, \
                                     update_file_form
from vertex.model.core import FileRevision

class EditorController(object):

    @expose('vertex.templates.editor.new')
    def new(self, pid):
        project = DBSession.query(Project).filter_by(id=pid).one()
        tmpl_context.add_blank_file_form = add_blank_file_form
        tmpl_context.import_file_form = import_file_form
        return dict(project=project)

    @expose('vertex.templates.editor.workspace')
    def workspace(self, pid):
        project = DBSession.query(Project).filter_by(id=pid).one()
        return dict(project=project)
        
    @expose('vertex.templates.editor.project-sidebar')
    def project_sidebar(self, pid):
        project = DBSession.query(Project).filter_by(id=pid).one()
        return dict(project=project)
        
    @expose('vertex.templates.editor.edit')
    def edit(self, id):
        file = DBSession.query(File).filter_by(id=id).one()
        return dict(file=file)
    
    @expose('vertex.templates.editor.editor')
    def editor(self, id, revid=None):
        file = DBSession.query(File).filter_by(id=id).one()
        revision = None
        
        if revid is not None:
            revision = DBSession.query(FileRevision).filter_by(id=revid, file_id=id).one()
        
        if file.is_binary:
            tmpl_context.update_file_form = update_file_form
        
        return dict(file=file, revision=revision)

    @expose('vertex.templates.editor.compare')
    def compare(self, rev1, rev2):
        rev1 = DBSession.query(FileRevision).filter_by(id=rev1).one()
        rev2 = DBSession.query(FileRevision).filter_by(id=rev2).one()
        return dict(rev1=rev1, rev2=rev2)
    
    @expose('vertex.templates.editor.latex-symbols')
    def latex_symbols(self):
        res = dict()
        groups = DBSession.query(LaTeXSymbolGroup)
        
        for group in groups:
            symbols_ = []
            
            for symbol in group.symbols:
                symbols_.append(dict(id=symbol.id,
                                     name=symbol.name,
                                     command=symbol.command))
            res[group.name] = symbols_
        
        return dict(symbols=res)
    
    @expose(content_type=CUSTOM_CONTENT_TYPE)
    def latex_symbols_thumb(self, id):
        symbol = DBSession.query(LaTeXSymbol).filter_by(id=id).one()
        response.content_type = 'image/png'
        return symbol.thumbnail
    
    @expose('json')
    def compile(self, file_id, content):
        file = DBSession.query(File).filter_by(id=file_id).one()
        run = LaTeXCompileRun(file=file, content=content)
        
        if run.compile():
            DBSession.add(run)
            DBSession.flush()
            return dict(_msg=u'El archivo fue compilado exitosamente.',
                        _status=u'ok',
                        run_id=run.id,
                        pdf_url=url('/files/download/%s' % run.id),
                        ps_url=url('/files/download/%s/ps' % run.id),
                        dvi_url=url('/files/download/%s/dvi' % run.id),                        
                        latex_log=run.latex_log)
        else:
            return dict(_msg=u'El archivo no pudo ser compilado por errores en el código. Revise el log para obtener más detalles.', _status='error',
                        latex_log=run.latex_log)