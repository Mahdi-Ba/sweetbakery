from django.conf.urls import url
from django.urls import path
from .api import views
from rest_framework_jwt.views import refresh_jwt_token

urlpatterns = [
    path('', views.UserList.as_view(), name=None),
    path('register', views.Register.as_view(), name=None),
    path('login', views.StaticLogin.as_view(), name=None),
    path('refresh/token', refresh_jwt_token),
]
