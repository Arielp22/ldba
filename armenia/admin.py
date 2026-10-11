from django.contrib import admin

# Register your models here.
from django.contrib import admin
from armenia.models.temporada import Temporada
from armenia.models.categoria import Categoria


@admin.register(Temporada)
class TemporadaAdmin(admin.ModelAdmin):
    list_display = ("id", "nombre", "anio", "estado", "fecha_inicio", "fecha_fin")
    list_filter = ("estado", "anio")
    search_fields = ("nombre",)
    ordering = ("-anio",)
    date_hierarchy = "fecha_inicio"


@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ("id", "nombre", "activa", "created_at")
    list_filter = ("activa",)
    search_fields = ("nombre",)
    ordering = ("nombre",)