from django.urls import path,re_path
from ..views import *

app_name = 'src'
urlpatterns = [
    path('api/login', api.login),
    path('api/logout', api.logout),
    path('api/update-user-profile', api.updateUserProfile),
    path('api/update-user-password', api.updateUserPassword),
]