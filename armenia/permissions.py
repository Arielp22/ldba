from rest_framework.permissions import BasePermission, SAFE_METHODS


def _in_group(user, group_name):
    return user.is_authenticated and user.groups.filter(name=group_name).exists()


class IsSuperadmin(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and (
            request.user.is_superuser or _in_group(request.user, "Superadmin")
        )


class IsComisionTecnicaOrReadOnly(BasePermission):
    """
    - Lectura: cualquier usuario autenticado.
    - Escritura: solo superuser, grupo 'Superadmin' o grupo 'Comision Tecnica'.
    """

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        if request.method in SAFE_METHODS:
            return True
        return request.user.is_superuser or _in_group(request.user, "Comision Tecnica")


class IsSuperadminOrReadOnly(BasePermission):
    """
    Lectura: cualquier usuario autenticado.
    Escritura: solo Superadmin o superuser.
    """
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        if request.method in SAFE_METHODS:
            return True
        return request.user.is_superuser or _in_group(request.user, "Superadmin")

class IsCalificaciones(BasePermission):
    """Solo Comisión Calificaciones o Superadmin."""
    def has_permission(self, request, view):
        return request.user.is_authenticated and (
            request.user.is_superuser or _in_group(request.user, "Comision Calificaciones")
        )


class IsCalificacionesOrReadOnly(BasePermission):
    """Lectura autenticada; escritura solo Calificaciones o Superadmin."""
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        if request.method in SAFE_METHODS:
            return True
        return request.user.is_superuser or _in_group(request.user, "Comision Calificaciones")

class IsComisionPenas(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and (
            request.user.is_superuser or _in_group(request.user, "Comision Penas")
        )


class IsComisionPenasOrReadOnly(BasePermission):
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        if request.method in SAFE_METHODS:
            return True
        return request.user.is_superuser or _in_group(request.user, "Comision Penas")

class IsComisionFinanciera(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and (
            request.user.is_superuser or _in_group(request.user, "Comision Financiera")
        )


class IsComisionFinancieraOrReadOnly(BasePermission):
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        if request.method in SAFE_METHODS:
            return True
        return request.user.is_superuser or _in_group(request.user, "Comision Financiera")

class IsComisionSeguro(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and (
            request.user.is_superuser or _in_group(request.user, "Comision Seguro")
        )


class IsComisionSeguroOrReadOnly(BasePermission):
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        if request.method in SAFE_METHODS:
            return True
        return request.user.is_superuser or _in_group(request.user, "Comision Seguro")

