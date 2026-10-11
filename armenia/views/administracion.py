from django.utils import timezone
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend

from armenia.models.administracion import (
    Sesion, SesionParticipante, Documento, Noticia,
)
from armenia.serializers.administracion import (
    SesionSerializer,
    SesionParticipanteSerializer,
    DocumentoSerializer,
    NoticiaSerializer,
    NoticiaPublicaSerializer,
)
from armenia.permissions import (
    IsComisionAdministrativaOrReadOnly,
    IsComisionAdministrativa,
)
from armenia.pagination import StandardPagination


class SesionViewSet(viewsets.ModelViewSet):
    queryset = Sesion.objects.all()
    serializer_class = SesionSerializer
    permission_classes = [IsComisionAdministrativaOrReadOnly]
    pagination_class = StandardPagination
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ["tipo", "estado", "fecha"]
    search_fields = ["orden_del_dia", "acta", "observaciones"]
    ordering_fields = ["fecha", "created_at"]
    ordering = ["-fecha"]

    @action(detail=True, methods=["post"], url_path="finalizar")
    def finalizar(self, request, pk=None):
        sesion = self.get_object()
        sesion.estado = "finalizada"
        sesion.save()
        return Response(SesionSerializer(sesion).data)


class SesionParticipanteViewSet(viewsets.ModelViewSet):
    queryset = SesionParticipante.objects.select_related("sesion").all()
    serializer_class = SesionParticipanteSerializer
    permission_classes = [IsComisionAdministrativaOrReadOnly]
    pagination_class = StandardPagination
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ["sesion", "presente"]
    search_fields = ["nombre", "cargo"]
    ordering_fields = ["nombre", "created_at"]
    ordering = ["nombre"]


class DocumentoViewSet(viewsets.ModelViewSet):
    queryset = Documento.objects.select_related("jugador", "equipo", "sesion").all()
    serializer_class = DocumentoSerializer
    permission_classes = [IsComisionAdministrativaOrReadOnly]
    pagination_class = StandardPagination
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ["tipo", "jugador", "equipo", "sesion"]
    search_fields = ["titulo", "descripcion"]
    ordering_fields = ["created_at", "titulo"]
    ordering = ["-created_at"]


class NoticiaViewSet(viewsets.ModelViewSet):
    queryset = Noticia.objects.all()
    serializer_class = NoticiaSerializer
    permission_classes = [IsComisionAdministrativaOrReadOnly]
    pagination_class = StandardPagination
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ["publicada", "destacada"]
    search_fields = ["titulo", "resumen", "contenido"]
    ordering_fields = ["fecha_publicacion", "created_at"]
    ordering = ["-created_at"]

    @action(detail=True, methods=["post"], url_path="publicar",
            permission_classes=[IsComisionAdministrativa])
    def publicar(self, request, pk=None):
        noticia = self.get_object()
        noticia.publicada = True
        if not noticia.fecha_publicacion:
            noticia.fecha_publicacion = timezone.now()
        noticia.save()
        return Response(NoticiaSerializer(noticia).data)

    @action(detail=True, methods=["post"], url_path="despublicar",
            permission_classes=[IsComisionAdministrativa])
    def despublicar(self, request, pk=None):
        noticia = self.get_object()
        noticia.publicada = False
        noticia.save()
        return Response(NoticiaSerializer(noticia).data)


class NoticiaPublicaViewSet(viewsets.ReadOnlyModelViewSet):
    """Endpoints públicos (sin login) para la vista pública."""
    queryset = Noticia.objects.filter(publicada=True).order_by(
        "-destacada", "-fecha_publicacion"
    )
    serializer_class = NoticiaPublicaSerializer
    permission_classes = [AllowAny]
    pagination_class = StandardPagination
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ["destacada"]
    ordering = ["-destacada", "-fecha_publicacion"]