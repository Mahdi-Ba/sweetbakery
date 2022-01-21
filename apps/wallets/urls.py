from django.urls import path

from .api import views

urlpatterns = [
    path('', views.WalletList.as_view(), name=None),
    path('deposit', views.Deposit.as_view(), name=None),
    path('withdraw', views.WithDraw.as_view(), name=None),
]
