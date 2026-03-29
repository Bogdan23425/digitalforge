from rest_framework.permissions import BasePermission


class IsSellerOrAdmin(BasePermission):
    message = "Seller or admin access is required."

    def has_permission(self, request, view):
        user = request.user
        return bool(
            user
            and user.is_authenticated
            and (user.is_seller or user.is_admin or user.is_superuser)
        )


class IsProductOwnerOrAdmin(BasePermission):
    message = "You can access only your own products."

    def has_object_permission(self, request, view, obj):
        user = request.user
        return bool(
            user
            and user.is_authenticated
            and (obj.seller_id == user.id or user.is_admin or user.is_superuser)
        )
