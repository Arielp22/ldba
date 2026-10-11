from rest_framework import serializers

from armenia.models.jornada import Jornada, Partido


# ─────────────────────────────────────────────
# Jornada
# ─────────────────────────────────────────────
class JornadaSerializer(serializers.ModelSerializer):
    temporada_nombre = serializers.CharField(source="temporada.nombre", read_only=True)
    categoria_nombre = serializers.CharField(source="categoria.nombre", read_only=True)
    partidos_count = serializers.IntegerField(source="partidos.count", read_only=True)

    class Meta:
        model = Jornada
        fields = [
            "id",
            "temporada", "temporada_nombre",
            "categoria", "categoria_nombre",
            "numero",
            "fecha_sabado", "fecha_domingo",
            "estado",
            "partidos_count",
            "created_at", "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


# ─────────────────────────────────────────────
# Partido
# ─────────────────────────────────────────────
class PartidoSerializer(serializers.ModelSerializer):
    jornada_numero = serializers.IntegerField(source="jornada.numero", read_only=True)
    temporada_nombre = serializers.CharField(source="jornada.temporada.nombre", read_only=True)
    categoria_nombre = serializers.CharField(source="jornada.categoria.nombre", read_only=True)
    equipo_local_nombre = serializers.CharField(source="equipo_local.nombre", read_only=True)
    equipo_visitante_nombre = serializers.CharField(source="equipo_visitante.nombre", read_only=True)
    equipo_vocal_nombre = serializers.CharField(source="equipo_vocal.nombre", read_only=True, default=None)
    dia_display = serializers.CharField(source="get_dia_display", read_only=True)
    estado_display = serializers.CharField(source="get_estado_display", read_only=True)

    class Meta:
        model = Partido
        fields = [
            "id",
            "jornada", "jornada_numero", "temporada_nombre", "categoria_nombre",
            "numero_partido", "dia", "dia_display",
            "hora",
            "equipo_local", "equipo_local_nombre",
            "equipo_visitante", "equipo_visitante_nombre",
            "equipo_vocal", "equipo_vocal_nombre",
            "goles_local", "goles_visitante",
            "estado", "estado_display",
            "observaciones",
            "created_at", "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]

    def validate(self, data):
        local = data.get("equipo_local", getattr(self.instance, "equipo_local", None))
        visitante = data.get("equipo_visitante", getattr(self.instance, "equipo_visitante", None))
        vocal = data.get("equipo_vocal", getattr(self.instance, "equipo_vocal", None))

        # Local ≠ Visitante
        if local and visitante and local == visitante:
            raise serializers.ValidationError(
                {"equipo_visitante": "El equipo visitante no puede ser el mismo que el local."}
            )

        # Vocal ≠ local y ≠ visitante
        if vocal and local and vocal == local:
            raise serializers.ValidationError(
                {"equipo_vocal": "El equipo vocal no puede ser el equipo local."}
            )
        if vocal and visitante and vocal == visitante:
            raise serializers.ValidationError(
                {"equipo_vocal": "El equipo vocal no puede ser el equipo visitante."}
            )

        # Un equipo no vocaliza 2 veces el mismo día en la misma jornada
        if vocal:
            jornada = data.get("jornada", getattr(self.instance, "jornada", None))
            dia = data.get("dia", getattr(self.instance, "dia", None))
            if jornada and dia:
                qs = Partido.objects.filter(
                    jornada=jornada,
                    dia=dia,
                    equipo_vocal=vocal,
                )
                if self.instance:
                    qs = qs.exclude(pk=self.instance.pk)
                if qs.exists():
                    raise serializers.ValidationError({
                        "equipo_vocal": (
                            "Este equipo ya tiene una vocalía asignada en este día "
                            "para esta jornada."
                        )
                    })

        return data


class PartidoResultadoSerializer(serializers.Serializer):
    """Acción: registrar resultado del partido."""
    goles_local = serializers.IntegerField(min_value=0)
    goles_visitante = serializers.IntegerField(min_value=0)
    observaciones = serializers.CharField(required=False, allow_blank=True)