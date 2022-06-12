from django.shortcuts import redirect, render, get_object_or_404
from django.urls import reverse, reverse_lazy
from .models import Role, RolePerm, Permission
from .forms import RoleForm, RoleFormset, PermFormset
from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.db.models import Q, ProtectedError
from django.http import HttpResponseRedirect
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib.sessions.models import Session
from django.contrib.sessions.backends.db import SessionStore
from django.utils import timezone
from .calls import perm_required
from django.conf import settings
from django.contrib.auth import get_user_model

User = get_user_model()
ITEMS_PER_PAGE = 20

def process_action(request, action, selected_ids):
	# print(action, selected_ids)

	if action == 'Delete':
		return HttpResponseRedirect(reverse('delete-role', args=(selected_ids,)))
	else:
		messages.error(request, 'No such action')
		return redirect('all-roles')


def update_session_perm(role, perm_dict):
	"""
	update permissions for existing sessions
	"""
	all_current_sessions = Session.objects.filter(expire_date__gte=timezone.now())

	for session in all_current_sessions:
		# check for logged in users
		session_data = session.get_decoded()
		# print(session_data)
		if '_auth_user_id' in session_data:

			user = User.objects.get(pk=session_data['_auth_user_id'])
			
			if user.role==role:
				s = SessionStore(session_key=session.session_key)
				s['perm'] = perm_dict
				s.save()
				# s.modified


def update_roles(new_perms):
	"""
	update roles when permission objects are created
	"""

	all_roles = Role.objects.filter()
	# if no roles don't bother
	if all_roles:
		for perm in new_perms:
			for role in all_roles:
				RolePerm.objects.create(app=perm.app, desc=perm.desc, code=perm.code, value=perm.value, role=role)

		for role in all_roles:
			role_perm = RolePerm.objects.filter(role=role)

			perm_dict = {}
			for perm in role_perm:
				try:
					perm_dict[perm.app][perm.code] = perm.value
				except:
					# init app key
					perm_dict[perm.app] = {}
					# create first input
					perm_dict[perm.app][perm.code] = perm.value
		
			update_session_perm(role, perm_dict)




@login_required
def permissions(request):

	perm_items = Permission.objects.filter().order_by('app')
	edit_ids = [i.pk for i in perm_items]

	formset = PermFormset(queryset=perm_items)
	formset.extra=0 if perm_items else 1

	if request.method == 'POST':
		formset = PermFormset(request.POST)
		
		if formset.is_valid():
			new_perms = []

			for form in formset:
				try:
					edit_ids.remove(form.cleaned_data['id'].pk)
					save_perm = form.save(commit=False)
					save_perm.desc = save_perm.desc.title()
					save_perm.code = save_perm.code.lower()
					save_perm.save()                 
				except:
					# new line items do not have pk attribute
					save_perm = form.save(commit=False)
					save_perm.desc = save_perm.desc.title()
					save_perm.code = save_perm.code.lower()
					save_perm.save()

					new_perms.append(save_perm)

			if new_perms:
				# add new perms to existing roles
				update_roles(new_perms)

			# items still in edit_ids have been deleted by the user
			Permission.objects.filter(pk__in=edit_ids).delete()

			messages.success(request, 'Permissions Updated')
			return redirect('all-perms')
		else:
			messages.error(request, formset.non_form_errors())

	context = {'title':'User Permissions', 'formset':formset}
	return render(request, 'perm/permissions.html', context)



@login_required
@perm_required('permissions', 'view_perms')
def search(request):

	name = request.GET.get('role')

	arguments = Q()
	if name: arguments = Q(name__icontains=name)

	all_roles = Role.objects.filter(arguments)
	
	page = request.GET.get('page', 1)
	paginator = Paginator(all_roles, ITEMS_PER_PAGE)

	try:
		roles = paginator.page(page)
	except PageNotAnInteger:
		roles = paginator.page(1)
	except EmptyPage:
		roles = paginator.page(paginator.num_pages)

	context = {'roles':roles, 'rolename':name, 'title':'Search Roles'}
	return render(request, 'perm/all.html', context)
	


