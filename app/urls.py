from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
     path('verify_otp/', views.otp_verify_view, name='verify_otp'),
     path('login-otp/', views.otp_request_view, name='otp_request'),
     path('register/', views.register, name='register'),
     path('logout/', views.logout_view, name='logout'),

     path('' , views.dashboard, name='home'),

     path('products/', views.product_list, name='product_list'),
     path('products/<int:pk>/', views.product_detail, name='product_detail'),
     path('cart/', views.cart, name='cart'),
     path('checkout/', views.checkout, name='checkout'),
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
