from django.db import models


class MovimientoFinanciero(models.Model):
    TIPOS = [
        ("ingreso", "Ingreso"),
        ("egreso", "Egreso"),
    ]

    tipo = models.CharField(max_length=10, choices=TIPOS)
    concepto = models.CharField(max_length=255)
    fecha = models.DateField()
    valor = models.DecimalField(max_digits=12, decimal_places=2)
    responsable = models.CharField(max_length=150, blank=True, null=True)
    comprobante = models.CharField(max_length=255, blank=True, null=True)
    observaciones = models.TextField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "core_movimiento_financiero"
        verbose_name = "Movimiento financiero"
        verbose_name_plural = "Movimientos financieros"
        ordering = ["-fecha", "-created_at"]
        indexes = [
            models.Index(fields=["tipo"]),
            models.Index(fields=["fecha"]),
        ]

    def __str__(self):
        return f"{self.get_tipo_display()} ${self.valor} — {self.concepto} ({self.fecha})"


class InformeFinancieroSemanal(models.Model):
    ESTADOS = [
        ("borrador", "Borrador"),
        ("presentado", "Presentado"),
        ("aprobado", "Aprobado"),
    ]

    numero_semana = models.PositiveIntegerField()
    anio = models.PositiveIntegerField()
    fecha_semana = models.DateField(help_text="Fecha del sábado de la semana")

    cerveza = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    boleteria = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    multas = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    otros_ingresos = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    egresos = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    estado = models.CharField(max_length=20, choices=ESTADOS, default="borrador")
    observaciones = models.TextField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "core_informe_financiero_semanal"
        verbose_name = "Informe financiero semanal"
        verbose_name_plural = "Informes financieros semanales"
        unique_together = ("numero_semana", "anio")
        ordering = ["-anio", "-numero_semana"]

    def __str__(self):
        return f"Informe semanal {self.numero_semana}/{self.anio}"

    @property
    def total_ingresos(self):
        return (self.cerveza or 0) + (self.boleteria or 0) + \
               (self.multas or 0) + (self.otros_ingresos or 0)

    @property
    def balance(self):
        return self.total_ingresos - (self.egresos or 0)