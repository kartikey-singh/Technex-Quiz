from django.conf.urls import url
from .views import *
from django.contrib.auth.views import *

urlpatterns=[
##    url(r'^$', StartTest, name='index'),
##    url(r'^login', LoginView, name='login'),
##    url(r'^logout', LogoutView, name='logout'),
##    url(r'^register', RegistrationView, name='register'),

    url(r'^$', HomeView),    
    url(r'^dashboard', DashboardView, name ='dashboard'),
    url(r'^about', AboutView, name='about'),
    url(r'^index', IndexView, name='index'),
    url(r'^home', HomeView, name='home'),
    
    url(r'^login', LoginView, name='login'),
    url(r'^logout', LogoutView, name='logout'),
    url(r'^register', RegistrationView, name='register'),
    url(r'^test', StartTest, name='StartTest'),
##    url(r'^quiz/dashboard/create_post/$', views.create_post),
]