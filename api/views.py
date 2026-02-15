import random
from rest_framework.parsers import MultiPartParser, FormParser
from django.shortcuts import render, get_object_or_404
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from app.models import User, OTP, Profile, Category, Cart, Product
from rest_framework.response import Response
from . import serializers
from rest_framework import status
from drf_spectacular.utils import extend_schema, OpenApiExample, OpenApiResponse
from rest_framework.authtoken.models import Token
from django.db import transaction
import logging

logger = logging.getLogger(__name__)


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


@extend_schema(
    tags=['احراز هویت'],
    summary='تأیید کد (Verify OTP) و دریافت توکن',
    description='''
    این endpoint برای تایید کد ارسال شده به موبایل کاربر و دریافت توکن احراز هویت (Login) استفاده می‌شود.

    **مراحل کار:**
    1. کاربر کد دریافت شده را وارد می‌کند.
    2. سیستم صحت کد و انقضای آن را بررسی می‌کند.
    3. در صورت صحت، کد مصرف شده و حذف می‌گردد.
    4. یک توکن (Token) برای دسترسی‌های بعدی به کاربر داده می‌شود.
    ''',
    request=serializers.VerifyOTPSerializer,
    responses={
        200: OpenApiResponse(
            description='کد با موفقیت تایید شد و توکن صادر گردید',
            examples=[
                OpenApiExample(
                    'پاسخ موفق',
                    value={
                        "token": "9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b"
                    }
                )
            ]
        ),
        400: OpenApiResponse(
            description='خطا در اعتبار سنجی یا انقضای کد',
            examples=[
                OpenApiExample(
                    'کد منقضی شده یا اشتباه',
                    value={
                        "status": False,
                        "message": "کد وارد شده منقضی شده است یا اشتباه است."
                    }
                ),
                OpenApiExample(
                    'دیتا نامعتبر',
                    value={
                        "status": False,
                        "message": "دیتا نامعتبر است !",
                        "errors": {
                            "code": ["این فیلد الزامی است."]
                        }
                    }
                )
            ]
        ),
        404: OpenApiResponse(
            description='کاربر یا کد یافت نشد',
            examples=[
                OpenApiExample(
                    'یافت نشد',
                    value={
                        "detail": "Not found."
                    }
                )
            ]
        ),
        500: OpenApiResponse(
            description='خطای سرور',
            examples=[
                OpenApiExample(
                    'خطای سیستمی',
                    value={"error": "خطای سیستمی در پردازش احراز هویت."}
                )
            ]
        )
    }
)
class VerifyOTPAPIView(APIView):
    def post(self, request, *args, **kwargs):
        serializer = serializers.VerifyOTPSerializer(data=request.data)

        if not serializer.is_valid():
            return Response({
                "status": False,
                "message": "دیتا نامعتبر است !",
                "errors": serializer.errors
            })

        phone = serializer.validated_data['phone']
        code = serializer.validated_data['code']

        profile = get_object_or_404(Profile, phone=phone)
        user_obj = profile.user
        enter_code = get_object_or_404(OTP, user=user_obj, code=code)

        if not enter_code.is_valid():
            return Response({"error": "کد وارد شده منقضی شده است."}, status=status.HTTP_400_BAD_REQUEST)

        # Create Token
        try:
            with transaction.atomic():
                token, _ = Token.objects.get_or_create(user=user_obj)
                enter_code.delete()

                # Procces

        except Exception as e:
            logger.error(f"Error during OTP verification transaction for {user_obj.username}: {e}", exc_info=True)
            return Response({"error": "خطای سیستمی در پردازش احراز هویت."},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        response_data = {
            "status": True,
            "message": "ورود با موفقیت انجام شد",
            "data": {
                "token": token.key
            }
        }
        return Response(response_data, status=status.HTTP_200_OK)

    @extend_schema(
        summary="لیست محصولات پرفروش",
        description="این متد لیست تمام محصولاتی که وضعیت 'پرفروش ترین' (is_best_seller) آن‌ها فعال است را برمی‌گرداند.",
        responses={200: serializers.ProductSerializer(many=True)}
    )
    def get(self, request, *args, **kwargs):
        product = Product.objects.filter(is_best_seller=True)
        serializer = serializers.ProductSerializer(product, many=True)
        return Response(serializer.data)


@extend_schema(
    summary="ایجاد محصول جدید (با قابلیت آپلود عکس)",
    description="""
      برای ارسال عکس، حتماً از فرمت **multipart/form-data** استفاده کنید.
      در محیط Swagger، بعد از زدن دکمه Try it out، یک فیلد برای انتخاب فایل (Image) ظاهر می‌شود.
      """,
    request={
        'multipart/form-data': serializers.ProductSerializer,
    },
    responses={
        201: OpenApiResponse(description="محصول با موفقیت ساخته شد"),
        400: OpenApiResponse(description="خطا در مقادیر ورودی")
    }
)
class ProductAPIView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]


    def get(self, request, *args, **kwargs):
        product = Product.objects.filter(is_best_seller=True)
        serializer = serializers.ProductSerializer(product, many=True)
        return Response(serializer.data)

    def post(self, request, *args, **kwargs):
        serializer = serializers.ProductSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        image = serializer.validated_data['image']
        title = serializer.validated_data['title']
        description = serializer.validated_data['description']
        count = serializer.validated_data['count']
        price = serializer.validated_data['price']

        product = Product.objects.create(
            image=image,
            title=title,
            description=description,
            count=count,
            price=price,
        )

        product = serializer.save()

        response_data = {
            'status': True,
            'message': 'This is ok and data saved !',
            'data': serializers.ProductSerializer(product).data
        }
        return Response(response_data, status=status.HTTP_200_OK)
