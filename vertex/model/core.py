# -*- coding: utf-8 -*-
from datetime import datetime
from sqlalchemy import ForeignKey, Column
from sqlalchemy.orm import relation, backref, synonym
from sqlalchemy.types import Integer, Unicode, UnicodeText, DateTime, Boolean, \
                             Binary
from vertex.model import DBSession, DeclarativeBase
from vertex.model.auth import User


class Project(DeclarativeBase):
    __tablename__ = 'projects'

    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(Unicode(255), unique=True, nullable=False)
    description = Column(UnicodeText, nullable=True, default=None)
    creator_id = Column(Integer, ForeignKey(User.user_id), nullable=False)

    created_on = Column(DateTime, default=datetime.now, nullable=False)
    updated_on = Column(DateTime, default=datetime.now, onupdate=datetime.now, nullable=False)
    
    creator = relation(User)


class ProjectMembership(DeclarativeBase):
    __tablename__ = 'memberships'
    
    project_id = Column(Integer, ForeignKey('projects.id'), primary_key=True)
    user_id = Column(Integer, ForeignKey('users.user_id'), primary_key=True)

    created_on = Column(DateTime, default=datetime.now, nullable=False)
    updated_on = Column(DateTime, default=datetime.now, onupdate=datetime.now, nullable=False)
    
    project = relation(Project, backref=backref('members', cascade='all, delete-orphan'))
    user = relation(User)


class File(DeclarativeBase):
    __tablename__ = 'files'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    project_id = Column(Integer, ForeignKey('projects.id'), nullable=False)
    filename = Column(Unicode(255), nullable=False)
    content_type = Column(Unicode(255), nullable=False, default=u'text/x-tex')
    
    created_on = Column(DateTime, default=datetime.now, nullable=False)
    updated_on = Column(DateTime, default=datetime.now, onupdate=datetime.now, nullable=False)    
    
    project = relation(Project, backref='files')
    
    @property
    def is_binary(self):
        return self.content_type not in ('text/plain', 'text/x-tex', 'application/x-tex')
    
    @property
    def last_revision(self):
        return DBSession.query(FileRevision).filter_by(file_id=self.id).order_by('-id')[0:1][0]


class FileRevision(DeclarativeBase):
    __tablename__ = 'file_revisions'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    file_id = Column(Integer, ForeignKey('files.id'), nullable=False)
    user_id = Column(Integer, ForeignKey('users.user_id'), nullable=False)
    autosave = Column(Boolean, nullable=False, default=False)
    content = Column(UnicodeText, nullable=False, default=u'')
    content_binary = Column(Binary, nullable=True, default=None)

    created_on = Column(DateTime, default=datetime.now, nullable=False)
    
    file = relation(File, backref=backref('revisions', cascade='all, delete-orphan'))
    user = relation(User)


class LaTeXCompileRun(DeclarativeBase):
    __tablename__ = 'latex_compilations'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    file_id = Column(Integer, ForeignKey('files.id'), nullable=False)
    content = Column(UnicodeText, nullable=False, default=u'')

    dvi_output = Column(Binary, nullable=True)
    pdf_output = Column(Binary, nullable=False)
    ps_output = Column(Binary, nullable=True)
    latex_log = Column(UnicodeText, nullable=False, default=u'')
    
    created_on = Column(DateTime, default=datetime.now, nullable=False)
    
    file = relation(File, uselist=False)
    
    def compile(self):
        from vertex.lib import latexutils
        import tempfile, os, shutil
        
        compiledir = tempfile.mkdtemp()
        texfname = os.path.join(compiledir, self.file.filename)
        texfile = open(texfname, 'w')
        texfile.write(self.content)
        texfile.close()
        
        # Perform compilation
        (res, dvi, log) = latexutils.compile(self.file.filename, compiledir)
        errors = latexutils.simplify_log(log)
        
        self.latex_log = log
                        
        if res:
            self.dvi_output = dvi
            self.pdf_output = latexutils.convert_dvi(dvi, 'pdf')
            self.ps_output = latexutils.convert_dvi(dvi, 'ps')
        
        # Cleanup
        shutil.rmtree(compiledir)
        
        return res


# LaTeX Symbols

class LaTeXSymbolGroup(DeclarativeBase):
    __tablename__ = 'symbol_groups'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(Unicode(100), nullable=False, unique=True)
    
    created_on = Column(DateTime, default=datetime.now, nullable=False)
    updated_on = Column(DateTime, default=datetime.now, onupdate=datetime.now, nullable=False)    

    
class LaTeXSymbol(DeclarativeBase):
    __tablename__ = 'symbols'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    group_id = Column(Integer, ForeignKey(LaTeXSymbolGroup.id), nullable=False)
    command = Column(UnicodeText, nullable=False)
    name = Column(Unicode(100), nullable=False)
    thumbnail = Column(Binary, nullable=False)
    
    created_on = Column(DateTime, default=datetime.now, nullable=False)
    updated_on = Column(DateTime, default=datetime.now, onupdate=datetime.now, nullable=False)
    
    group = relation('LaTeXSymbolGroup', backref='symbols')
