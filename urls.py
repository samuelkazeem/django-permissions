from django.urls import path
from .import views

urlpatterns = [
    path('', views.permissions, name='all-perms'),
    path('all/', views.all, name='all-roles'),
    path('new/', views.new, name='new-role'),
    path('search/', views.search, name='search-role'),
    path('edit/<int:pk>', views.edit, name='edit-role'),
    path('delete/<ids>', views.delete, name='delete-role'),
]