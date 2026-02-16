from django.urls import path

from . import views

urlpatterns = [
    path('Register/', views.Register.as_view(), name='register'),
]
