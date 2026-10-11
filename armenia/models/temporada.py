from django.db import models


class Temporada(models.Model):
    ESTADOS = [
        ("planificada", "Planificada"),
        ("en_curso", "En curso"),
        ("finalizada", "Finalizada"),
        ("cancelada", "Cancelada"),
    ]

    nombre = models.CharField(max_length=100, unique=True)
    anio = models.PositiveIntegerField()
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField()
    estado = models.CharField(max_length=20, choices=ESTADOS, default="planificada")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "core_temporada"
        verbose_name = "Temporada"
        verbose_name_plural = "Temporadas"
        ordering = ["-anio", "nombre"]

    def __str__(self):
        return f"{self.nombre} ({self.anio})"