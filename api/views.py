import random

from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from app.models import User, OTP, Profile, Category, Cart, Product
from rest_framework.response import Response
from . import serializers
from rest_framework import status
from drf_spectacular.utils import extend_schema, OpenApiExample, OpenApiResponse
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


@extend_schema(
    tags=['احراز هویت'],
    summary='درخواست کد تایید (OTP)',
    description='''
    این endpoint برای درخواست کد یکبار مصرف (OTP) استفاده می‌شود.

    **کاربردها:**
    - ثبت نام کاربر جدید
    - ورود با شماره موبایل
    - بازیابی رمز عبور

    **نکات مهم:**
    - کد OTP فقط 5 دقیقه اعتبار دارد
    - هر شماره موبایل فقط می‌تواند هر 2 دقیقه یکبار درخواست کد جدید کند
    - کد فقط یکبار قابل استفاده است
    ''',
    request=serializers.RequestOTPSerializer,
    responses={
        201: OpenApiResponse(
            response=serializers.RequestOTPSerializer,
            description='کد OTP با موفقیت ایجاد و ارسال شد',
            examples=[
                OpenApiExample(
                    'نمونه پاسخ موفق',
                    value={
                        "status": True,
                        "message": "کد تأیید با موفقیت به شماره موبایل شما ارسال شد",
                        "data": {
                            "otp_id": "123e4567-e89b-12d3-a456-426614174000",
                            "phone": "09123456789",
                            "expires_at": "2024-01-30T15:30:00Z"
                        }
                    }
                )
            ]
        ),
        400: OpenApiResponse(
            description='خطا در درخواست',
            examples=[
                OpenApiExample(
                    'شماره موبایل نامعتبر',
                    value={
                        "status": False,
                        "message": "شماره موبایل معتبر نیست",
                        "errors": {
                            "phone": ["لطفاً یک شماره موبایل معتبر وارد کنید."]
                        }
                    }
                ),
                OpenApiExample(
                    'درخواست مکرر',
                    value={
                        "status": False,
                        "message": "لطفاً 2 دقیقه صبر کنید سپس مجدداً تلاش کنید"
                    }
                )
            ]
        ),
        429: OpenApiResponse(
            description='تعداد درخواست بیش از حد',
            examples=[
                OpenApiExample(
                    'Rate Limit Exceeded',
                    value={
                        "status": False,
                        "message": "تعداد درخواست‌های شما بیش از حد مجاز است. لطفاً 15 دقیقه دیگر تلاش کنید."
                    }
                )
            ]
        )
    }
)
class RequestOTPAPIView(APIView):
    def post(self, request, *args, **kwargs):
        serializer = serializers.RequestOTPSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({
                "status": False,
                "message": "دیتا نامعتبر است !",
                "errors": serializer.errors
            })

        phone = serializer.validated_data['phone']

        try:
            profile = Profile.objects.get(phone=phone)

            code = str(random.randint(100000, 999999))
            otp = OTP.objects.create(user=profile.user, code=code)

            print(f"OTP for {profile.user.username}: {code}")

            response_data = {
                "status": True,
                "message": "کد تأیید با موفقیت ارسال شد",
                "data": {
                    "otp_id": str(otp.id),
                    "phone": phone,
                }
            }

            return Response(response_data, status=status.HTTP_201_CREATED)

        except Profile.DoesNotExist:
            return Response({
                "status": False,
                "message": "شماره تلفن یافت نشد. لطفاً ابتدا ثبت نام کنید.",
                "error_code": "PROFILE_NOT_FOUND"
            }, status=status.HTTP_404_NOT_FOUND)


