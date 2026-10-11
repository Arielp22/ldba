from django.db import models


class Lesion(models.Model):
    TIPOS = [
        ("esguince", "Esguince"),
        ("fractura", "Fractura"),
        ("desgarro", "Desgarro"),
        ("contusion", "Contusión"),
        ("luxacion", "Luxación"),
        ("otro", "Otro"),
    ]
    GRAVEDAD = [
        ("leve", "Leve"),
        ("moderada", "Moderada"),
        ("grave", "Grave"),
    ]
    ESTADOS = [
        ("reportada", "Reportada"),
        ("en_revision", "En revisión"),
        ("aprobada", "Aprobada"),
        ("rechazada", "Rechazada"),
        ("pagada", "Pagada"),
    ]

    jugador = models.ForeignKey(
        "armenia.Jugador",
        on_delete=models.CASCADE,
        related_name="lesiones",
    )
    partido = models.ForeignKey(
        "armenia.Partido",
        on_delete=models.SET_NULL,
        related_name="lesiones",
        blank=True, null=True,
    )
    vocalia = models.ForeignKey(
        "armenia.Vocalia",
        on_delete=models.SET_NULL,
        related_name="lesiones",
        blank=True, null=True,
    )
    equipo = models.ForeignKey(
        "armenia.Equipo",
        on_delete=models.SET_NULL,
        related_name="lesiones",
        blank=True, null=True,
    )

    fecha = models.DateField()
    tipo = models.CharField(max_length=20, choices=TIPOS)
    gravedad = models.CharField(max_length=20, choices=GRAVEDAD, default="leve")
    descripcion = models.TextField(blank=True, null=True)

    monto_apoyo = models.DecimalField(
        max_digits=10, decimal_places=2, blank=True, null=True
    )
    estado = models.CharField(max_length=20, choices=ESTADOS, default="reportada")
    observaciones = models.TextField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "core_lesion"
        verbose_name = "Lesión"
        verbose_name_plural = "Lesiones"
        ordering = ["-fecha", "-created_at"]
        indexes = [
            models.Index(fields=["estado"]),
            models.Index(fields=["gravedad"]),
            models.Index(fields=["fecha"]),
        ]

    def __str__(self):
        return f"Lesión {self.get_tipo_display()} — {self.jugador} ({self.fecha})"