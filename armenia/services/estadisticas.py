from django.db.models import Count, Sum, Q, F, Case, When, IntegerField
from django.db.models.functions import Coalesce

from armenia.models.jornada import Partido
from armenia.models.vocalia import VocaliaJugador


def tabla_posiciones(temporada_id, categoria_id=None):
    """
    Devuelve la tabla de posiciones para una temporada (y categoría opcional).
    Solo cuenta partidos finalizados.
    """
    qs = Partido.objects.filter(
        jornada__temporada_id=temporada_id,
        estado="finalizado",
        goles_local__isnull=False,
        goles_visitante__isnull=False,
    )
    if categoria_id:
        qs = qs.filter(jornada__categoria_id=categoria_id)

    equipos = {}

    def _init(equipo_id, nombre):
        if equipo_id not in equipos:
            equipos[equipo_id] = {
                "equipo_id": equipo_id,
                "equipo": nombre,
                "pj": 0, "pg": 0, "pe": 0, "pp": 0,
                "gf": 0, "gc": 0, "dg": 0, "pts": 0,
            }

    for p in qs.select_related("equipo_local", "equipo_visitante"):
        local = p.equipo_local
        visita = p.equipo_visitante
        gl = p.goles_local
        gv = p.goles_visitante

        _init(local.id, local.nombre)
        _init(visita.id, visita.nombre)

        equipos[local.id]["pj"] += 1
        equipos[visita.id]["pj"] += 1
        equipos[local.id]["gf"] += gl
        equipos[local.id]["gc"] += gv
        equipos[visita.id]["gf"] += gv
        equipos[visita.id]["gc"] += gl

        if gl > gv:
            equipos[local.id]["pg"] += 1
            equipos[local.id]["pts"] += 3
            equipos[visita.id]["pp"] += 1
        elif gl < gv:
            equipos[visita.id]["pg"] += 1
            equipos[visita.id]["pts"] += 3
            equipos[local.id]["pp"] += 1
        else:
            equipos[local.id]["pe"] += 1
            equipos[local.id]["pts"] += 1
            equipos[visita.id]["pe"] += 1
            equipos[visita.id]["pts"] += 1

    tabla = list(equipos.values())
    for row in tabla:
        row["dg"] = row["gf"] - row["gc"]

    tabla.sort(key=lambda r: (-r["pts"], -r["dg"], -r["gf"], r["equipo"]))
    for idx, row in enumerate(tabla, start=1):
        row["posicion"] = idx
    return tabla


def goleadores(temporada_id, categoria_id=None, limit=None):
    """
    Ranking de goleadores desde VocaliaJugador.
    """
    qs = VocaliaJugador.objects.filter(
        vocalia__partido__jornada__temporada_id=temporada_id,
        goles__gt=0,
    )
    if categoria_id:
        qs = qs.filter(vocalia__partido__jornada__categoria_id=categoria_id)

    qs = (
        qs.values(
            "jugador_id",
            "jugador__nombres",
            "jugador__apellidos",
            "equipo__id",
            "equipo__nombre",
        )
        .annotate(total_goles=Sum("goles"))
        .order_by("-total_goles", "jugador__apellidos")
    )

    if limit:
        qs = qs[:limit]

    return [
        {
            "jugador_id": r["jugador_id"],
            "jugador": f"{r['jugador__apellidos']}, {r['jugador__nombres']}",
            "equipo_id": r["equipo__id"],
            "equipo": r["equipo__nombre"],
            "goles": r["total_goles"],
        }
        for r in qs
    ]


def tarjetas(temporada_id, categoria_id=None):
    """
    Ranking de tarjetas amarillas y rojas por jugador.
    """
    qs = VocaliaJugador.objects.filter(
        vocalia__partido__jornada__temporada_id=temporada_id,
    )
    if categoria_id:
        qs = qs.filter(vocalia__partido__jornada__categoria_id=categoria_id)

    qs = (
        qs.values(
            "jugador_id",
            "jugador__nombres",
            "jugador__apellidos",
            "equipo__nombre",
        )
        .annotate(
            amarillas=Count("id", filter=Q(tarjeta_amarilla=True)),
            rojas=Count("id", filter=Q(tarjeta_roja=True)),
        )
        .filter(Q(amarillas__gt=0) | Q(rojas__gt=0))
        .order_by("-rojas", "-amarillas", "jugador__apellidos")
    )

    return [
        {
            "jugador_id": r["jugador_id"],
            "jugador": f"{r['jugador__apellidos']}, {r['jugador__nombres']}",
            "equipo": r["equipo__nombre"],
            "amarillas": r["amarillas"],
            "rojas": r["rojas"],
            "total": r["amarillas"] + r["rojas"],
        }
        for r in qs
    ]