from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend

from armenia.models.jornada import Jornada, Partido
from armenia.serializers.jornada import (
    JornadaSerializer,
    PartidoSerializer,
    PartidoResultadoSerializer,
)
from armenia.permissions import IsComisionTecnicaOrReadOnly
from armenia.pagination import StandardPagination


class JornadaViewSet(viewsets.ModelViewSet):
    queryset = Jornada.objects.select_related("temporada", "categoria").all()
    serializer_class = JornadaSerializer
    permission_classes = [IsComisionTecnicaOrReadOnly]
    pagination_class = StandardPagination
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ["temporada", "categoria", "estado", "numero"]
    search_fields = ["temporada__nombre", "categoria__nombre"]
    ordering_fields = ["numero", "fecha_sabado", "fecha_domingo", "created_at"]
    ordering = ["temporada", "categoria", "numero"]

    @action(
        detail=True,
        methods=["get"],
        url_path="resumen",
    )
    def resumen(self, request, pk=None):
        """Devuelve todos los partidos de la jornada con datos de equipos."""
        jornada = self.get_object()
        partidos = jornada.partidos.select_related(
            "equipo_local", "equipo_visitante", "equipo_vocal"
        ).all()
        return Response({
            "jornada": JornadaSerializer(jornada).data,
            "partidos": PartidoSerializer(partidos, many=True).data,
        })

    @action(
        detail=True,
        methods=["post"],
        url_path="sortear-vocalias",
    )
    def sortear_vocalias(self, request, pk=None):
        """
        Aplica el emparejamiento fijo P1→P3, P2→P1, P3→P2, P4↔P5
        y sortea cuál de los dos equipos del partido vocalizador hará la vocalía.
        Se ejecuta por día (sábado y domingo por separado).
        """
        import random
        from collections import Counter

        jornada = self.get_object()
        resultados = []

        for dia in ("sabado", "domingo"):
            partidos = list(
                jornada.partidos.filter(dia=dia).order_by("numero_partido")
            )
            if len(partidos) < 5:
                resultados.append({
                    "dia": dia,
                    "error": f"Se esperaban 5 partidos y hay {len(partidos)}.",
                })
                continue

            # Mapeo fijo: partido_a_vocalizar → partido_que_le_vocaliza
            # P1→P3, P2→P1, P3→P2, P4↔P5
            mapeo = {
                1: 3,
                2: 1,
                3: 2,
                4: 5,
                5: 4,
            }

            por_numero = {p.numero_partido: p for p in partidos}

            # Contador de vocalías por equipo (balance por temporada)
            vocales_previas = Counter(
                p.equipo_vocal_id
                for p in jornada.partidos.exclude(equipo_vocal=None)
                if p.equipo_vocal_id
            )

            asignados_hoy = set()

            for num_partido, num_vocalizador in mapeo.items():
                partido = por_numero.get(num_partido)
                vocalizador = por_numero.get(num_vocalizador)

                if not partido or not vocalizador:
                    continue

                candidatos = [
                    vocalizador.equipo_local,
                    vocalizador.equipo_visitante,
                ]
                candidatos = [c for c in candidatos if c.id not in asignados_hoy]

                if not candidatos:
                    resultados.append({
                        "dia": dia,
                        "partido": num_partido,
                        "error": "Sin candidatos disponibles (ambos ya vocalizan hoy).",
                    })
                    continue

                # Ordenar por menor cantidad de vocalías previas (balance)
                candidatos.sort(key=lambda c: vocales_previas.get(c.id, 0))
                min_count = vocales_previas.get(candidatos[0].id, 0)
                empatados = [
                    c for c in candidatos
                    if vocales_previas.get(c.id, 0) == min_count
                ]
                elegido = random.choice(empatados)

                partido.equipo_vocal = elegido
                partido.save(update_fields=["equipo_vocal"])
                asignados_hoy.add(elegido.id)
                vocales_previas[elegido.id] += 1

                resultados.append({
                    "dia": dia,
                    "partido": num_partido,
                    "vocaliza_partido": num_vocalizador,
                    "equipo_vocal": elegido.nombre,
                    "equipo_vocal_id": elegido.id,
                })

        return Response({
            "jornada": jornada.id,
            "asignaciones": resultados,
        })


class PartidoViewSet(viewsets.ModelViewSet):
    queryset = Partido.objects.select_related(
        "jornada", "jornada__temporada", "jornada__categoria",
        "equipo_local", "equipo_visitante", "equipo_vocal",
    ).all()
    serializer_class = PartidoSerializer
    permission_classes = [IsComisionTecnicaOrReadOnly]
    pagination_class = StandardPagination
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = [
        "jornada", "dia", "estado",
        "equipo_local", "equipo_visitante", "equipo_vocal",
    ]
    search_fields = [
        "equipo_local__nombre",
        "equipo_visitante__nombre",
        "equipo_vocal__nombre",
    ]
    ordering_fields = ["dia", "numero_partido", "hora", "created_at"]
    ordering = ["jornada", "dia", "numero_partido"]

    @action(
        detail=True,
        methods=["post"],
        url_path="resultado",
    )
    def resultado(self, request, pk=None):
        """Registra el resultado y marca el partido como finalizado."""
        partido = self.get_object()
        serializer = PartidoResultadoSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        partido.goles_local = serializer.validated_data["goles_local"]
        partido.goles_visitante = serializer.validated_data["goles_visitante"]
        partido.estado = "finalizado"
        if "observaciones" in serializer.validated_data:
            partido.observaciones = serializer.validated_data["observaciones"]
        partido.save()

        return Response(PartidoSerializer(partido).data)