from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework import status

from armenia.services.estadisticas import (
    tabla_posiciones,
    goleadores,
    tarjetas,
)


def _get_params(request):
    temporada = request.query_params.get("temporada")
    categoria = request.query_params.get("categoria")
    if not temporada:
        return None, None, Response(
            {"detail": "El parámetro 'temporada' es obligatorio."},
            status=status.HTTP_400_BAD_REQUEST,
        )
    return temporada, categoria, None


class TablaPosicionesView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        temporada, categoria, err = _get_params(request)
        if err:
            return err
        data = tabla_posiciones(temporada, categoria)
        return Response({
            "temporada": int(temporada),
            "categoria": int(categoria) if categoria else None,
            "tabla": data,
        })


class GoleadoresView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        temporada, categoria, err = _get_params(request)
        if err:
            return err
        limit = request.query_params.get("limit")
        try:
            limit = int(limit) if limit else None
        except ValueError:
            limit = None
        data = goleadores(temporada, categoria, limit)
        return Response({
            "temporada": int(temporada),
            "categoria": int(categoria) if categoria else None,
            "goleadores": data,
        })


class TarjetasView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        temporada, categoria, err = _get_params(request)
        if err:
            return err
        data = tarjetas(temporada, categoria)
        return Response({
            "temporada": int(temporada),
            "categoria": int(categoria) if categoria else None,
            "tarjetas": data,
        })