from rest_framework import serializers
from armenia.models.jugador import (
    Jugador,
    JugadorEquipoTemporada,
    CapitanEquipoTemporada,
)


# ─────────────────────────────────────────────
# Jugador
# ─────────────────────────────────────────────
class JugadorSerializer(serializers.ModelSerializer):
    nombre_completo = serializers.CharField(read_only=True)

    class Meta:
        model = Jugador
        fields = [
            "id",
            "nombres", "apellidos", "nombre_completo",
            "cedula", "fecha_nacimiento", "telefono", "email", "direccion",
            "foto", "numero_carnet", "estado_calificacion", "observaciones",
            "activo", "created_at", "updated_at",
        ]
        read_only_fields = ["id", "nombre_completo", "created_at", "updated_at"]

    def validate_cedula(self, value):
        qs = Jugador.objects.filter(cedula=value)
        if self.instance:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise serializers.ValidationError("Ya existe un jugador con esta cédula.")
        return value

    def validate_numero_carnet(self, value):
        if not value:
            return value
        qs = Jugador.objects.filter(numero_carnet=value)
        if self.instance:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise serializers.ValidationError("Este número de carnet ya está en uso.")
        return value


class JugadorCalificacionSerializer(serializers.Serializer):
    """Acción específica: cambiar estado de calificación."""
    estado_calificacion = serializers.ChoiceField(
        choices=Jugador.ESTADOS_CALIFICACION
    )
    observaciones = serializers.CharField(required=False, allow_blank=True)


# ─────────────────────────────────────────────
# JugadorEquipoTemporada
# ─────────────────────────────────────────────
class JugadorEquipoTemporadaSerializer(serializers.ModelSerializer):
    jugador_nombre = serializers.CharField(source="jugador.nombre_completo", read_only=True)
    equipo_nombre = serializers.CharField(source="equipo.nombre", read_only=True)
    temporada_nombre = serializers.CharField(source="temporada.nombre", read_only=True)
    categoria_nombre = serializers.CharField(source="categoria.nombre", read_only=True)

    class Meta:
        model = JugadorEquipoTemporada
        fields = [
            "id",
            "jugador", "jugador_nombre",
            "equipo", "equipo_nombre",
            "temporada", "temporada_nombre",
            "categoria", "categoria_nombre",
            "dorsal", "activo", "created_at",
        ]
        read_only_fields = ["id", "created_at"]


class JugadorEquipoTemporadaCreateSerializer(serializers.ModelSerializer):
    """Creación con validación de temporada/categoría del equipo."""

    class Meta:
        model = JugadorEquipoTemporada
        fields = [
            "jugador", "equipo", "temporada", "categoria", "dorsal", "activo",
        ]

    def validate(self, data):
        equipo = data["equipo"]
        temporada = data["temporada"]
        categoria = data["categoria"]

        # El equipo debe estar participando en esa temporada/categoría
        from armenia.models.equipo import EquipoTemporadaCategoria
        if not EquipoTemporadaCategoria.objects.filter(
            equipo=equipo, temporada=temporada, categoria=categoria
        ).exists():
            raise serializers.ValidationError({
                "equipo": "El equipo no está registrado en esta temporada y categoría."
            })
        return data


# ─────────────────────────────────────────────
# CapitanEquipoTemporada
# ─────────────────────────────────────────────
class CapitanEquipoTemporadaSerializer(serializers.ModelSerializer):
    jugador_nombre = serializers.CharField(source="jugador.nombre_completo", read_only=True)
    equipo_nombre = serializers.CharField(source="equipo.nombre", read_only=True)
    temporada_nombre = serializers.CharField(source="temporada.nombre", read_only=True)
    categoria_nombre = serializers.CharField(source="categoria.nombre", read_only=True)

    class Meta:
        model = CapitanEquipoTemporada
        fields = [
            "id",
            "equipo", "equipo_nombre",
            "jugador", "jugador_nombre",
            "temporada", "temporada_nombre",
            "categoria", "categoria_nombre",
            "activo", "created_at",
        ]
        read_only_fields = ["id", "created_at"]

    def validate(self, data):
        equipo = data["equipo"]
        jugador = data["jugador"]
        temporada = data["temporada"]
        categoria = data["categoria"]

        # El jugador debe pertenecer al equipo en esa temporada/categoría
        if not JugadorEquipoTemporada.objects.filter(
            jugador=jugador, equipo=equipo,
            temporada=temporada, categoria=categoria,
        ).exists():
            raise serializers.ValidationError({
                "jugador": "El jugador no pertenece a este equipo en esta temporada y categoría."
            })
        return data