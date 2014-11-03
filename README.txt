About verTeX
======================
- Author: Jorge A. Torres <j at jorgetorres.co>
- URL: http://0xfee1dead.org/vertex
- Source Code: http://github.com/jorgeatorres/vertex

verTeX is an online collaborative LaTeX editor featuring version control, syntax highlighting, management of projects and users and a lot more while still keeping it simple.


Requirements (server)
======================

- Turbogears2 environment (including ToscaWidgets, SQLAlchemy).
- A LaTeX environment.


Installation and Setup (Standard TG2 cruft)
===========================================

1) Edit the configuration files to suit your environment (development.ini).

2) Create the project database for any model classes defined:

    $ paster setup-app development.ini

3) Start the paste http server::

    $ paster serve development.ini

While developing you may want the server to reload after changes in package files (or its dependencies) are saved. This can be achieved easily by adding the --reload option::

    $ paster serve --reload development.ini

Then you are ready to go.
