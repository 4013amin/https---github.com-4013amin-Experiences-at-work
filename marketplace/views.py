from django.contrib import messages
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from marketplace.permissions.counstomer import CustomerPermission
from marketplace.serializers import RegisterSerializer
from . import models


# Create your views here.

class Register(APIView):
    permission_classes = [CustomerPermission]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        name = serializer.validated_data['name']
        phone = serializer.validated_data['phone']

        models.Profile.objects.create(name=name, phone=phone)
        serializer.save()
        messages.success(request, 'Profile created successfully')
        return Response(serializer.data, status=status.HTTP_201_CREATED)
