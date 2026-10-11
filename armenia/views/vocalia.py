from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend

from armenia.models.vocalia import Vocalia, VocaliaJugador
from armenia.serializers.vocalia import (
    VocaliaSerializer,
    VocaliaJugadorSerializer,
    VocaliaRechazoSerializer,
)
from armenia.permissions import IsComisionTecnicaOrReadOnly
from armenia.pagination import StandardPagination


class VocaliaViewSet(viewsets.ModelViewSet):
    queryset = Vocalia.objects.select_related(
        "partido",
        "partido__jornada",
        "partido__equipo_local",
        "partido__equipo_visitante",
    ).all()
    serializer_class = VocaliaSerializer
    permission_classes = [IsComisionTecnicaOrReadOnly]
    pagination_class = StandardPagination
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ["estado", "partido"]
    search_fields = ["arbitro", "vocal"]
    ordering_fields = ["created_at", "estado"]
    ordering = ["-created_at"]

    @action(detail=True, methods=["post"], url_path="aprobar")
    def aprobar(self, request, pk=None):
        vocalia = self.get_object()
        if vocalia.estado == "aprobada":
            return Response(
                {"detail": "La vocalía ya está aprobada."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        vocalia.estado = "aprobada"
        vocalia.observaciones_rechazo = None
        vocalia.save()
        return Response(VocaliaSerializer(vocalia).data)

    @action(detail=True, methods=["post"], url_path="rechazar")
    def rechazar(self, request, pk=None):
        vocalia = self.get_object()
        serializer = VocaliaRechazoSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        vocalia.estado = "rechazada"
        vocalia.observaciones_rechazo = serializer.validated_data["observaciones_rechazo"]
        vocalia.save()
        return Response(VocaliaSerializer(vocalia).data)

    @action(detail=True, methods=["post"], url_path="sincronizar-resultado")
    def sincronizar_resultado(self, request, pk=None):
        vocalia = self.get_object()
        if not vocalia.partido:
            return Response(
                {"detail": "La vocalía no tiene partido asociado."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if vocalia.goles_local is None or vocalia.goles_visitante is None:
            return Response(
                {"detail": "La vocalía no tiene resultado registrado."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        partido = vocalia.partido
        partido.goles_local = vocalia.goles_local
        partido.goles_visitante = vocalia.goles_visitante
        partido.estado = "finalizado"
        partido.save()

        return Response(VocaliaSerializer(vocalia).data)


class VocaliaJugadorViewSet(viewsets.ModelViewSet):
    queryset = VocaliaJugador.objects.select_related(
        "vocalia", "jugador", "equipo"
    ).all()
    serializer_class = VocaliaJugadorSerializer
    permission_classes = [IsComisionTecnicaOrReadOnly]
    pagination_class = StandardPagination
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ["vocalia", "jugador", "equipo"]
    search_fields = ["jugador__nombres", "jugador__apellidos", "equipo__nombre"]
    ordering_fields = ["created_at"]
    ordering = ["-created_at"]