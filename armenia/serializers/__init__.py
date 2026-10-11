# armenia/serializers/__init__.py
from .auth import CustomTokenSerializer, CustomTokenView
from .user import (
    RegisterSerializer,
    UserSerializer,
    UserProfileSerializer,
    ChangePasswordSerializer,
)

# Bloque 1: Configuración base
from .temporada import TemporadaSerializer
from .categoria import CategoriaSerializer

__all__ = [
    # Auth
    "CustomTokenSerializer",
    "CustomTokenView",
    # User
    "RegisterSerializer",
    "UserSerializer",
    "UserProfileSerializer",
    "ChangePasswordSerializer",
    # Configuración base
    "TemporadaSerializer",
    "CategoriaSerializer",
]