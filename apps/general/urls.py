from django.conf.urls import url
from django.urls import path
from .api import views
from rest_framework_jwt.views import refresh_jwt_token

urlpatterns = [
    path('state', views.StateList.as_view(), name=None),
    path('province/<int:pk>', views.ProvincesListByState.as_view(), name=None),
    path('location/<int:pk>', views.LocationListByProvince.as_view(), name=None),
    path('schaduling/<int:pk>', views.SchedulingListByLocation.as_view(), name=None),
]
