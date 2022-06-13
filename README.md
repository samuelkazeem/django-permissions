Django has a permissions system which is almost impossible to use if you intend to give non-staff users the ability to control permissions on your Django App.

With this you can create permissions by App and objects in each App, assign those permissions to roles which controls what each user(assigned to that role) can do.


## SETUP

* Clone this repo to a *permissions* folder in your django project
* Add *permissions* to settings INSTALLED_APPS
* Add *permissions* to urls.py
* Add a ForeignKey field *role* to your user model. This field links to *'permissions.Role'*
* Run *makemigrations* and  *migrate*
* Create Permissions, Roles and assign users to roles.
* In your login script use *calls.get_perms(request)* to set user permission.
* In your views use *calls.perm_required('app_name', perm_code)* to check permissions.
* Change *nav.html* to your base navigation file


## LIBRARIES

The following external libraries were used.

* Jquery 3.0.6
* Bootstrap 5.0.2