## SETUP

* Clone this repo to your root project folder
* Add *permissions* to settings INSTALLED_APPS
* Add *permissions* to urls.py
* Run *python manage.py migrate*
* In your login script use *calls.get_perms(request)* to set user permission.
* In your views use *calls.perm_required('app_name', perm_code)* to check permissions.
* Change *nav.html* to your base navigation file


## LIBRARIES

The following external libraries were used.

* Jquery 3.0.6
* Bootstrap 5.0.2