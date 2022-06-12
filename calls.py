from django.shortcuts import redirect
from functools import wraps
from django.http import HttpResponseRedirect
from django.contrib import messages
from .models import RolePerm

def perm_required(app, code):
	def check_perm(function):

		@wraps(function)
		def wrap(request, *args, **kwargs):

			user = request.user
			# superuser always returns true
			if user.is_superuser:
				perm = True
			else:
				try:
					perm = request.session['perm'].get(app, False).get(code, False)
				except:
					# permission might have been used in views and not added yet to db
					perm = False
			if perm:
				return function(request, *args, **kwargs)
			else:
				messages.error(request, 'You do not have access this resource.')
				return redirect('/')

		return wrap
	return check_perm


def get_perms(request):
	"""
	gets and stores each user's permissions in session at login
	"""
	user_perm = RolePerm.objects.filter(role=request.user.role)

	perm_dict = {}
	for perm in user_perm:
		try:
			# app key exists
			perm_dict[perm.app][perm.code] = perm.value
		except:
			# init app key
			perm_dict[perm.app] = {}
			# create first input
			perm_dict[perm.app][perm.code] = perm.value

	request.session['perm'] = perm_dict