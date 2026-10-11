from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend

from armenia.models.sancion import (
    Sancion, HistorialSancion, Multa, Recibo,
)
from armenia.serializers.sancion import (
    SancionSerializer,
    SancionCambioEstadoSerializer,
    HistorialSancionSerializer,
    MultaSerializer,
    ReciboSerializer,
)
from armenia.permissions import IsComisionPenasOrReadOnly
from armenia.pagination import StandardPagination


class SancionViewSet(viewsets.ModelViewSet):
    queryset = Sancion.objects.select_related(
        "jugador", "equipo", "partido", "vocalia"
    ).all()
    serializer_class = SancionSerializer
    permission_classes = [IsComisionPenasOrReadOnly]
    pagination_class = StandardPagination
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ["tipo", "estado", "jugador", "equipo", "partido"]
    search_fields = ["motivo", "articulo", "jugador__nombres", "equipo__nombre"]
    ordering_fields = ["fecha_inicio", "created_at"]
    ordering = ["-created_at"]

    @action(detail=True, methods=["post"], url_path="cambiar-estado")
    def cambiar_estado(self, request, pk=None):
        sancion = self.get_object()
        serializer = SancionCambioEstadoSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        estado_anterior = sancion.estado
        sancion.estado = serializer.validated_data["estado"]
        sancion.save()

        HistorialSancion.objects.create(
            sancion=sancion,
            estado_anterior=estado_anterior,
            estado_nuevo=sancion.estado,
            motivo_cambio=serializer.validated_data.get("motivo_cambio"),
            usuario=request.user if request.user.is_authenticated else None,
        )
        return Response(SancionSerializer(sancion).data)


class HistorialSancionViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = HistorialSancion.objects.select_related("sancion", "usuario").all()
    serializer_class = HistorialSancionSerializer
    permission_classes = [IsComisionPenasOrReadOnly]
    pagination_class = StandardPagination
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ["sancion", "estado_nuevo", "estado_anterior"]
    ordering_fields = ["created_at"]
    ordering = ["-created_at"]


class MultaViewSet(viewsets.ModelViewSet):
    queryset = Multa.objects.select_related("sancion", "equipo").all()
    serializer_class = MultaSerializer
    permission_classes = [IsComisionPenasOrReadOnly]
    pagination_class = StandardPagination
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ["estado", "equipo", "sancion", "forma_pago"]
    search_fields = ["motivo", "equipo__nombre"]
    ordering_fields = ["monto", "fecha_pago", "created_at"]
    ordering = ["-created_at"]

    @action(detail=True, methods=["post"], url_path="marcar-pagada")
    def marcar_pagada(self, request, pk=None):
        multa = self.get_object()
        fecha_pago = request.data.get("fecha_pago")
        forma_pago = request.data.get("forma_pago")

        if not fecha_pago or not forma_pago:
            return Response(
                {"detail": "Se requieren 'fecha_pago' y 'forma_pago'."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        multa.estado = "pagada"
        multa.fecha_pago = fecha_pago
        multa.forma_pago = forma_pago
        multa.save()
        return Response(MultaSerializer(multa).data)


class ReciboViewSet(viewsets.ModelViewSet):
    queryset = Recibo.objects.select_related("multa").all()
    serializer_class = ReciboSerializer
    permission_classes = [IsComisionPenasOrReadOnly]
    pagination_class = StandardPagination
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ["multa"]
    search_fields = ["numero", "entregado_a", "entregado_por"]
    ordering_fields = ["fecha_entrega", "created_at"]
    ordering = ["-created_at"]