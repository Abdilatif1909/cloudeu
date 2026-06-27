from rest_framework.permissions import SAFE_METHODS, BasePermission


class IsSuperAdmin(BasePermission):
    def has_permission(self, request, view) -> bool:
        return bool(request.user and request.user.is_authenticated and request.user.is_super_admin)


class IsTeacherOrSuperAdmin(BasePermission):
    def has_permission(self, request, view) -> bool:
        user = request.user
        return bool(user and user.is_authenticated and (user.is_teacher or user.is_super_admin))


class ReadOnlyOrTeacher(BasePermission):
    def has_permission(self, request, view) -> bool:
        if request.method in SAFE_METHODS:
            return True
        user = request.user
        return bool(user and user.is_authenticated and (user.is_teacher or user.is_super_admin))


class IsOwnerTeacherOrSuperAdmin(BasePermission):
    def has_object_permission(self, request, view, obj) -> bool:
        user = request.user
        if not user or not user.is_authenticated:
            return False
        if user.is_teacher or user.is_super_admin:
            return True
        owner = getattr(obj, "student", None)
        return owner == user
