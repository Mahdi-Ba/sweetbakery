from django.conf.urls import url
from django.urls import path
from .api import views
from rest_framework_jwt.views import refresh_jwt_token

urlpatterns = [
    path('supplier', views.MySupplier.as_view(), name=None),
    path('brand/<int:pk>', views.GetBrand.as_view(), name=None),
    path('brand/<int:pk>/products', views.GetBrandProduct.as_view(), name=None),
    path('brand', views.BrandList.as_view(), name=None),

    path('product/type', views.ProductTypeList.as_view(), name=None),
    path('product/category', views.ProductCategoryList.as_view(), name=None),
    path('product/specification', views.ProductSpecificationList.as_view(), name=None),

    path('product/specification/supplier', views.ProductSpecificationSupplier.as_view(), name=None),
    path('product/discount/supplier', views.ProductDiscountSupplier.as_view(), name=None),
    path('product/images/supplier', views.ProductImagesSupplier.as_view(), name=None),

    path('product/supplier', views.ProductSupplier.as_view(), name=None),
    path('product/<int:pk>/supplier', views.GETProductSupplier.as_view(), name=None),
    path('product/<int:pk>/question/supplier', views.GETProductQuestionSupplier.as_view(), name=None),
    path('product/reply/question/<int:pk>', views.ReplyQuestionSupplier.as_view(), name=None),

    path('product/<int:pk>/rating/supplier', views.GETProductRatingSupplier.as_view(), name=None),

    path('product/limit/offers', views.ProductOffersList.as_view(), name=None),
    path('product/slider', views.ProductSliderList.as_view(), name=None),
    path('product/<int:pk>/question', views.ProductQuestion.as_view(), name=None),
    path('product/question', views.ProductAskQuestion.as_view(), name=None),

    path('product/<int:pk>/rating', views.ProductRating.as_view(), name=None),
    path('product/rating', views.AskProductRating.as_view(), name=None),
    path('product/favorite', views.ProductFavoriteList.as_view(), name=None),

    path('product', views.ProductList.as_view(), name=None),
    path('product/<int:pk>', views.GETProduct.as_view(), name=None),
    path('order/status', views.OrderStatusList.as_view(), name=None),

    path('order/<int:pk>', views.GetOrder.as_view(), name=None),
    path('order/qrcode/<str:pk>', views.GetOrderQr.as_view(), name=None),
    path('order', views.OrderList.as_view(), name=None),
    path('invoice/performa', views.InvoicePerforma.as_view(), name=None),
    path('invoice/performa/<int:pk>', views.InvoicePerformaDetail.as_view(), name=None),
    path('invoice/performa/supplier', views.InvoicePerformaSupplier.as_view(), name=None),
    path('order/supplier', views.OrderSupplierList.as_view(), name=None),
    path('order/<int:pk>/supplier', views.OrderSupplierDetailList.as_view(), name=None),
    path('invoice/<int:pk>/purchase', views.PurcheaseList.as_view()),

    path('my/notification', views.NotificationList.as_view(), name=None),

    path('tranaction', views.TransactionList.as_view(), name=None),
    path('withdraw', views.Withdraw.as_view(), name=None),
    path('deposit', views.Deposit.as_view(), name=None),
]
