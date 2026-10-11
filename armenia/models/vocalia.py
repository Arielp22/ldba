from django.db import models


class Vocalia(models.Model):
    ESTADOS = [
        ("borrador", "Borrador"),
        ("enviada", "Enviada"),
        ("aprobada", "Aprobada"),
        ("rechazada", "Rechazada"),
    ]

    partido = models.OneToOneField(
        "armenia.Partido",
        on_delete=models.CASCADE,
        related_name="vocalia",
        blank=True,
        null=True,
    )

    # Árbitro y vocal: texto libre, no hay catálogo
    arbitro = models.CharField(max_length=150)
    vocal = models.CharField(max_length=150)

    # Resultado (respalda al Partido)
    goles_local = models.PositiveIntegerField(blank=True, null=True)
    goles_visitante = models.PositiveIntegerField(blank=True, null=True)

    informe = models.TextField(blank=True, null=True)

    # Firmas (solo ruta/metadata, no archivos en BD)
    firma_arbitro = models.CharField(max_length=255, blank=True, null=True)
    firma_vocal = models.CharField(max_length=255, blank=True, null=True)

    estado = models.CharField(max_length=20, choices=ESTADOS, default="borrador")
    observaciones_rechazo = models.TextField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "core_vocalia"
        verbose_name = "Vocalía"
        verbose_name_plural = "Vocalías"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["estado"]),
        ]

    def __str__(self):
        return f"Vocalía — {self.partido} ({self.estado})"


class VocaliaJugador(models.Model):
    vocalia = models.ForeignKey(
        Vocalia,
        on_delete=models.CASCADE,
        related_name="jugadores",
    )
    jugador = models.ForeignKey(
        "armenia.Jugador",
        on_delete=models.PROTECT,
        related_name="vocalias",
    )
    equipo = models.ForeignKey(
        "armenia.Equipo",
        on_delete=models.PROTECT,
        related_name="vocalias_jugadores",
    )

    goles = models.PositiveIntegerField(default=0)
    tarjeta_amarilla = models.BooleanField(default=False)
    tarjeta_roja = models.BooleanField(default=False)
    es_capitan = models.BooleanField(default=False)

    ingreso_minuto = models.PositiveIntegerField(blank=True, null=True)
    salida_minuto = models.PositiveIntegerField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "core_vocalia_jugador"
        verbose_name = "Jugador en vocalía"
        verbose_name_plural = "Jugadores en vocalía"
        unique_together = ("vocalia", "jugador")
        ordering = ["vocalia", "equipo", "jugador"]

    def __str__(self):
        return f"{self.jugador} — {self.equipo.nombre}"