from django.conf.urls import url
from django.urls import path
from .api import views
from rest_framework_jwt.views import refresh_jwt_token

urlpatterns = [
    path('upload', views.FileUploadView.as_view(), name=None)
]
