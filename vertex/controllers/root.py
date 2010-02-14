# -*- coding: utf-8 -*-
import os
from tg import expose, validate, flash, require, url, request, response, redirect, tmpl_context
from tg.controllers import CUSTOM_CONTENT_TYPE
from pylons.i18n import ugettext as _, lazy_ugettext as l_
from repoze.what import predicates

from vertex.lib.base import BaseController
from vertex.model import DBSession, metadata
from vertex.model import Project, File, FileRevision, LaTeXSymbolGroup, LaTeXSymbol
from vertex.model import LaTeXCompileRun, ProjectMembership, User
from vertex.controllers.editor import EditorController
from vertex.controllers.error import ErrorController
from vertex.widgets.forms import *

__all__ = ['RootController']

# TODO: Cambiar las URLS a algo asi:
# projects/index ...
# projects/1 == projects/view/1
# projects/1/files/index == files/index para project 1
# projects/1/files/new, etc.
# projects/1/files/2/history ...

@expose('json')
def ajax_error_handler(self, **kw):
    res = dict(_msg='No se pudo enviar el formulario pues contiene errrores.', _status=u'error')
    
    if tmpl_context.form_errors:
        res['form_errors'] = tmpl_context.form_errors
        res['form_values'] = tmpl_context.form_values
    
    return res

class ProjectsController(object):
    
    @require(predicates.not_anonymous())    
    @expose('vertex.templates.projects.add')
    def add(self):
        tmpl_context.add_project_form = add_project_form
        return dict()

    @require(predicates.not_anonymous())
    @expose('json')
    @validate(add_project_form, error_handler=ajax_error_handler)
    def add_do(self, title, **kw):
        project = Project(title=title, description=kw.get('description', u''),
                          creator=request.identity['user'])
        project.members.append(ProjectMembership(user=request.identity['user']))
        DBSession.add(project)
        DBSession.flush()
        
        flash(u'El proyecto "%s" ha sido creado' % title)
        
        return dict(_status=u'ok',
                    _redirect=url('/editor/workspace/%s' % project.id))
    
    @require(predicates.not_anonymous())    
    @expose()
    def delete(self, project_id):
        project = DBSession.query(Project).filter_by(id=project_id).one()
        DBSession.delete(project)
        flash(u'El proyecto "%s" fue eliminado' % project.title)
        redirect(url('/'))
        
    @require(predicates.not_anonymous())        
    @expose('json')
    @validate(invite_people_form, error_handler=ajax_error_handler)
    def members_add(self, **kw):
        project = DBSession.query(Project).filter_by(id=kw['project_id']).one()
        emails = kw['emails'].lower().split(',')
        
        if emails:
            for email in emails:
                user = DBSession.query(User).filter_by(email_address=email).one()
                project.members.append(ProjectMembership(user=user))
        
        flash(u'Los usuarios han sido invitados al proyecto')
        return dict(_status='ok',
                    _redirect=url('/editor/workspace/%s#project_settings' % project.id))
        
    @require(predicates.not_anonymous())        
    @expose('json')
    def members_delete(self, project_id, user_id):
        membership = DBSession.query(ProjectMembership).filter_by(project_id=project_id,
                                                                  user_id=user_id).one()
        DBSession.delete(membership)
        return dict(_status=u'ok',
                    _msg=u'El usuario "%s" ha sido removido del proyecto' % membership.user.name)
    
    @require(predicates.not_anonymous())    
    @expose('json')
    def mine_list(self):
        projects = DBSession.query(Project).filter(Project.members.any(ProjectMembership.user == request.identity['user'])).all()
        return dict(projects=projects)
    
    @require(predicates.not_anonymous())    
    @expose('vertex.templates.projects.overview')
    def overview(self, id):
        project = DBSession.query(Project).filter_by(id=id).one()
        tmpl_context.invite_people_form = invite_people_form
        return dict(project=project)

