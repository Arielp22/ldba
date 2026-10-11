# armenia/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView, TokenVerifyView

from armenia.serializers.auth import CustomTokenView
from armenia.views.auth       import RegisterView, LogoutView
from armenia.views.user       import UserViewSet
from armenia.views.temporada  import TemporadaViewSet
from armenia.views.categoria  import CategoriaViewSet
from armenia.views.equipo import EquipoViewSet, EquipoTemporadaCategoriaViewSet
from armenia.views.jugador import (JugadorViewSet, JugadorEquipoTemporadaViewSet, CapitanEquipoTemporadaViewSet,)
from armenia.views.jornada import JornadaViewSet, PartidoViewSet
from armenia.views.vocalia import VocaliaViewSet, VocaliaJugadorViewSet
from armenia.views.sancion import (SancionViewSet,HistorialSancionViewSet,MultaViewSet,ReciboViewSet,)




router = DefaultRouter()
router.register("users",       UserViewSet,       basename="user")
router.register("temporadas",  TemporadaViewSet,  basename="temporada")
router.register("categorias",  CategoriaViewSet,  basename="categoria")
router.register("equipos", EquipoViewSet, basename="equipo")
router.register("equipos-temporada-categoria", EquipoTemporadaCategoriaViewSet, basename="equipo-temporada-categoria")
router.register("jugadores", JugadorViewSet, basename="jugador")
router.register("jugadores-equipo-temporada", JugadorEquipoTemporadaViewSet, basename="jugador-equipo-temporada")
router.register("capitanes-equipo-temporada", CapitanEquipoTemporadaViewSet, basename="capitan-equipo-temporada")
router.register("jornadas", JornadaViewSet, basename="jornada")
router.register("partidos",  PartidoViewSet, basename="partido")
router.register("vocalias",          VocaliaViewSet,        basename="vocalia")
router.register("vocalia-jugadores", VocaliaJugadorViewSet, basename="vocalia-jugador")
router.register("sanciones", SancionViewSet, basename="sancion")
router.register("historial-sanciones", HistorialSancionViewSet, basename="historial-sancion")
router.register("multas", MultaViewSet, basename="multa")
router.register("recibos", ReciboViewSet, basename="recibo")





urlpatterns = [
    path("auth/register/",      RegisterView.as_view()),
    path("auth/login/",         CustomTokenView.as_view()),
    path("auth/token/refresh/", TokenRefreshView.as_view()),
    path("auth/token/verify/",  TokenVerifyView.as_view()),
    path("auth/logout/",        LogoutView.as_view()),
    path("", include(router.urls)),
]