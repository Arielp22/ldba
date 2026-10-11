from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend

from armenia.models.lesion import Lesion
from armenia.serializers.lesion import (
    LesionSerializer,
    LesionCambioEstadoSerializer,
)
from armenia.permissions import IsComisionSeguroOrReadOnly
from armenia.pagination import StandardPagination


class LesionViewSet(viewsets.ModelViewSet):
    queryset = Lesion.objects.select_related(
        "jugador", "equipo", "partido", "vocalia"
    ).all()
    serializer_class = LesionSerializer
    permission_classes = [IsComisionSeguroOrReadOnly]
    pagination_class = StandardPagination
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ["estado", "gravedad", "tipo", "jugador", "equipo", "fecha"]
    search_fields = ["jugador__nombres", "jugador__apellidos", "descripcion"]
    ordering_fields = ["fecha", "gravedad", "created_at"]
    ordering = ["-fecha", "-created_at"]

    @action(detail=True, methods=["post"], url_path="cambiar-estado")
    def cambiar_estado(self, request, pk=None):
        lesion = self.get_object()
        serializer = LesionCambioEstadoSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        lesion.estado = serializer.validated_data["estado"]
        if "monto_apoyo" in serializer.validated_data:
            lesion.monto_apoyo = serializer.validated_data["monto_apoyo"]
        if "observaciones" in serializer.validated_data:
            lesion.observaciones = serializer.validated_data["observaciones"]
        lesion.save()
        return Response(LesionSerializer(lesion).data)