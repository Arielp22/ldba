from rest_framework import viewsets
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend

from armenia.models import Temporada
from armenia.serializers import TemporadaSerializer
from armenia.permissions import IsComisionTecnicaOrReadOnly
from armenia.pagination import StandardPagination


class TemporadaViewSet(viewsets.ModelViewSet):
    queryset = Temporada.objects.all()
    serializer_class = TemporadaSerializer
    permission_classes = [IsComisionTecnicaOrReadOnly]
    pagination_class = StandardPagination
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ["estado", "anio"]
    search_fields = ["nombre"]
    ordering_fields = ["anio", "fecha_inicio", "fecha_fin", "created_at"]
    ordering = ["-anio"]