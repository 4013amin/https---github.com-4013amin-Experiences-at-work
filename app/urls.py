from django.urls import path
from . import views

urlpatterns = [
     path('verify_otp/', views.otp_verify_view, name='verify_otp'),
     path('login-otp/', views.otp_request_view, name='otp_request'),
     path('register/', views.register, name='register'),
     path('logout/', views.logout_view, name='logout'),

     path('' , views.home, name='home'),
]