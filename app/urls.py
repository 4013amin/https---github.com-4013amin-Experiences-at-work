from django.urls import path
from . import views

urlpatterns = [
     path('register/', views.register, name='register'),
     path('register_otp/', views.otp_request_view, name='register_otp'),
     path('verify_otp/', views.otp_verify_view, name='verify_otp'),
]