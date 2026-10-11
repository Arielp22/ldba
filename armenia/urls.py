# armenia/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView, TokenVerifyView

from armenia.views.auth       import RegisterView, LogoutView
from armenia.views.user       import UserViewSet
from armenia.views.temporada  import TemporadaViewSet
from armenia.views.categoria  import CategoriaViewSet
from armenia.serializers.auth import CustomTokenView

router = DefaultRouter()
router.register("users",       UserViewSet,       basename="user")
router.register("temporadas",  TemporadaViewSet,  basename="temporada")
router.register("categorias",  CategoriaViewSet,  basename="categoria")

urlpatterns = [
    path("auth/register/",      RegisterView.as_view()),
    path("auth/login/",         CustomTokenView.as_view()),
    path("auth/token/refresh/", TokenRefreshView.as_view()),
    path("auth/token/verify/",  TokenVerifyView.as_view()),
    path("auth/logout/",        LogoutView.as_view()),
    path("", include(router.urls)),
]