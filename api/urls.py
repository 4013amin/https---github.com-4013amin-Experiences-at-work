from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.RegisterAPIView.as_view(), name='register'),
    path('request_otp/', views.RequestOTPAPIView.as_view(), name='request_otp'),
    path('verify-otp/', views.VerifyOTPAPIView.as_view(), name='verify_otp'),

    # Profile
    path('profile', views.ProfileAPIView.as_view(), name='profile'),

    # Dashboard
    path('products/', views.ProductAPIView.as_view(), name='products'),
    path('categories/', views.CategoryAPIView.as_view(), name='categories'),

    # Cart
    path('cart/', views.CartAPIView.as_view(), name='cart'),

    path('pyment_history/', views.PymentHistoryAPIView.as_view(), name='orders'),
]
