from django.db import models


class Jugador(models.Model):
    ESTADOS_CALIFICACION = [
        ("pendiente", "Pendiente"),
        ("calificado", "Calificado"),
        ("rechazado", "Rechazado"),
        ("inhabilitado", "Inhabilitado"),
    ]

    # Datos personales
    nombres = models.CharField(max_length=150)
    apellidos = models.CharField(max_length=150)
    cedula = models.CharField(max_length=20, unique=True)
    fecha_nacimiento = models.DateField()
    telefono = models.CharField(max_length=30, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    direccion = models.CharField(max_length=255, blank=True, null=True)

    # Documentación / calificación
    foto = models.CharField(max_length=255, blank=True, null=True)  # solo ruta
    numero_carnet = models.CharField(max_length=30, blank=True, null=True, unique=True)
    estado_calificacion = models.CharField(
        max_length=20,
        choices=ESTADOS_CALIFICACION,
        default="pendiente",
    )
    observaciones = models.TextField(blank=True, null=True)

    activo = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "core_jugador"
        verbose_name = "Jugador"
        verbose_name_plural = "Jugadores"
        ordering = ["apellidos", "nombres"]
        indexes = [
            models.Index(fields=["cedula"]),
            models.Index(fields=["estado_calificacion"]),
        ]

    def __str__(self):
        return f"{self.apellidos}, {self.nombres} ({self.cedula})"

    @property
    def nombre_completo(self):
        return f"{self.nombres} {self.apellidos}"


class JugadorEquipoTemporada(models.Model):
    jugador = models.ForeignKey(
        Jugador,
        on_delete=models.CASCADE,
        related_name="participaciones",
    )
    equipo = models.ForeignKey(
        "armenia.Equipo",
        on_delete=models.CASCADE,
        related_name="jugadores",
    )
    temporada = models.ForeignKey(
        "armenia.Temporada",
        on_delete=models.CASCADE,
        related_name="jugadores",
    )
    categoria = models.ForeignKey(
        "armenia.Categoria",
        on_delete=models.CASCADE,
        related_name="jugadores",
    )
    dorsal = models.PositiveIntegerField(blank=True, null=True)
    activo = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "core_jugador_equipo_temporada"
        verbose_name = "Jugador por equipo y temporada"
        verbose_name_plural = "Jugadores por equipo y temporada"
        unique_together = ("jugador", "temporada", "categoria")
        ordering = ["temporada", "categoria", "equipo", "dorsal"]

    def __str__(self):
        return f"{self.jugador} — {self.equipo.nombre} — {self.temporada.nombre}"


class CapitanEquipoTemporada(models.Model):
    equipo = models.ForeignKey(
        "armenia.Equipo",
        on_delete=models.CASCADE,
        related_name="capitanes",
    )
    jugador = models.ForeignKey(
        Jugador,
        on_delete=models.CASCADE,
        related_name="capitanias",
    )
    temporada = models.ForeignKey(
        "armenia.Temporada",
        on_delete=models.CASCADE,
        related_name="capitanes",
    )
    categoria = models.ForeignKey(
        "armenia.Categoria",
        on_delete=models.CASCADE,
        related_name="capitanes",
    )
    activo = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "core_capitan_equipo_temporada"
        verbose_name = "Capitán por equipo y temporada"
        verbose_name_plural = "Capitanes por equipo y temporada"
        unique_together = ("equipo", "temporada", "categoria")
        ordering = ["temporada", "categoria", "equipo"]

    def __str__(self):
        return f"{self.jugador} — Capitán {self.equipo.nombre} ({self.temporada.nombre})"