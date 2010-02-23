# coding: utf-8

"""The base Controller API."""

from tg import TGController, tmpl_context
from tg.render import render
from tg import request, expose
import pylons
from pylons.i18n import _, ungettext, N_
from tw.api import WidgetBunch
import vertex.model as model

__all__ = ['Controller', 'BaseController']


class BaseController(TGController):
    """
    Base class for the controllers in the application.

    Your web application should have one of these. The root of
    your application is used to compute URLs used by your app.

    """

    def __call__(self, environ, start_response):
        """Invoke the Controller"""
        # TGController.__call__ dispatches to the Controller method
        # the request is routed to. This routing information is
        # available in environ['pylons.routes_dict']

        request.identity = request.environ.get('repoze.who.identity')
        tmpl_context.identity = request.identity
        return TGController.__call__(self, environ, start_response)

@expose('json')
def ajax_form_error_handler(self, **kw):
    res = dict(_status=u'error',
               _msg=_('The form could not be sent because it contains errors.'))

    if pylons.c.form_errors:
        res['form_errors'] = pylons.c.form_errors
        res['form_values'] = pylons.c.form_values

    return res