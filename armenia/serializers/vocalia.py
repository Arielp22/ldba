from rest_framework import serializers

from armenia.models.vocalia import Vocalia, VocaliaJugador


# ─────────────────────────────────────────────
# Vocalia
# ─────────────────────────────────────────────
class VocaliaSerializer(serializers.ModelSerializer):
    partido_info = serializers.SerializerMethodField()
    estado_display = serializers.CharField(source="get_estado_display", read_only=True)

    class Meta:
        model = Vocalia
        fields = [
            "id",
            "partido", "partido_info",
            "arbitro", "vocal",
            "goles_local", "goles_visitante",
            "informe",
            "firma_arbitro", "firma_vocal",
            "estado", "estado_display",
            "observaciones_rechazo",
            "created_at", "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]

    def get_partido_info(self, obj):
        if not obj.partido:
            return None
        p = obj.partido
        return {
            "id": p.id,
            "dia": p.dia,
            "numero_partido": p.numero_partido,
            "hora": p.hora,
            "equipo_local": p.equipo_local.nombre,
            "equipo_visitante": p.equipo_visitante.nombre,
            "jornada_numero": p.jornada.numero,
        }


class VocaliaRechazoSerializer(serializers.Serializer):
    observaciones_rechazo = serializers.CharField()


# ─────────────────────────────────────────────
# VocaliaJugador
# ─────────────────────────────────────────────
class VocaliaJugadorSerializer(serializers.ModelSerializer):
    jugador_nombre = serializers.CharField(source="jugador.nombre_completo", read_only=True)
    equipo_nombre = serializers.CharField(source="equipo.nombre", read_only=True)

    class Meta:
        model = VocaliaJugador
        fields = [
            "id",
            "vocalia",
            "jugador", "jugador_nombre",
            "equipo", "equipo_nombre",
            "goles", "tarjeta_amarilla", "tarjeta_roja", "es_capitan",
            "ingreso_minuto", "salida_minuto",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]

    def validate(self, data):
        vocalia = data.get("vocalia", getattr(self.instance, "vocalia", None))
        equipo = data.get("equipo", getattr(self.instance, "equipo", None))

        if vocalia and vocalia.partido and equipo:
            partido = vocalia.partido
            if equipo not in (partido.equipo_local, partido.equipo_visitante):
                raise serializers.ValidationError({
                    "equipo": (
                        "El equipo debe ser el local o visitante del partido "
                        "de esta vocalía."
                    )
                })

        if vocalia:
            jugador = data.get("jugador", getattr(self.instance, "jugador", None))
            if jugador:
                qs = VocaliaJugador.objects.filter(vocalia=vocalia, jugador=jugador)
                if self.instance:
                    qs = qs.exclude(pk=self.instance.pk)
                if qs.exists():
                    raise serializers.ValidationError({
                        "jugador": "Este jugador ya está registrado en esta vocalía."
                    })

        return data