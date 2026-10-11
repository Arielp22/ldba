from rest_framework import viewsets
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend

from armenia.models import Categoria
from armenia.serializers import CategoriaSerializer
from armenia.permissions import IsComisionTecnicaOrReadOnly
from armenia.pagination import StandardPagination


class CategoriaViewSet(viewsets.ModelViewSet):
    queryset = Categoria.objects.all()
    serializer_class = CategoriaSerializer
    permission_classes = [IsComisionTecnicaOrReadOnly]
    pagination_class = StandardPagination
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ["activa"]
    search_fields = ["nombre"]
    ordering_fields = ["nombre", "created_at"]
    ordering = ["nombre"]