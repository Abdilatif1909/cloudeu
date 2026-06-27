from django.conf import settings
from django.core.cache import cache
from drf_spectacular.utils import extend_schema, inline_serializer
from rest_framework import generics, permissions, serializers, status
from rest_framework.exceptions import APIException
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView

from apps.common.models import AuditLog
from apps.common.services import AuditLogService

from .serializers import ChangePasswordSerializer, CustomTokenObtainPairSerializer, LogoutSerializer, UserSerializer


class LoginView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer
    throttle_scope = "login"

    def _lock_key(self, request):
        username = request.data.get("username", "")
        ip_address = request.META.get("HTTP_X_FORWARDED_FOR", request.META.get("REMOTE_ADDR", "")).split(",")[0].strip()
        return f"login-lock:{username}:{ip_address}"

    def post(self, request, *args, **kwargs):
        lock_key = self._lock_key(request)
        max_attempts = int(getattr(settings, "LOGIN_LOCKOUT_ATTEMPTS", 5))
        if cache.get(lock_key, 0) >= max_attempts:
            return Response({"detail": "Too many failed login attempts. Try again later."}, status=status.HTTP_429_TOO_MANY_REQUESTS)
        try:
            response = super().post(request, *args, **kwargs)
        except APIException:
            cache.set(lock_key, cache.get(lock_key, 0) + 1, int(getattr(settings, "LOGIN_LOCKOUT_SECONDS", 900)))
            raise
        if response.status_code == 200:
            cache.delete(lock_key)
            AuditLogService.record(request, AuditLog.Action.LOGIN, target="auth.login", metadata={"username": request.data.get("username")})
        else:
            cache.set(lock_key, cache.get(lock_key, 0) + 1, int(getattr(settings, "LOGIN_LOCKOUT_SECONDS", 900)))
        return response


class ProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user


class ChangePasswordView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(
        request=ChangePasswordSerializer,
        responses={200: inline_serializer("ChangePasswordResponse", {"detail": serializers.CharField()})},
    )
    def post(self, request):
        serializer = ChangePasswordSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        request.user.set_password(serializer.validated_data["new_password"])
        request.user.save(update_fields=["password"])
        return Response({"detail": "Password changed successfully."})


class LogoutView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(request=LogoutSerializer, responses={204: None})
    def post(self, request):
        serializer = LogoutSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        token = RefreshToken(serializer.validated_data["refresh"])
        token.blacklist()
        return Response(status=status.HTTP_204_NO_CONTENT)
