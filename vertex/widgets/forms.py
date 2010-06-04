# coding: utf-8
import json
from pylons.i18n import ugettext as _, lazy_ugettext as l_
from tg import url

from tw.jquery import js_function, js_callback
from tw.forms import TableForm, TextField, TextArea, HiddenField, Spacer, \
                     FileField, PasswordField
from tw.forms.validators import UnicodeString, FieldStorageUploadConverter, Email


class AjaxForm(TableForm):
    params = ['id', 'action', 'clearForm', 'resetForm', 'disableSubmit',
              'submitAltText', 'callback']
    template = "genshi:vertex.widgets.templates.ajaxform"
    
    clearForm = True # TODO: implement this!
    resetForm = True
    disableSubmit = True
    submitAltText = None
    callback = None

    def update_params(self, d):
        super(AjaxForm, self).update_params(d)
        if not getattr(d, "id", None):
            raise ValueError("AjaxForm is supposed to have an id")
        d['ajaxconf'] = json.dumps({'id': d['id'],
                                    'action': d['action'],
                                    'clearForm': self.clearForm,
                                    'resetForm': self.resetForm,
                                    'disableSubmit': self.disableSubmit,
                                    'submitAltText': self.submitAltText,
                                    'callback': self.callback})

class AddBlankFileForm(AjaxForm):
    fields = [TextField(u'filename', label_text=_('Filename'), help_text=_('.latex'), validator=UnicodeString(not_empty=True,
                                                                                                      strip=True,
                                                                                                      max=255)),
              HiddenField(u'project_id')]
    submit_text = _('Create file')

class ImportFileForm(TableForm):
    fields = [FileField(u'file', validator=FieldStorageUploadConverter(not_empty=True)),
              HiddenField(u'project_id')]
    submit_text = _('Import file')
    
class UpdateFileForm(TableForm):
    fields = [FileField(u'file',
                        help_text=_('Upload a new version of this file'),
                        validator=FieldStorageUploadConverter(not_empty=True)),
              HiddenField(u'file_id')]
    submit_text = _('Update file')
    
class AddProjectForm(AjaxForm):
    fields = [TextField(u'title', validator=UnicodeString(not_empty=True, strip=True,
                                                          max=255)),
              TextArea(u'description', validator=UnicodeString(strip=True))]
    submit_text = u'Create'
    
class ProfileEditForm(AjaxForm):
    fields = [TextField(u'email_address', label_text=_('E-mail'), validator=Email(not_empty=True, strip=True)),
              PasswordField(u'new_password', label_text=_('New password'), validator=UnicodeString(strip=True, if_invalid=None, if_empty=None)),
              Spacer(),
              TextField(u'institution', label_text=_('Institution'), validator=UnicodeString(strip=True, if_empty=u'', if_invalid=u''))]
    submit_text = _('Update profile')
    
class InvitePeopleForm(AjaxForm):
    fields = [TextArea(u'emails', label_text=_('E-mails'), help_text=_('Separate distinct e-mails with a comma'),
                       validator=UnicodeString(not_empty=True, strip=True)), HiddenField('project_id')]
    submit_text = _('Invite')
    
   
add_blank_file_form = AddBlankFileForm('add_blank_file_form', action=url('/files/new'))
import_file_form = ImportFileForm('import_file_form', action=url('/files/upload'))
update_file_form = UpdateFileForm('update_file_form', action=url('/files/upload_update'))

add_project_form = AddProjectForm('add_project_form',
                                  action=url('/projects/add_do'))

invite_people_form = InvitePeopleForm('invite_people_form',
                                      action=url('/projects/members_add'))

profile_edit_form = ProfileEditForm('profile_edit_form',
                                    action=url('/profile_edit_do'),
                                    clearForm=False,
                                    resetForm=False)