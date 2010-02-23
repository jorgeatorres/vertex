# coding: utf-8
from vertex.controllers.template import TemplateController
import os
from tg import expose, validate, flash, require, url, request, response, redirect, tmpl_context, config
from tg.controllers import CUSTOM_CONTENT_TYPE
from pylons.i18n import ugettext as _, lazy_ugettext as l_
from repoze.what import predicates

from vertex.lib.base import BaseController, ajax_form_error_handler
from vertex.model import DBSession, metadata
from vertex.model import Project, File, FileRevision, LaTeXSymbolGroup, LaTeXSymbol
from vertex.model import LaTeXCompileRun, ProjectMembership, User
from vertex.controllers.editor import EditorController
from vertex.controllers.error import ErrorController
from vertex.widgets.forms import *


__all__ = ['RootController']


class ProjectsController(object):
    
    @require(predicates.not_anonymous())    
    @expose('vertex.templates.projects.add')
    def add(self):
        tmpl_context.add_project_form = add_project_form
        return dict()

    @require(predicates.not_anonymous())
    @expose('json')
    @validate(add_project_form, error_handler=ajax_form_error_handler)
    def add_do(self, title, **kw):
        project = Project(title=title, description=kw.get('description', u''),
                          creator=request.identity['user'])
        project.members.append(ProjectMembership(user=request.identity['user']))
        DBSession.add(project)
        DBSession.flush()
        
        flash(_('Project "%s" has been created' % title))
        return dict(_status=u'ok',
                    _redirect=url('/projects/view/%d' % project.id))
    
    @require(predicates.not_anonymous())        
    @expose('json')
    @validate(invite_people_form, error_handler=ajax_form_error_handler)
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
    def settings(self, id):
        project = DBSession.query(Project).filter_by(id=id).one()
        tmpl_context.invite_people_form = invite_people_form
        return dict(project=project)
    
    @require(predicates.not_anonymous())
    @expose('vertex.templates.projects.overview')
    def view(self, project_id):
        return self.settings(project_id)


class FilesController(object):
    
    @require(predicates.not_anonymous())
    @expose('json')
    @validate(add_blank_file_form, error_handler=ajax_form_error_handler)    
    def new(self, **kw):
        project = DBSession.query(Project).filter_by(id=kw['project_id']).one()
        file = File(project=project, filename='%s.latex' % kw['filename'])
        DBSession.add(FileRevision(file=file,
                                   user=request.identity['user']))
        DBSession.flush()
        flash(_('The file "%s.latex" has been added to the project.' % kw['filename']))
        
        return dict(_status=u'ok', _redirect=url('/editor/edit/%s' % file.id))

    @require(predicates.not_anonymous())
    @expose()
    @validate(import_file_form, error_handler=ajax_form_error_handler)
    def upload(self, **kw):
        project = DBSession.query(Project).filter_by(id=kw['project_id']).one()

        content_type = kw['file'].type
        
        # XXX: We assume files ending in .latex or .tex are LaTeX files
        if kw['file'].filename.lower().endswith('.tex') or \
           kw['file'].filename.lower().endswith('.latex'):
            content_type = u'text/x-latex'
                    
        rev = FileRevision(file=File(project=project, filename=kw['file'].filename,
                                     content_type=content_type),
                           user=request.identity['user'])
        
        if rev.file.content_type in (config.get('vertex_text_types') + config.get('vertex_latex_types')):
            rev.content = kw['file'].value
        else:
            rev.content_binary = kw['file'].value
    
        DBSession.add(rev)
        DBSession.flush()

        flash(_('The file "%s" has been added to the project.' % (kw['file'].filename)))
        redirect(url('/editor/edit/%s' % rev.file.id))
        
    @require(predicates.not_anonymous())
    @expose()
    @validate(update_file_form, error_handler=ajax_form_error_handler)
    def upload_update(self, **kw):
        file = DBSession.query(File).filter_by(id=kw['file_id']).one()
        
        if file.content_type != kw['file'].type:
            raise Exception(_('File content-type is invalid!')) # TODO: do this in validation!
        
        file.revisions.append(FileRevision(content_binary=kw['file'].value,
                                           user=request.identity['user']))
        
        flash(_('"%s" has been updated to a new revision.' % file.filename))
        redirect(url('/editor/edit/%s' % file.id))
        
    @require(predicates.not_anonymous())
    @expose('json')
    def save(self, file_id, revid, content):
        file = DBSession.query(File).filter_by(id=file_id).one()
        last_rev = file.last_revision
        
        _msg = _('The file has been saved.')
        _status = u'ok'
        
        if last_rev.id != int(revid):
            _msg = _('The file has been saved. Changes that you might want to check were detected between this revision and the previous one.')
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
        flash(_('The file "%s" has been deleted from the project.' % file.filename))
        redirect(url('/projects/view/%d' % file.project.id))


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
        flash(_('Welcome back %s!') % request.identity['user'].name)
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
        return dict(_msg=_('Profile updated.'), _status=u'ok')
