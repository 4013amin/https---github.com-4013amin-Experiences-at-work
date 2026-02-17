from django.urls import path

from . import views

urlpatterns = [
    path('Register/', views.VendorRequstAPIView.as_view(), name='VendorRequstAPIView'),
]
