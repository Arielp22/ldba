from rest_framework import serializers

from armenia.models.temporada import Temporada
from armenia.models.categoria import Categoria
from armenia.models.equipo import Equipo
from armenia.models.jornada import Jornada, Partido


class TemporadaPublicaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Temporada
        fields = ["id", "nombre", "anio", "fecha_inicio", "fecha_fin", "estado"]


class CategoriaPublicaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Categoria
        fields = ["id", "nombre", "descripcion"]


class EquipoPublicoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Equipo
        fields = ["id", "nombre", "siglas", "color_principal", "logo"]


class PartidoPublicoSerializer(serializers.ModelSerializer):
    jornada_numero = serializers.IntegerField(source="jornada.numero", read_only=True)
    temporada = serializers.IntegerField(source="jornada.temporada.id", read_only=True)
    temporada_nombre = serializers.CharField(source="jornada.temporada.nombre", read_only=True)
    categoria = serializers.IntegerField(source="jornada.categoria.id", read_only=True)
    categoria_nombre = serializers.CharField(source="jornada.categoria.nombre", read_only=True)

    equipo_local = EquipoPublicoSerializer(read_only=True)
    equipo_visitante = EquipoPublicoSerializer(read_only=True)
    equipo_vocal = EquipoPublicoSerializer(read_only=True)

    dia_display = serializers.CharField(source="get_dia_display", read_only=True)
    estado_display = serializers.CharField(source="get_estado_display", read_only=True)

    class Meta:
        model = Partido
        fields = [
            "id",
            "jornada", "jornada_numero",
            "temporada", "temporada_nombre",
            "categoria", "categoria_nombre",
            "dia", "dia_display",
            "numero_partido", "hora",
            "equipo_local", "equipo_visitante", "equipo_vocal",
            "goles_local", "goles_visitante",
            "estado", "estado_display",
        ]


class JornadaPublicaSerializer(serializers.ModelSerializer):
    temporada_nombre = serializers.CharField(source="temporada.nombre", read_only=True)
    categoria_nombre = serializers.CharField(source="categoria.nombre", read_only=True)
    partidos = PartidoPublicoSerializer(many=True, read_only=True)

    class Meta:
        model = Jornada
        fields = [
            "id", "numero",
            "temporada", "temporada_nombre",
            "categoria", "categoria_nombre",
            "fecha_sabado", "fecha_domingo",
            "estado",
            "partidos",
        ]