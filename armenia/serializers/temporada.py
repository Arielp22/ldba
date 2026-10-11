from rest_framework import serializers
from armenia.models import Temporada


class TemporadaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Temporada
        fields = [
            "id", "nombre", "anio",
            "fecha_inicio", "fecha_fin",
            "estado", "created_at", "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]

    def validate(self, data):
        if data.get("fecha_inicio") and data.get("fecha_fin"):
            if data["fecha_inicio"] >= data["fecha_fin"]:
                raise serializers.ValidationError(
                    {"fecha_fin": "La fecha de fin debe ser posterior a la de inicio."}
                )
        return data