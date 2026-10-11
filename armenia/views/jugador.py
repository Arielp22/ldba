from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend

from armenia.models.jugador import (
    Jugador,
    JugadorEquipoTemporada,
    CapitanEquipoTemporada,
)
from armenia.serializers.jugador import (
    JugadorSerializer,
    JugadorCalificacionSerializer,
    JugadorEquipoTemporadaSerializer,
    JugadorEquipoTemporadaCreateSerializer,
    CapitanEquipoTemporadaSerializer,
)
from armenia.permissions import IsCalificacionesOrReadOnly, IsCalificaciones
from armenia.pagination import StandardPagination


class JugadorViewSet(viewsets.ModelViewSet):
    queryset = Jugador.objects.all()
    serializer_class = JugadorSerializer
    permission_classes = [IsCalificacionesOrReadOnly]
    pagination_class = StandardPagination
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ["estado_calificacion", "activo"]
    search_fields = ["nombres", "apellidos", "cedula", "numero_carnet"]
    ordering_fields = ["apellidos", "nombres", "fecha_nacimiento", "created_at"]
    ordering = ["apellidos", "nombres"]

    @action(
        detail=True,
        methods=["post"],
        permission_classes=[IsCalificaciones],
        url_path="calificar",
    )
    def calificar(self, request, pk=None):
        """Cambia el estado de calificación del jugador."""
        jugador = self.get_object()
        serializer = JugadorCalificacionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        jugador.estado_calificacion = serializer.validated_data["estado_calificacion"]
        if "observaciones" in serializer.validated_data:
            jugador.observaciones = serializer.validated_data["observaciones"]
        jugador.save()
        return Response(JugadorSerializer(jugador).data)


class JugadorEquipoTemporadaViewSet(viewsets.ModelViewSet):
    queryset = JugadorEquipoTemporada.objects.select_related(
        "jugador", "equipo", "temporada", "categoria"
    ).all()
    permission_classes = [IsCalificacionesOrReadOnly]
    pagination_class = StandardPagination
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ["temporada", "categoria", "equipo", "jugador", "activo"]
    search_fields = ["jugador__nombres", "jugador__apellidos", "jugador__cedula"]
    ordering_fields = ["created_at", "dorsal"]
    ordering = ["-created_at"]

    def get_serializer_class(self):
        if self.action == "create":
            return JugadorEquipoTemporadaCreateSerializer
        return JugadorEquipoTemporadaSerializer


class CapitanEquipoTemporadaViewSet(viewsets.ModelViewSet):
    queryset = CapitanEquipoTemporada.objects.select_related(
        "equipo", "jugador", "temporada", "categoria"
    ).all()
    serializer_class = CapitanEquipoTemporadaSerializer
    permission_classes = [IsCalificacionesOrReadOnly]
    pagination_class = StandardPagination
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ["temporada", "categoria", "equipo", "jugador", "activo"]
    search_fields = ["jugador__nombres", "jugador__apellidos", "equipo__nombre"]
    ordering_fields = ["created_at"]
    ordering = ["-created_at"]