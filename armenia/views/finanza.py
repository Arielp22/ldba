from rest_framework import viewsets
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Sum

from armenia.models.finanza import MovimientoFinanciero, InformeFinancieroSemanal
from armenia.serializers.finanza import (
    MovimientoFinancieroSerializer,
    InformeFinancieroSemanalSerializer,
)
from armenia.permissions import IsComisionFinancieraOrReadOnly
from armenia.pagination import StandardPagination

from rest_framework.decorators import action
from rest_framework.response import Response


class MovimientoFinancieroViewSet(viewsets.ModelViewSet):
    queryset = MovimientoFinanciero.objects.all()
    serializer_class = MovimientoFinancieroSerializer
    permission_classes = [IsComisionFinancieraOrReadOnly]
    pagination_class = StandardPagination
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ["tipo", "fecha", "responsable"]
    search_fields = ["concepto", "responsable", "observaciones"]
    ordering_fields = ["fecha", "valor", "created_at"]
    ordering = ["-fecha"]

    @action(detail=False, methods=["get"], url_path="resumen")
    def resumen(self, request):
        """Totales de ingresos, egresos y balance (con filtros opcionales)."""
        qs = self.filter_queryset(self.get_queryset())
        total_ingresos = qs.filter(tipo="ingreso").aggregate(
            total=Sum("valor"))["total"] or 0
        total_egresos = qs.filter(tipo="egreso").aggregate(
            total=Sum("valor"))["total"] or 0
        return Response({
            "total_ingresos": total_ingresos,
            "total_egresos": total_egresos,
            "balance": total_ingresos - total_egresos,
            "cantidad_movimientos": qs.count(),
        })


class InformeFinancieroSemanalViewSet(viewsets.ModelViewSet):
    queryset = InformeFinancieroSemanal.objects.all()
    serializer_class = InformeFinancieroSemanalSerializer
    permission_classes = [IsComisionFinancieraOrReadOnly]
    pagination_class = StandardPagination
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ["estado", "anio", "numero_semana"]
    search_fields = ["observaciones"]
    ordering_fields = ["anio", "numero_semana", "fecha_semana", "created_at"]
    ordering = ["-anio", "-numero_semana"]