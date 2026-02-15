from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.RegisterAPIView.as_view(), name='register'),
    path('request_otp/', views.RequestOTPAPIView.as_view(), name='request_otp'),
    path('verify-otp/', views.VerifyOTPAPIView.as_view(), name='verify_otp'),

    # Dashboard
    path('products/', views.ProductAPIView.as_view(), name='products'),
    path('add_product/', views.ProductAPIView.as_view(), name='add_product'),

]
