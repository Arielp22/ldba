from django.contrib.auth.models import User
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend

from armenia.models.equipo import Equipo, EquipoTemporadaCategoria
from armenia.serializers.equipo import (
    EquipoSerializer,
    EquipoCreateSerializer,
    EquipoUpdateSerializer,
    EquipoTemporadaCategoriaSerializer,
    ResetPasswordEquipoSerializer,
)
from armenia.permissions import IsSuperadminOrReadOnly, IsSuperadmin
from armenia.pagination import StandardPagination


class EquipoViewSet(viewsets.ModelViewSet):
    queryset = Equipo.objects.select_related("user").all()
    permission_classes = [IsSuperadminOrReadOnly]
    pagination_class = StandardPagination
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ["activo"]
    search_fields = ["nombre", "siglas", "presidente", "user__username"]
    ordering_fields = ["nombre", "created_at"]
    ordering = ["nombre"]

    def get_serializer_class(self):
        if self.action == "create":
            return EquipoCreateSerializer
        if self.action in ("update", "partial_update"):
            return EquipoUpdateSerializer
        return EquipoSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        equipo = serializer.save()
        return Response(
            EquipoSerializer(equipo).data,
            status=status.HTTP_201_CREATED,
        )

    @action(
        detail=True,
        methods=["post"],
        permission_classes=[IsSuperadmin],
        url_path="reset-password",
    )
    def reset_password(self, request, pk=None):
        """Solo Superadmin. Cambio de presidente = cambio de contraseña."""
        equipo = self.get_object()
        serializer = ResetPasswordEquipoSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        equipo.user.set_password(serializer.validated_data["new_password"])
        equipo.user.save()
        return Response({"message": "Contraseña actualizada."})


class EquipoTemporadaCategoriaViewSet(viewsets.ModelViewSet):
    queryset = EquipoTemporadaCategoria.objects.select_related(
        "equipo", "temporada", "categoria"
    ).all()
    serializer_class = EquipoTemporadaCategoriaSerializer
    permission_classes = [IsSuperadminOrReadOnly]
    pagination_class = StandardPagination
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ["temporada", "categoria", "equipo", "activo"]
    search_fields = ["equipo__nombre", "temporada__nombre", "categoria__nombre"]
    ordering_fields = ["created_at"]
    ordering = ["-created_at"]