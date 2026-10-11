from django.db import models


class Jornada(models.Model):
    ESTADOS = [
        ("planificada", "Planificada"),
        ("en_curso", "En curso"),
        ("finalizada", "Finalizada"),
        ("cancelada", "Cancelada"),
    ]

    temporada = models.ForeignKey(
        "armenia.Temporada",
        on_delete=models.CASCADE,
        related_name="jornadas",
    )
    categoria = models.ForeignKey(
        "armenia.Categoria",
        on_delete=models.CASCADE,
        related_name="jornadas",
    )
    numero = models.PositiveIntegerField()
    fecha_sabado = models.DateField()
    fecha_domingo = models.DateField()
    estado = models.CharField(max_length=20, choices=ESTADOS, default="planificada")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "core_jornada"
        verbose_name = "Jornada"
        verbose_name_plural = "Jornadas"
        unique_together = ("temporada", "categoria", "numero")
        ordering = ["temporada", "categoria", "numero"]
        indexes = [
            models.Index(fields=["temporada", "categoria"]),
            models.Index(fields=["fecha_sabado"]),
        ]

    def __str__(self):
        return f"Jornada {self.numero} — {self.categoria.nombre} — {self.temporada.nombre}"


class Partido(models.Model):
    DIAS = [
        ("sabado", "Sábado"),
        ("domingo", "Domingo"),
    ]
    ESTADOS = [
        ("programado", "Programado"),
        ("en_curso", "En curso"),
        ("finalizado", "Finalizado"),
        ("suspendido", "Suspendido"),
        ("cancelado", "Cancelado"),
    ]

    jornada = models.ForeignKey(
        Jornada,
        on_delete=models.CASCADE,
        related_name="partidos",
    )
    numero_partido = models.PositiveIntegerField(help_text="1 a 5 dentro del día")
    dia = models.CharField(max_length=10, choices=DIAS)
    hora = models.TimeField(blank=True, null=True)

    equipo_local = models.ForeignKey(
        "armenia.Equipo",
        on_delete=models.PROTECT,
        related_name="partidos_como_local",
    )
    equipo_visitante = models.ForeignKey(
        "armenia.Equipo",
        on_delete=models.PROTECT,
        related_name="partidos_como_visitante",
    )
    equipo_vocal = models.ForeignKey(
        "armenia.Equipo",
        on_delete=models.SET_NULL,
        related_name="partidos_como_vocal",
        blank=True,
        null=True,
    )

    goles_local = models.PositiveIntegerField(blank=True, null=True)
    goles_visitante = models.PositiveIntegerField(blank=True, null=True)

    estado = models.CharField(max_length=20, choices=ESTADOS, default="programado")
    observaciones = models.TextField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "core_partido"
        verbose_name = "Partido"
        verbose_name_plural = "Partidos"
        unique_together = ("jornada", "dia", "numero_partido")
        ordering = ["jornada", "dia", "numero_partido"]
        indexes = [
            models.Index(fields=["jornada", "dia"]),
            models.Index(fields=["estado"]),
        ]

    def __str__(self):
        return (
            f"{self.equipo_local.nombre} vs {self.equipo_visitante.nombre} "
            f"({self.get_dia_display()} P{self.numero_partido})"
        )