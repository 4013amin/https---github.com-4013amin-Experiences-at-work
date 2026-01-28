from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from app.models import User, OTP, Profile, Category, Cart, Product
from rest_framework.response import Response
from . import serializers
from rest_framework import status
from drf_spectacular.utils import extend_schema, OpenApiExample
from rest_framework.authtoken.models import Token

# Create your views here.
@extend_schema(
    request=serializers.Register_serializer,
    responses={201: OpenApiExample(
        'ثبت نام موفق',
        value={"status": True, "message": "با موفقیت ثبت‌نام شدید"}
    )}
)
class RegisterAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = serializers.Register_serializer(data=request.data)
        if not serializer.is_valid():
            return Response({
                "status": False,
                "message": "دیتا نامعتبر است !",
                "errors": serializer.errors
            })

        serializer.save()

        return Response({
            "status": True,
            "message": "با موفقیت ثبت‌نام شدید",
        }, status=status.HTTP_201_CREATED)

    def put(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return Response({
                "status": False,
                "message": "ابتدا باید لاگین کنید"
            }, status=status.HTTP_401_UNAUTHORIZED)

        try:
            profile = Profile.objects.get(user=request.user)
        except Profile.DoesNotExist:
            return Response({
                "status": False,
                "message": "پروفایل یافت نشد"
            }, status=status.HTTP_404_NOT_FOUND)

        serializer = serializers.Register_serializer(instance=profile, data=request.data, partial=True)

        if not serializer.is_valid():
            return Response({
                "status": False,
                "message": "دیتا نامعتبر است!",
                "errors": serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)

        serializer.save()
        return Response({
            "status": True,
            "message": "با موفقیت ویرایش شدید"
        }, status=status.HTTP_200_OK)
