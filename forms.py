from django import forms
from .models import Permission, Role, RolePerm
from django.forms import BaseModelFormSet
import re
from django.conf import settings

apps = [i.split('.')[0] for i in settings.INSTALLED_APPS]
# remove duplicates
apps = set(apps)
app_choices = [(app,app) for app in apps]
# insert blank
app_choices.append(('',''))
bool_choices = [(True, 'True'), (False, 'False')]

class RoleForm(forms.ModelForm):

	class Meta:
		model = Role
		fields = ['name',]

		widgets={
				'name': forms.TextInput(
					attrs={
						'class': 'form-control',
						'autofocus': True,
						'required': True,
					}),
				}



RoleFormset = forms.modelformset_factory(
	RolePerm,
	fields=('app', 'desc', 'code', 'value'),
	extra=0,
	widgets={
		'app': forms.TextInput(
			attrs={
				'required': 'True',
				'class': 'form-control',
				'readonly': True,
			}),
		'desc': forms.TextInput(
			attrs={
				'required': 'True',
				'class': 'form-control',
				'placeholder': 'Description',
				'readonly': True,
			}),
		'value': forms.Select(choices=bool_choices,
			attrs={
				'required': 'True',
				'class': 'form-select'
				}),		
		}
	)



class CleanPerm(BaseModelFormSet):

	def clean(self):
		super().clean()

		regex = re.compile(r"[A-Za-z_]*")

		for form in self.forms:
			code = form.cleaned_data['code'].strip()
			result = regex.fullmatch(code)

			if not result:
				raise forms.ValidationError("code can only contain alphabets and underscore")
							
			form.cleaned_data['code'] = code
			# update the instance value.
			form.instance.code = code	



PermFormset = forms.modelformset_factory(
	Permission,
	formset=CleanPerm,
	fields=('app', 'desc', 'code', 'value'),
	extra=1,
	widgets={
		'app': forms.Select(choices=app_choices,
			attrs={
				'required': 'True',
				'class': 'form-select',
			}),
		'desc': forms.TextInput(
			attrs={
				'required': 'True',
				'class': 'form-control',
				'placeholder': 'Description',

			}),
		'code': forms.TextInput(
			attrs={
				'required': 'True',
				'class': 'form-control',
				'placeholder': 'perm_code',

			}),
		'value': forms.Select(choices=bool_choices,
			attrs={
				'required': 'True',
				'class': 'form-select'
				}),		
		}
	)