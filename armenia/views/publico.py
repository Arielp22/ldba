from django.utils import timezone
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.filters import OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend

from armenia.models.temporada import Temporada
from armenia.models.categoria import Categoria
from armenia.models.equipo import Equipo
from armenia.models.jornada import Jornada, Partido
from armenia.serializers.publico import (
    TemporadaPublicaSerializer,
    CategoriaPublicaSerializer,
    EquipoPublicoSerializer,
    JornadaPublicaSerializer,
    PartidoPublicoSerializer,
)
from armenia.pagination import StandardPagination


class TemporadaPublicaViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Temporada.objects.all().order_by("-anio")
    serializer_class = TemporadaPublicaSerializer
    permission_classes = [AllowAny]
    pagination_class = StandardPagination
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ["estado", "anio"]
    ordering = ["-anio"]


class CategoriaPublicaViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Categoria.objects.filter(activa=True).order_by("nombre")
    serializer_class = CategoriaPublicaSerializer
    permission_classes = [AllowAny]
    pagination_class = StandardPagination


class EquipoPublicoViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Equipo.objects.filter(activo=True).order_by("nombre")
    serializer_class = EquipoPublicoSerializer
    permission_classes = [AllowAny]
    pagination_class = StandardPagination
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    ordering = ["nombre"]


class JornadaPublicaViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Jornada.objects.select_related("temporada", "categoria").prefetch_related(
        "partidos__equipo_local",
        "partidos__equipo_visitante",
        "partidos__equipo_vocal",
    ).all()
    serializer_class = JornadaPublicaSerializer
    permission_classes = [AllowAny]
    pagination_class = StandardPagination
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ["temporada", "categoria", "estado", "numero"]
    ordering = ["temporada", "categoria", "numero"]


class PartidoPublicoViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Partido.objects.select_related(
        "jornada", "jornada__temporada", "jornada__categoria",
        "equipo_local", "equipo_visitante", "equipo_vocal",
    ).all()
    serializer_class = PartidoPublicoSerializer
    permission_classes = [AllowAny]
    pagination_class = StandardPagination
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = [
        "jornada", "dia", "estado",
        "equipo_local", "equipo_visitante",
        "jornada__temporada", "jornada__categoria",
    ]
    ordering_fields = ["jornada", "dia", "numero_partido", "hora"]
    ordering = ["jornada", "dia", "numero_partido"]

    @action(detail=False, methods=["get"], url_path="proximos")
    def proximos(self, request):
        """
        Partidos próximos: los que están programados y su jornada
        tiene fecha_sabado >= hoy.
        """
        hoy = timezone.localdate()
        qs = self.get_queryset().filter(
            estado="programado",
            jornada__fecha_sabado__gte=hoy,
        ).order_by("jornada__fecha_sabado", "dia", "numero_partido")[:20]

        serializer = self.get_serializer(qs, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=["get"], url_path="recientes")
    def recientes(self, request):
        """
        Últimos resultados: partidos finalizados, ordenados por jornada desc.
        """
        qs = self.get_queryset().filter(
            estado="finalizado",
        ).order_by("-jornada__fecha_sabado", "-dia", "-numero_partido")[:20]

        serializer = self.get_serializer(qs, many=True)
        return Response(serializer.data)