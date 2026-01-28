from rest_framework import serializers
from django.contrib.auth.models import User
from app.models import Category,Cart,Product,Profile,OTP,User
from drf_spectacular.utils import extend_schema, OpenApiExample, OpenApiTypes, extend_schema_field


class Register_serializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ['username' , 'phone' , 'description']

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