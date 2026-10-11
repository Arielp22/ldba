from rest_framework import serializers

from armenia.models.finanza import MovimientoFinanciero, InformeFinancieroSemanal


class MovimientoFinancieroSerializer(serializers.ModelSerializer):
    tipo_display = serializers.CharField(source="get_tipo_display", read_only=True)

    class Meta:
        model = MovimientoFinanciero
        fields = [
            "id",
            "tipo", "tipo_display",
            "concepto", "fecha", "valor",
            "responsable", "comprobante",
            "observaciones",
            "created_at", "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]

    def validate_valor(self, value):
        if value <= 0:
            raise serializers.ValidationError("El valor debe ser mayor a 0.")
        return value


class InformeFinancieroSemanalSerializer(serializers.ModelSerializer):
    estado_display = serializers.CharField(source="get_estado_display", read_only=True)
    total_ingresos = serializers.DecimalField(
        max_digits=12, decimal_places=2, read_only=True
    )
    balance = serializers.DecimalField(
        max_digits=12, decimal_places=2, read_only=True
    )

    class Meta:
        model = InformeFinancieroSemanal
        fields = [
            "id",
            "numero_semana", "anio", "fecha_semana",
            "cerveza", "boleteria", "multas", "otros_ingresos", "egresos",
            "total_ingresos", "balance",
            "estado", "estado_display",
            "observaciones",
            "created_at", "updated_at",
        ]
        read_only_fields = ["id", "total_ingresos", "balance", "created_at", "updated_at"]

    def validate_numero_semana(self, value):
        if value < 1 or value > 53:
            raise serializers.ValidationError("El número de semana debe estar entre 1 y 53.")
        return value