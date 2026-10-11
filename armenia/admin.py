from django.contrib import admin

# Register your models here.
from django.contrib import admin
from armenia.models.temporada import Temporada
from armenia.models.categoria import Categoria
from armenia.models.equipo import Equipo, EquipoTemporadaCategoria
from armenia.models.jugador import (Jugador, JugadorEquipoTemporada, CapitanEquipoTemporada,)
from armenia.models.jornada import Jornada, Partido
from armenia.models.vocalia import Vocalia, VocaliaJugador
from armenia.models.sancion import Sancion, HistorialSancion, Multa, Recibo




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

@admin.register(Sancion)
class SancionAdmin(admin.ModelAdmin):
    list_display = ("id", "tipo", "jugador", "equipo", "motivo", "estado", "fecha_inicio", "dias")
    list_filter = ("tipo", "estado")
    search_fields = ("motivo", "articulo", "jugador__nombres", "equipo__nombre")
    autocomplete_fields = ("jugador", "equipo", "partido", "vocalia")


@admin.register(HistorialSancion)
class HistorialSancionAdmin(admin.ModelAdmin):
    list_display = ("id", "sancion", "estado_anterior", "estado_nuevo", "usuario", "created_at")
    list_filter = ("estado_nuevo", "estado_anterior")
    autocomplete_fields = ("sancion",)


@admin.register(Multa)
class MultaAdmin(admin.ModelAdmin):
    list_display = ("id", "equipo", "monto", "motivo", "estado", "fecha_pago", "forma_pago")
    list_filter = ("estado", "forma_pago")
    search_fields = ("motivo", "equipo__nombre")
    autocomplete_fields = ("sancion", "equipo")


@admin.register(Recibo)
class ReciboAdmin(admin.ModelAdmin):
    list_display = ("id", "numero", "multa", "entregado_a", "entregado_por", "fecha_entrega")
    search_fields = ("numero", "entregado_a", "entregado_por")
    autocomplete_fields = ("multa",)