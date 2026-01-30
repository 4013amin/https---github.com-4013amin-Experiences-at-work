from rest_framework import serializers
from django.contrib.auth.models import User
from app.models import Category,Cart,Product,Profile,OTP,User
from drf_spectacular.utils import extend_schema, OpenApiExample, OpenApiTypes, extend_schema_field


class Register_serializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ['username' , 'phone' , 'description']


    def validate_username(self , value):
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("این نام کاربری قبلاً ثبت شده است")
        return value

    def validate_phone(self, value):
        if Profile.objects.filter(phone=value).exists():
            raise serializers.ValidationError("این شماره تلفن قبلاً ثبت شده است")
        return value


    def create(self , validated_data):
        user = User.objects.create_user(
            username = validated_data['username']
        )

        profile = Profile.objects.create(
            user = user,
            username=validated_data['username'],
            phone = validated_data['phone'],
            description = validated_data['description']
        )

        return profile


class RequestOTPSerializer(serializers.Serializer):
    phone = serializers.CharField(max_length=11)

    def validate_phone(self, value):
        if not value.isdigit() or len(value) != 11 or not value.startswith('09'):
            raise serializers.ValidationError("لطفاً یک شماره موبایل معتبر (مانند 09123456789) وارد کنید.")
        return value