from django import forms
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.contrib.auth.password_validation import validate_password
from . import models


class RegisterForm(forms.Form):
    username = forms.CharField(max_length=150)
    phone = forms.CharField(max_length=15, required=False)
    description = forms.CharField(widget=forms.Textarea, required=False)


class regiter_otp(forms.Form):
    phone = forms.CharField(max_length=15)


class verify_otp(forms.Form):
    phone = forms.CharField(
        max_length=15, 
        label="شماره موبایل",
        widget=forms.TextInput(attrs={'readonly': 'readonly'})
    )
    code = forms.CharField(
        max_length=6, 
        label="کد تایید",
        widget=forms.PasswordInput() 
    )