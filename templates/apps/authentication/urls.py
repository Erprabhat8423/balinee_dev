from django.urls import include, path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', views.index, name="login"),
    path('login', views.index, name="login"),
    path('logout/', views.logout_view, name='logout'),
]
