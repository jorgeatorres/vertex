# coding: utf-8
import os, logging, transaction
from tg import config
from vertex.config.environment import load_environment

__all__ = ['setup_app']

log = logging.getLogger(__name__)

def setup_app(command, conf, vars):
    """Place any commands to setup vertex here"""
    load_environment(conf.global_conf, conf.local_conf)
    # Load the models
    from vertex import model
    from vertex.lib import latexutils
    from vertex.tests import fixtures
    
    print "Creating tables"
    model.metadata.create_all(bind=config['pylons.app_globals'].sa_engine)

    unal = model.User(email_address = u'nobody@unal.edu.co',
                      password = u'unal123456',
                      name = u'Test User',
                      institution = u'Universidad Nacional de Colombia')    

    model.DBSession.add(unal)

    group = model.Group()
    group.group_name = u'active_users'
    group.display_name = u'Users Group'
    
    group.users.append(unal)
    model.DBSession.add(group)
    
    project = model.core.Project(title=u'Douze Grandes Études Op. 10',
                                       creator=unal)
    project.members.append(model.core.ProjectMembership(user=unal))
    
    # LaTeX code fixtures
    for root, dirs, files in os.walk(os.path.join(os.path.dirname(__file__),
                                                     'tests', 'latex')):
        for file in files:
            _file = open(os.path.join(root, file))
            
            file_obj = model.core.File(filename=file)
            project.files.append(file_obj)
            
            file_obj.revisions.append(model.core.FileRevision(content=_file.read(), user=unal))

            _file.close()

    model.DBSession.add(project)
    
    # LaTeX symbols
    for groupname, symbols in fixtures.latex_symbols.iteritems():
        cat = model.core.LaTeXSymbolGroup(name=groupname)
        
        for symbol in symbols:
            symbol_thumb = latexutils.formula_to_png(symbol, 150)
            
            cat.symbols.append(model.core.LaTeXSymbol(command=symbol,
                                                       thumbnail=symbol_thumb,
                                                       name=symbol))
        
        model.DBSession.add(cat)


    model.DBSession.flush()
    transaction.commit()
    print "Successfully setup"