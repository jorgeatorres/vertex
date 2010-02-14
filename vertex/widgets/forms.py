# -*- coding: utf-8 -*-
from tw.jquery import js_function, js_callback
from tw.forms import TableForm, TextField, TextArea, HiddenField, Spacer, \
                     FileField
from tw.forms.validators import UnicodeString, FieldStorageUploadConverter

class AjaxForm(TableForm):
    params = ['id', 'target', 'beforeSubmit', 'action',
              'type', 'dataType', 'clearForm', 'resetForm']

    target = ''
    beforeSubmit = ''
    type = 'POST'
    dataType = 'json'
    clear = False
    resetForm = False

    template = "genshi:vertex.widgets.templates.ajaxform"
    javascript = []
    include_dynamic_js_calls = True

    def update_params(self, d):
        super(AjaxForm, self).update_params(d)
        if not getattr(d, "id", None):
            raise ValueError("AjaxForm is supposed to have an id")

#        options = dict(
#            target=('#%s' % self.target),
#            beforeSubmit=self.beforeSubmit,
#            success=js_callback('function(r,s) { vertex.forms.handle_form_basic("%s", r); }' % d.id),
#            url=self.action,
#            type=self.type,
#            dataType=self.dataType,
#            clearForm=self.clearForm,
#            resetForm=self.resetForm)
#
#        call = js_function('$("#%s").ajaxForm' % d.id)(options)
#        self.add_call(call)

class AddBlankFileForm(AjaxForm):
    fields = [TextField(u'filename', label_text=u'Filename', validator=UnicodeString(not_empty=True,
                                                                                     strip=True,
                                                                                     max=255)),
              HiddenField(u'project_id')]
    submit_text = u'Crear'

class ImportFileForm(TableForm):
    fields = [FileField(u'file', validator=FieldStorageUploadConverter(not_empty=True)),
              HiddenField(u'project_id')]
    submit_text = u'Importar'
    
class UpdateFileForm(TableForm):
    fields = [FileField(u'file', validator=FieldStorageUploadConverter(not_empty=True)),
              HiddenField(u'file_id')]
    submit_text = u'Actualizar'
    
class AddProjectForm(AjaxForm):
    fields = [TextField(u'title', validator=UnicodeString(not_empty=True, strip=True,
                                                          max=255)),
              TextArea(u'description', validator=UnicodeString(strip=True))]
    submit_text = u'Create'
    
class ProfileEditForm(AjaxForm):
    fields = [TextField(u'email_address', label_text=u'Correo electrónico'),
              Spacer(),
              TextField(u'institution')]
    submit_text = u'Guardar'
    
class InvitePeopleForm(AjaxForm):
    fields = [TextArea(u'emails', label_text=u'Correos electrónicos',
                       validator=UnicodeString(not_empty=True, strip=True)), HiddenField('project_id')]
    submit_text = u'Invitar'
    
   
add_blank_file_form = AddBlankFileForm('add_blank_file_form', action='/files/new')
import_file_form = ImportFileForm('import_file_form', action='/files/upload')
update_file_form = UpdateFileForm('update_file_form', action='/files/upload_update')

add_project_form = AddProjectForm('add_project_form',
                                  action=u'/projects/add_do')

invite_people_form = InvitePeopleForm('invite_people_form',
                                      action=u'/projects/members_add')

profile_edit_form = ProfileEditForm('profile_edit_form',
                                    action=u'/profile_edit_do',
                                    clearForm=False,
                                    resetForm=False,
                                    success=js_callback('vertex.forms.handle_form'))