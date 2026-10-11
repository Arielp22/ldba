from django.contrib import admin

# Register your models here.
from django.contrib import admin
from armenia.models.temporada import Temporada
from armenia.models.categoria import Categoria
from armenia.models.equipo import Equipo, EquipoTemporadaCategoria
from armenia.models.jugador import (Jugador, JugadorEquipoTemporada, CapitanEquipoTemporada,)
from armenia.models.jornada import Jornada, Partido
from armenia.models.vocalia import Vocalia, VocaliaJugador




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

@admin.register(Equipo)
class EquipoAdmin(admin.ModelAdmin):
    list_display = ("id", "nombre", "siglas", "presidente", "user", "activo")
    list_filter = ("activo",)
    search_fields = ("nombre", "siglas", "presidente", "user__username")
    ordering = ("nombre",)


@admin.register(EquipoTemporadaCategoria)
class EquipoTemporadaCategoriaAdmin(admin.ModelAdmin):
    list_display = ("id", "equipo", "temporada", "categoria", "activo")
    list_filter = ("temporada", "categoria", "activo")
    search_fields = ("equipo__nombre", "temporada__nombre", "categoria__nombre")

@admin.register(Jugador)
class JugadorAdmin(admin.ModelAdmin):
    list_display = ("id", "apellidos", "nombres", "cedula", "estado_calificacion", "activo")
    list_filter = ("estado_calificacion", "activo")
    search_fields = ("nombres", "apellidos", "cedula", "numero_carnet")
    ordering = ("apellidos", "nombres")


@admin.register(JugadorEquipoTemporada)
class JugadorEquipoTemporadaAdmin(admin.ModelAdmin):
    list_display = ("id", "jugador", "equipo", "temporada", "categoria", "dorsal", "activo")
    list_filter = ("temporada", "categoria", "equipo", "activo")
    search_fields = ("jugador__nombres", "jugador__apellidos", "jugador__cedula")
    autocomplete_fields = ("jugador", "equipo", "temporada", "categoria")


@admin.register(CapitanEquipoTemporada)
class CapitanEquipoTemporadaAdmin(admin.ModelAdmin):
    list_display = ("id", "equipo", "jugador", "temporada", "categoria", "activo")
    list_filter = ("temporada", "categoria", "equipo", "activo")
    search_fields = ("jugador__nombres", "jugador__apellidos", "equipo__nombre")
    autocomplete_fields = ("equipo", "jugador", "temporada", "categoria")

@admin.register(Jornada)
class JornadaAdmin(admin.ModelAdmin):
    list_display = ("id", "numero", "temporada", "categoria",
                    "fecha_sabado", "fecha_domingo", "estado")
    list_filter = ("temporada", "categoria", "estado")
    search_fields = ("temporada__nombre", "categoria__nombre")
    ordering = ("temporada", "categoria", "numero")
    autocomplete_fields = ("temporada", "categoria")


@admin.register(Partido)
class PartidoAdmin(admin.ModelAdmin):
    list_display = (
        "id", "jornada", "dia", "numero_partido", "hora",
        "equipo_local", "equipo_visitante", "equipo_vocal",
        "goles_local", "goles_visitante", "estado",
    )
    list_filter = ("dia", "estado", "jornada__temporada", "jornada__categoria")
    search_fields = (
        "equipo_local__nombre",
        "equipo_visitante__nombre",
        "equipo_vocal__nombre",
    )
    ordering = ("jornada", "dia", "numero_partido")
    autocomplete_fields = ("jornada", "equipo_local", "equipo_visitante", "equipo_vocal")

@admin.register(Vocalia)
class VocaliaAdmin(admin.ModelAdmin):
    list_display = (
        "id", "partido", "arbitro", "vocal",
        "goles_local", "goles_visitante", "estado",
    )
    list_filter = ("estado",)
    search_fields = ("arbitro", "vocal")
    autocomplete_fields = ("partido",)
    ordering = ("-created_at",)


@admin.register(VocaliaJugador)
class VocaliaJugadorAdmin(admin.ModelAdmin):
    list_display = (
        "id", "vocalia", "jugador", "equipo",
        "goles", "tarjeta_amarilla", "tarjeta_roja", "es_capitan",
    )
    list_filter = ("tarjeta_amarilla", "tarjeta_roja", "es_capitan")
    search_fields = ("jugador__nombres", "jugador__apellidos", "equipo__nombre")
    autocomplete_fields = ("vocalia", "jugador", "equipo")