from rest_framework import serializers

from armenia.models.administracion import (
    Sesion, SesionParticipante, Documento, Noticia,
)


class SesionParticipanteSerializer(serializers.ModelSerializer):
    class Meta:
        model = SesionParticipante
        fields = [
            "id", "sesion", "nombre", "cargo", "presente",
            "observaciones", "created_at",
        ]
        read_only_fields = ["id", "created_at"]


class SesionSerializer(serializers.ModelSerializer):
    tipo_display = serializers.CharField(source="get_tipo_display", read_only=True)
    estado_display = serializers.CharField(source="get_estado_display", read_only=True)
    participantes_count = serializers.IntegerField(
        source="participantes.count", read_only=True
    )

    class Meta:
        model = Sesion
        fields = [
            "id",
            "fecha", "tipo", "tipo_display",
            "orden_del_dia", "acta",
            "estado", "estado_display",
            "observaciones",
            "participantes_count",
            "created_at", "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class DocumentoSerializer(serializers.ModelSerializer):
    tipo_display = serializers.CharField(source="get_tipo_display", read_only=True)
    jugador_nombre = serializers.CharField(source="jugador.nombre_completo", read_only=True)
    equipo_nombre = serializers.CharField(source="equipo.nombre", read_only=True)

    class Meta:
        model = Documento
        fields = [
            "id",
            "tipo", "tipo_display",
            "titulo", "descripcion",
            "archivo", "mime_type", "tamano_bytes",
            "jugador", "jugador_nombre",
            "equipo", "equipo_nombre",
            "sesion",
            "created_at", "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class NoticiaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Noticia
        fields = [
            "id",
            "titulo", "resumen", "contenido", "imagen",
            "autor", "publicada", "destacada", "fecha_publicacion",
            "created_at", "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class NoticiaPublicaSerializer(serializers.ModelSerializer):
    """Vista pública: solo noticias publicadas, sin campos internos."""
    class Meta:
        model = Noticia
        fields = [
            "id", "titulo", "resumen", "contenido", "imagen",
            "autor", "destacada", "fecha_publicacion",
        ]