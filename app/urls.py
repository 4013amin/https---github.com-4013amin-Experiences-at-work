from django.urls import path
from . import views

urlpatterns = [
     path('verify_otp/', views.otp_verify_view, name='verify_otp'),
     path('login-otp/', views.otp_request_view, name='otp_request'),
     path('register/', views.register, name='register'),
     path('logout/', views.logout_view, name='logout'),

     path('' , views.home, name='home'),

     path('products/', views.product_list, name='product_list'),  # لیست محصولات
     path('products/<int:pk>/', views.product_detail, name='product_detail'),  # جزئیات محصول (با ID)
     path('cart/', views.cart, name='cart'),  # سبد خرید
     path('checkout/', views.checkout, name='checkout'),
]