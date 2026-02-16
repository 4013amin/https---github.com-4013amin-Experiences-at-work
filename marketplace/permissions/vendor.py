from rest_framework.permissions import BasePermission


class VendorPermission(BasePermission):
    def has_permission(self, request, view):
        return request.user.role == 'Vendor'