class FilesController(object):
    
    @require(predicates.not_anonymous())
    @expose('json')
    @validate(add_blank_file_form, error_handler=ajax_error_handler)    
    def new(self, **kw):
        project = DBSession.query(Project).filter_by(id=kw['project_id']).one()
        DBSession.add(FileRevision(file=File(project=project,
                                             filename=kw['filename']),
                                   user=request.identity['user']))
        flash(u'El archivo %s ha sido agregado al proyecto' % kw['filename'])
        
        return dict(_status=u'ok', _redirect=url('/editor/workspace/%s' % project.id))

    @require(predicates.not_anonymous())
    @expose()
    @validate(import_file_form, error_handler=ajax_error_handler)
    def upload(self, **kw):
        project = DBSession.query(Project).filter_by(id=kw['project_id']).one()
        
        rev = FileRevision(file=File(project=project, filename=kw['file'].filename,
                                     content_type=kw['file'].type),
                           user=request.identity['user'])
        
        if rev.file.content_type in ('text/x-tex', 'text/plain'):
            rev.content = kw['file'].value
        else:
            rev.content_binary = kw['file'].value
    
        DBSession.add(rev)

        flash(u'El archivo "%s" ha sido agregado al proyecto' % (kw['file'].filename))
        redirect(url('/editor/workspace/%s#f_%s' % (project.id, kw['file'].filename)))
        
    @require(predicates.not_anonymous())
    @expose()
    @validate(update_file_form, error_handler=ajax_error_handler)
    def upload_update(self, **kw):
        file = DBSession.query(File).filter_by(id=kw['file_id']).one()
        
        if file.content_type != kw['file'].type:
            raise Exception('el tipo de la nueva versión del archivo no coincide con el original!') # TODO: hacer esto en la validacion
        
        file.revisions.append(FileRevision(content_binary=kw['file'].value,
                                           user=request.identity['user']))
        
        flash(u'La nueva revisión de "%s" ha sido agregada al proyecto' % file.filename)
        redirect(url('/editor/workspace/%s#f_%s' % (file.project.id, file.filename)))
        
    @require(predicates.not_anonymous())
    @expose('json')
    def save(self, file_id, revid, content):
        file = DBSession.query(File).filter_by(id=file_id).one()
        last_rev = file.last_revision
        
        _msg = u'El archivo ha sido guardado'
        _status = u'ok'
        
        if last_rev.id != int(revid):
            _msg = u'El archivo guardado. Hay cambios entre esta versión y la anterior que debería revisar'
            _status = u'warning'
            
        file.revisions.append(FileRevision(content=content,
                                           user=request.identity['user']))

        return dict(_msg=_msg, _status=_status, file_id=file.id)    

    @require(predicates.not_anonymous())
    @expose('vertex.templates.files.revisions-index')
    def revisions(self, fid):
        file = DBSession.query(File).filter_by(id=fid).one()
        revisions = DBSession.query(FileRevision).filter_by(file_id=fid).order_by('-id')
        return dict(file=file, revisions=revisions)

    @require(predicates.not_anonymous())
    @expose()
    def revision_content(self, rid, download=False):
        rev = DBSession.query(FileRevision).filter_by(id=rid).one()
        
        response.content_type = rev.file.content_type
        
        if download:
            response.headers.add('Content-Disposition:', 'attachment; filename=%s' % rev.file.filename)
        else:
            response.headers.add('Content-Disposition:', 'inline; filename=%s' % rev.file.filename)
        
        if rev.file.is_binary:
            return rev.content_binary
        else:
            return rev.content 

    @require(predicates.not_anonymous())
    @expose(content_type=CUSTOM_CONTENT_TYPE)
    def download(self, run_id, format=u'pdf'):
        run = DBSession.query(LaTeXCompileRun).filter_by(id=run_id).one()

        filename = '%s.%s' % (os.path.splitext(run.file.filename)[0], format)
        download = getattr(run, '%s_output' % format)

        response.content_type = 'application/%s' % format
        response.headers.add('Content-Disposition:', 'attachment; filename=%s' % filename)
        
        return download
    
    @require(predicates.not_anonymous())
    @expose()
    def delete(self, file_id):
        file = DBSession.query(File).filter_by(id=file_id).one()
        DBSession.delete(file)
        flash(u'El archivo "%s" ha sido eliminado del proyecto' % file.filename)
        redirect(url('/editor/workspace/%s' % file.project.id))


class RootController(BaseController):

    editor = EditorController()
    error = ErrorController()
    projects = ProjectsController()
    files = FilesController()

    @require(predicates.not_anonymous())
    @expose('vertex.templates.index')
    def index(self):
        projects = DBSession.query(Project).filter(Project.members.any(ProjectMembership.user == request.identity['user'])).all()
        return dict(projects=projects)

    @expose('vertex.templates.login')
    def login(self, came_from=url('/')):
        login_counter = request.environ['repoze.who.logins']
        if login_counter > 0:
            flash(_('Wrong credentials'), 'warning')
        return dict(login_counter=str(login_counter),
                    came_from=came_from)
    
    @expose()
    def post_login(self, came_from=url('/')):
        if not request.identity:
            login_counter = request.environ['repoze.who.logins'] + 1
            redirect(url('/login', came_from=came_from, __logins=login_counter))
        userid = request.identity['repoze.who.userid']
        flash(_('Bienvenido de nuevo %s!') % request.identity['user'].name)
        redirect(came_from)

    @expose()
    def post_logout(self, came_from=url('/')):
        redirect('/')
        
    @require(predicates.not_anonymous())
    @expose('vertex.templates.profile-edit')
    def profile_edit(self):
        tmpl_context.profile_edit_form = profile_edit_form
        return dict(user=request.identity['user'])
    
    @require(predicates.not_anonymous())
    @expose('json')
    def profile_edit_do(self, **kw):
        return dict(_msg=u'Perfil actualizado', _status=u'ok')