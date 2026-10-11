from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.crypto import get_random_string


class Equipo(models.Model):
    nombre = models.CharField(max_length=150, unique=True)
    siglas = models.CharField(max_length=10, blank=True, null=True)
    color_principal = models.CharField(max_length=30, blank=True, null=True)
    color_secundario = models.CharField(max_length=30, blank=True, null=True)
    logo = models.CharField(max_length=255, blank=True, null=True)  # solo ruta/metadata
    presidente = models.CharField(max_length=150, blank=True, null=True)
    telefono = models.CharField(max_length=30, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    activo = models.BooleanField(default=True)

    user = models.OneToOneField(
        User,
        on_delete=models.PROTECT,
        related_name="equipo",
        help_text="Usuario único del equipo. Se entrega al presidente.",
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "core_equipo"
        verbose_name = "Equipo"
        verbose_name_plural = "Equipos"
        ordering = ["nombre"]

    def __str__(self):
        return self.nombre


class EquipoTemporadaCategoria(models.Model):
    equipo = models.ForeignKey(
        Equipo,
        on_delete=models.CASCADE,
        related_name="participaciones",
    )
    temporada = models.ForeignKey(
        "armenia.Temporada",
        on_delete=models.CASCADE,
        related_name="equipos",
    )
    categoria = models.ForeignKey(
        "armenia.Categoria",
        on_delete=models.CASCADE,
        related_name="equipos",
    )
    activo = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "core_equipo_temporada_categoria"
        verbose_name = "Equipo por temporada y categoría"
        verbose_name_plural = "Equipos por temporada y categoría"
        unique_together = ("equipo", "temporada", "categoria")
        ordering = ["temporada", "categoria", "equipo"]

    def __str__(self):
        return f"{self.equipo.nombre} — {self.temporada.nombre} — {self.categoria.nombre}"


# ──────────────────────────────────────────────────────────
# Señal: al crear un Equipo, crear automáticamente su User
# ──────────────────────────────────────────────────────────
@receiver(post_save, sender=Equipo)
def _noop(sender, instance, **kwargs):
    """Placeholder para futuras señales."""
    pass