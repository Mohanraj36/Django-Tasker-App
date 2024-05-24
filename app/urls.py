from . import views
from django.urls import path

urlpatterns = [
    path('', views.index, name='index'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('register/', views.user_register, name='register'),
    # path('profile/', views.profile, name='profile'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('task-form', views.task_form, name='task-form'),
    path('ticket-form', views.ticket_form, name='ticket-form'),
    path('search', views.search, name='search'),
]
