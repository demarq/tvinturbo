from django.urls import path, re_path
from .views import *

urlpatterns = [
    path('', index, name='index'),
    path('users/', users, name='users'),
    path('signup/', signup, name='signup'),
    path('logout/', logout, name='logout'),
    path('login/', login, name='login'),
    path('dosend/', dosend, name='dosend'),
    path('settings/', settings, name='settings'),
    path('message_settings/', message_settings, name='message_settings'),
    re_path(r'^user/(?P<id>[\d])/$', user_page, name='user page'),
]
