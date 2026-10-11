from rest_framework import serializers

from armenia.models.sancion import (
    Sancion, HistorialSancion, Multa, Recibo,
)


class SancionSerializer(serializers.ModelSerializer):
    tipo_display = serializers.CharField(source="get_tipo_display", read_only=True)
    estado_display = serializers.CharField(source="get_estado_display", read_only=True)
    jugador_nombre = serializers.CharField(source="jugador.nombre_completo", read_only=True)
    equipo_nombre = serializers.CharField(source="equipo.nombre", read_only=True)

    class Meta:
        model = Sancion
        fields = [
            "id",
            "tipo", "tipo_display",
            "jugador", "jugador_nombre",
            "equipo", "equipo_nombre",
            "partido", "vocalia",
            "motivo", "articulo",
            "fecha_inicio", "fecha_fin", "dias", "partidos_sancion",
            "estado", "estado_display",
            "observaciones",
            "created_at", "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]

    def validate(self, data):
        tipo = data.get("tipo", getattr(self.instance, "tipo", None))
        jugador = data.get("jugador", getattr(self.instance, "jugador", None))
        equipo = data.get("equipo", getattr(self.instance, "equipo", None))

        if tipo == "jugador" and not jugador:
            raise serializers.ValidationError(
                {"jugador": "Si la sanción es de tipo jugador, debes indicarlo."}
            )
        if tipo == "equipo" and not equipo:
            raise serializers.ValidationError(
                {"equipo": "Si la sanción es de tipo equipo, debes indicarlo."}
            )
        return data


class SancionCambioEstadoSerializer(serializers.Serializer):
    estado = serializers.ChoiceField(choices=Sancion.ESTADOS)
    motivo_cambio = serializers.CharField(required=False, allow_blank=True)


class HistorialSancionSerializer(serializers.ModelSerializer):
    class Meta:
        model = HistorialSancion
        fields = [
            "id", "sancion",
            "estado_anterior", "estado_nuevo",
            "motivo_cambio", "usuario",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]


class MultaSerializer(serializers.ModelSerializer):
    estado_display = serializers.CharField(source="get_estado_display", read_only=True)
    forma_pago_display = serializers.CharField(source="get_forma_pago_display", read_only=True)
    equipo_nombre = serializers.CharField(source="equipo.nombre", read_only=True)

    class Meta:
        model = Multa
        fields = [
            "id",
            "sancion", "equipo", "equipo_nombre",
            "monto", "motivo",
            "estado", "estado_display",
            "fecha_pago", "forma_pago", "forma_pago_display",
            "observaciones",
            "created_at", "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]

    def validate(self, data):
        estado = data.get("estado", getattr(self.instance, "estado", None))
        fecha_pago = data.get("fecha_pago", getattr(self.instance, "fecha_pago", None))
        forma_pago = data.get("forma_pago", getattr(self.instance, "forma_pago", None))

        if estado == "pagada" and (not fecha_pago or not forma_pago):
            raise serializers.ValidationError({
                "estado": "Si la multa está pagada, se requiere fecha_pago y forma_pago."
            })
        return data


class ReciboSerializer(serializers.ModelSerializer):
    multa_monto = serializers.DecimalField(
        source="multa.monto", max_digits=10, decimal_places=2, read_only=True
    )
    multa_motivo = serializers.CharField(source="multa.motivo", read_only=True)

    class Meta:
        model = Recibo
        fields = [
            "id", "multa", "multa_monto", "multa_motivo",
            "numero", "entregado_a", "entregado_por",
            "fecha_entrega", "observaciones",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]

    def validate_numero(self, value):
        qs = Recibo.objects.filter(numero=value)
        if self.instance:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise serializers.ValidationError("Este número de recibo ya existe.")
        return value