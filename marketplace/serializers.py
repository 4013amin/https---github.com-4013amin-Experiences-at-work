from rest_framework import serializers
from drf_spectacular.utils import extend_schema, OpenApiExample, OpenApiTypes, extend_schema_field

from marketplace.permissions.counstomer import CustomerPermission
from . import models


class VerndorRegisterSerializer(serializers.ModelSerializer):
    permission_classes = [CustomerPermission]

    class Meta:
        model = models.vendor_request
        fields = ['phone', 'description']
