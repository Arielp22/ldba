from rest_framework import serializers

from armenia.models.lesion import Lesion


class LesionSerializer(serializers.ModelSerializer):
    tipo_display = serializers.CharField(source="get_tipo_display", read_only=True)
    gravedad_display = serializers.CharField(source="get_gravedad_display", read_only=True)
    estado_display = serializers.CharField(source="get_estado_display", read_only=True)

    jugador_nombre = serializers.CharField(source="jugador.nombre_completo", read_only=True)
    equipo_nombre = serializers.CharField(source="equipo.nombre", read_only=True)

    class Meta:
        model = Lesion
        fields = [
            "id",
            "jugador", "jugador_nombre",
            "equipo", "equipo_nombre",
            "partido", "vocalia",
            "fecha", "tipo", "tipo_display",
            "gravedad", "gravedad_display",
            "descripcion",
            "monto_apoyo",
            "estado", "estado_display",
            "observaciones",
            "created_at", "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]

    def validate_monto_apoyo(self, value):
        if value is not None and value < 0:
            raise serializers.ValidationError("El monto de apoyo no puede ser negativo.")
        return value


class LesionCambioEstadoSerializer(serializers.Serializer):
    estado = serializers.ChoiceField(choices=Lesion.ESTADOS)
    monto_apoyo = serializers.DecimalField(
        max_digits=10, decimal_places=2, required=False, allow_null=True
    )
    observaciones = serializers.CharField(required=False, allow_blank=True)