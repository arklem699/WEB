from rest_framework import permissions
from bmstu_lab.models import CustomUser
from django.conf import settings
import redis


session_storage = redis.StrictRedis(host=settings.REDIS_HOST, port=settings.REDIS_PORT)

class IsManager(permissions.BasePermission):
    def has_permission(self, request, view):
        ssid = request.COOKIES.get("session_id")

        if ssid is not None:
            user_id = session_storage.get(ssid)

        if user_id is not None:
            user = CustomUser.objects.get(id=user_id)

        return bool(user and (user.is_staff or user.is_superuser))


class IsAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        ssid = request.COOKIES.get("session_id")

        if ssid is not None:
            user_id = session_storage.get(ssid)

        if user_id is not None:
            user = CustomUser.objects.get(id=user_id)
            
        return bool(user and user.is_superuser)