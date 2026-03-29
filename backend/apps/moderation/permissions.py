from rest_framework.permissions import BasePermission


class IsModeratorOrAdmin(BasePermission):
    message = "Moderator or admin access is required."

    def has_permission(self, request, view):
        user = request.user
        return bool(
            user
            and user.is_authenticated
            and (user.is_moderator or user.is_admin or user.is_superuser)
        )
