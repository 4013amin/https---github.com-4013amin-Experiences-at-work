import random
from datetime import timezone, timedelta

from rest_framework.parsers import MultiPartParser, FormParser
from django.shortcuts import render, get_object_or_404
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from app.models import User, OTP, Profile, Category, Cart, Product, HistoryPyment
from rest_framework.response import Response
from . import serializers
from rest_framework import status
from drf_spectacular.utils import extend_schema, OpenApiExample, OpenApiResponse
from rest_framework.authtoken.models import Token
from django.db import transaction
import logging

from .serializers import CartSerializer, PymentHistorySerializer

logger = logging.getLogger(__name__)


# Create your views here.
@extend_schema(
    tags=['ثبت نام اولیه'],
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
        enter_code = OTP.objects.filter(
            user=user_obj,
            code=code,
            created_at__gte=timezone.now() - timedelta(minutes=5)
        ).first()

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


# Profile Section
class ProfileAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="دریافت اطلاعات پروفایل",
        description="این متد اطلاعات پروفایل کاربری که در حال حاضر لاگین کرده است (بر اساس توکن) را برمی‌گرداند.",
        responses={
            200: serializers.ProfileSerializer,
            401: OpenApiResponse(description="توکن نامعتبر یا ارسال نشده است")
        }
    )
    def get(self, request, *args, **kwargs):
        profile = get_object_or_404(Profile, user=self.request.user)
        serializer = serializers.ProfileSerializer(profile)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(
        summary="ویرایش پروفایل کاربر",
        description="""
          با استفاده از این متد، کاربر می‌تواند اطلاعات پروفایل خود را ویرایش کند. 
          نکته: فیلد شماره موبایل یا نام کاربری اگر در سریالایزر Unique باشند، نباید تکراری ارسال شوند.
          """,
        request=serializers.ProfileSerializer,
        responses={
            200: OpenApiResponse(
                description="ویرایش با موفقیت انجام شد",
                examples=[OpenApiExample('نمونه پاسخ موفق', value={
                    "status": True,
                    "message": "پروفایل با موفقیت به‌روزرسانی شد",
                    "data": {"username": "new_name", "phone": "0912..."}
                })]
            ),
            400: OpenApiResponse(description="خطا در اعتبارسنجی داده‌ها")
        }
    )
    def put(self, request, *args, **kwargs):
        profile = get_object_or_404(Profile, user=self.request.user)
        serializer = serializers.ProfileSerializer(profile, data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)


class ProductAPIView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

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
    def post(self, request, *args, **kwargs):
        serializer = serializers.ProductSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        image = serializer.validated_data['image']
        title = serializer.validated_data['title']
        description = serializer.validated_data['description']
        count = serializer.validated_data['count']
        price = serializer.validated_data['price']
        category = serializer.validated_data['category']

        products = Product.objects.create(
            image=image,
            title=title,
            description=description,
            count=count,
            price=price,
            category=category
        )

        products = serializer.save()

        response_data = {
            'status': True,
            'message': 'محصول با موفقیت ذخیره شد .',
            'data': serializers.ProductSerializer(products).data
        }
        return Response(response_data, status=status.HTTP_200_OK)


class CategoryAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        categories = Category.objects.all()
        serializer = serializers.CategorySerializer(categories, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class CartAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="مشاهده سبد خرید کاربر",
        description="این متد تمام محصولاتی که کاربر فعلی به سبد خرید خود اضافه کرده است را نمایش می‌دهد.",
        responses={
            200: serializers.CartSerializer(many=True),
            401: OpenApiResponse(description="کاربر وارد نشده است")
        }
    )
    def get(self, request, *args, **kwargs):
        cart_items = Cart.objects.filter(user=request.user)
        serializer = serializers.CartSerializer(cart_items, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(
        summary="افزودن محصول به سبد خرید",
        description="""
    شناسه محصول (product) و وضعیت اعمال کد تخفیف (code_offer) را ارسال کنید.
    فرمت درخواست باید multipart/form-data یا application/json باشد.
            """,
        request=CartSerializer,
        responses={
            201: OpenApiResponse(
                response=CartSerializer,
                description="محصول با موفقیت اضافه شد",
                examples=[
                    OpenApiExample(
                        "نمونه پاسخ موفق",
                        value={
                            "status": True,
                            "message": "محصول با موفقیت به سبد خرید اضافه شد.",
                            "data": {
                                "id": 1,
                                "product": 10,
                                "code_offer": False,
                                "user": 3
                            }
                        }
                    )
                ]
            ),
            400: OpenApiResponse(description="اطلاعات نامعتبر است")
        }
    )
    def post(self, request, *args, **kwargs):
        serializer = serializers.CartSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        product = serializer.validated_data['product']
        code_offer = serializer.validated_data['code_offer']

        cart_item = Cart.objects.create(
            user=request.user,
            product=product,
            code_offer=code_offer
        )

        response_data = {
            'status': True,
            'message': 'محصول با موفقیت به سبد خرید اضافه شد.',
            'data': serializers.CartSerializer(cart_item).data
        }
        return Response(response_data, status=status.HTTP_201_CREATED)


class PymentHistoryAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        history = HistoryPyment.objects.filter(user=request.user)
        serializer = serializers.PymentHistorySerializer(history, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(
        summary="افزودن دیتا به تاریخچه پرداخت ها به صورت تست است این متد",
        request=PymentHistorySerializer,
        responses={
            201: OpenApiResponse(
                response=CartSerializer,
                description="تاریخچه ایجاد شد",
                examples=[
                    OpenApiExample(
                        "نمونه پاسخ موفق",
                        value={
                            "status": True,
                            "message": "تاریخچه پرداخت ایجاد شد",

                        }
                    )
                ]
            ),
            400: OpenApiResponse(description="اطلاعات نامعتبر است")
        }
    )
    def post(self, request, *args, **kwargs):
        serializer = serializers.PymentHistorySerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        user = request.user
        price = serializer.validated_data['price']
        description = serializer.validated_data['description']

        history = HistoryPyment.objects.create(
            user=user,
            price=price,
            description=description
        )
        return Response(serializer.data, status=status.HTTP_201_CREATED)