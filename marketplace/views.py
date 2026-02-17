from django.contrib import messages
from rest_framework import status
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from marketplace.permissions.counstomer import CustomerPermission
from marketplace.serializers import VerndorRegisterSerializer
from . import models
from .models import Vendor_Profile, vendor_request
from drf_spectacular.utils import extend_schema, OpenApiExample, OpenApiResponse


# Create your views here.

class VendorRequstAPIView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        summary="افزودن دیتا تستی است",
        request=VerndorRegisterSerializer,
        responses={
            201: OpenApiResponse(
                response=VerndorRegisterSerializer,
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
        serializer = VerndorRegisterSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        user = request.user
        phone = serializer.validated_data['phone']
        description = serializer.validated_data['description']
        vendor = vendor_request.objects.create(
            phone=phone,
            description=description,
        )
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def get(self, request, *args, **kwargs):
        vendorre = vendor_request.objects.all()
        serializer = VerndorRegisterSerializer(vendorre)
        return Response(serializer.data, status=status.HTTP_200_OK)