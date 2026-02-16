from rest_framework.permissions import BasePermission


class Is_admin(BasePermission):
    def has_permission(self, request, view):
        return request.user.role == "admin"