@login_required
@perm_required('permissions', 'view_perms')
def all(request):

	if request.method == 'GET':
		all_roles = Role.objects.filter()
		
		page = request.GET.get('page', 1)
		paginator = Paginator(all_roles, ITEMS_PER_PAGE)
		
		try:
			roles = paginator.page(page)
		except PageNotAnInteger:
			roles = paginator.page(1)
		except EmptyPage:
			roles = paginator.page(paginator.num_pages)

		context = {'roles':roles, 'title':'All Roles'}
		return render(request, 'perm/all.html', context)
	
	elif request.method == 'POST':
		action = request.POST['action']
		selected_ids = request.POST.getlist('selected_ids')
		
		if not selected_ids:
			messages.error(request, 'select role')
			return redirect('all-roles')

		return process_action(request, action, selected_ids)



@login_required
@perm_required('permissions', 'create_perms')
def new(request):
	form = RoleForm(request.GET or None)
	perms = Permission.objects.filter().order_by('app')
	formset = RoleFormset(queryset=perms)

	if request.method == 'POST':
		request.POST._mutable = True
		request.POST['form-INITIAL_FORMS'] = '0'
		request.POST._mutable = False

		form = RoleForm(request.POST)
		formset = RoleFormset(request.POST)

		if form.is_valid() and formset.is_valid():
			try:
				save_role = form.save(commit=False)
				save_role.name = save_role.name.title()
				save_role.save(request)

				for item in formset:
					save_item = item.save(commit=False)
					save_item.role = save_role
					save_item.save()

				messages.success(request, 'New role created')
				
				if 'save_continue' in request.POST:
					return redirect('all-roles')
				else:
					return redirect('new-role')

			except IntegrityError:
				messages.error(request, 'Role Already Exists')            

		else:
			errors = form.errors if form.errors else formset.errors
			messages.error(request, errors)

	context = {'form':form, 'formset':formset, 'title':'New Role'}
	return render(request, 'perm/objects.html', context)




@login_required
@perm_required('permissions', 'edit_perms')
def edit(request, pk):

	role = get_object_or_404(Role, pk=pk)
	role_name = role.name

	if role_name == 'Administrator':
		messages.error(request, 'Admin role cannot be edited')
		return redirect('all-roles')

	form = RoleForm(instance=role)
	if role_name == 'Manager':
		# prevent changing of manager role name
		form.fields['name'].disabled = True

	perms = RolePerm.objects.filter(role=role).order_by('app')
	formset = RoleFormset(queryset=perms)

	if request.method == 'POST':
		if role_name == 'Manager':
			# prevent changing of manager role name
			request.POST._mutable = True
			request.POST['name'] = role_name
			request.POST._mutable = False

		form = RoleForm(request.POST, instance=role)
		formset = RoleFormset(request.POST)

		if form.is_valid() and formset.is_valid():
			# print(formset.cleaned_data)
			try:
				save_role = form.save(commit=False)
				save_role.name = save_role.name.title()
				save_role.save(request)
				
				formset.save()
				# update loggedin users with role with permission, if the formset was changed.

				clean_form = formset.cleaned_data

				perm_dict = {}
				for perm in clean_form:
					try:
						perm_dict[perm['app']][perm['code']] = perm['value']
					except:
						# init app key
						perm_dict[perm['app']] = {}
						# create first input
						perm_dict[perm['app']][perm['code']] = perm['value']                
				
				update_session_perm(save_role, perm_dict)

				messages.success(request, 'Role Updated')

				# redirect
				if 'save_continue' in request.POST:
					return redirect('all-roles')
					# return HttpResponseRedirect(reverse('edit-user', args=(save_vendor.id,)))
				else:
					return redirect('new-role')

			except IntegrityError:
				messages.error(request, 'Role Already Exists')

		else:
			errors = form.errors if form.errors else formset.errors
			messages.error(request, errors)

	context = {'form':form, 'formset':formset, 'title':'Edit Role'}
	return render(request, 'perm/objects.html', context)



@login_required
@perm_required('permissions', 'delete_perms')
def delete(request, ids):
	# remove unneeded items and convert to list
	ids = ids.replace('[','').replace(']','').replace("'",'').split(',')
	roles = ''
	role_object = []

	for pk in ids:
		role = get_object_or_404(Role, id=pk.strip())

		if len(ids) == 1:
			roles += str(role)
		else:
			if pk != ids[-1]:
				roles += str(role) + ', '
			else:
				roles += ' and ' + str(role)

		role_object.append(role)

	if request.method == 'POST':
		for r in role_object:
			try:
				r.delete()
			except ProtectedError:
				messages.error(request, f"{r} cannot be deleted. Users are assigned to {r}.")
				return redirect('all-roles')

		messages.success(request, 'Delete Successfull')
		return redirect('all-roles')

	context = {'roles':roles}
	return render(request, 'perm/delete.html', context)