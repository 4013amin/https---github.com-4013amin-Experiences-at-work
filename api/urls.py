from django.urls import path
from . import views

urlpatterns = [
    path('register/' , views.RegisterAPIView.as_view(), name='register'),
    path('request_otp/' , views.RequestOTPAPIView.as_view(), name='request_otp'),
]