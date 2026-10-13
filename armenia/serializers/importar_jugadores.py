from django.db import transaction
from rest_framework import serializers

from armenia.models.equipo import Equipo, EquipoTemporadaCategoria
from armenia.models.temporada import Temporada
from armenia.models.categoria import Categoria
from armenia.models.jugador import Jugador, JugadorEquipoTemporada


# Columnas esperadas en el Excel
COLUMNAS_ESPERADAS = [
    "nombres",
    "apellidos",
    "cedula",
    "fecha_nacimiento",
    "telefono",
    "email",
    "direccion",
    "equipo",
    "temporada",
    "categoria",
]

MAX_FILAS = 35


class ImportarJugadoresSerializer(serializers.Serializer):
    archivo = serializers.FileField()

    def validate_archivo(self, value):
        if not value.name.lower().endswith((".xlsx", ".xls")):
            raise serializers.ValidationError(
                "El archivo debe ser un Excel (.xlsx o .xls)."
            )
        return value

    @transaction.atomic
    def create(self, validated_data):
        """
        Procesa el Excel en transacción atómica.
        Si hay cualquier error → rollback total y devuelve errores.
        """
        import openpyxl

        archivo = validated_data["archivo"]

        try:
            wb = openpyxl.load_workbook(archivo, data_only=True)
            ws = wb.active
        except Exception as e:
            raise serializers.ValidationError(
                {"archivo": f"No se pudo leer el Excel: {str(e)}"}
            )

        # Leer todas las filas
        filas = list(ws.iter_rows(values_only=True))
        if not filas:
            raise serializers.ValidationError({"archivo": "El Excel está vacío."})

        # Validar cabecera
        cabecera = [str(c).strip().lower() if c is not None else "" for c in filas[0]]
        if cabecera != COLUMNAS_ESPERADAS:
            raise serializers.ValidationError(
                {
                    "archivo": (
                        "Las columnas del Excel no coinciden con el formato esperado. "
                        f"Esperadas: {COLUMNAS_ESPERADAS}. Recibidas: {cabecera}."
                    )
                }
            )

        # Filas de datos (sin cabecera)
        datos = filas[1:]

        # Filtrar filas completamente vacías
        datos = [
            fila
            for fila in datos
            if any(c is not None and str(c).strip() != "" for c in fila)
        ]

        if not datos:
            raise serializers.ValidationError(
                {"archivo": "El Excel no contiene filas de datos."}
            )

        if len(datos) > MAX_FILAS:
            raise serializers.ValidationError(
                {
                    "archivo": (
                        f"El Excel tiene {len(datos)} filas. "
                        f"El máximo permitido es {MAX_FILAS}."
                    )
                }
            )

        # Procesar fila por fila
        errores = []
        jugadores_creados = []

        for idx, fila in enumerate(datos, start=2):
            fila = list(fila) + [None] * (len(COLUMNAS_ESPERADAS) - len(fila))
            registro = dict(zip(COLUMNAS_ESPERADAS, fila))

            try:
                jugador = self._procesar_fila(registro)
                jugadores_creados.append(jugador)
            except serializers.ValidationError as e:
                errores.append(
                    {"fila": idx, "error": self._formatear_error(e.detail)}
                )
            except Exception as e:
                errores.append({"fila": idx, "error": str(e)})

        if errores:
            raise serializers.ValidationError({"errores": errores})

        return {"creados": len(jugadores_creados)}

    def _procesar_fila(self, r):
        """Valida y crea un jugador + su inscripción."""
        from datetime import datetime, date
        from django.core.validators import validate_email
        from django.core.exceptions import ValidationError as DjangoValidationError

        # ── Normalizar strings ──────────────────────────────────────────────
        def _s(v):
            return str(v).strip() if v is not None else ""

        nombres = _s(r["nombres"])
        apellidos = _s(r["apellidos"])
        cedula = _s(r["cedula"])
        telefono = _s(r["telefono"]) or None
        email = _s(r["email"]) or None
        direccion = _s(r["direccion"]) or None
        equipo_nombre = _s(r["equipo"])
        temporada_nombre = _s(r["temporada"])
        categoria_nombre = _s(r["categoria"])

        # Fecha: NO la convertimos a string, la procesamos aparte
        fecha_raw = r["fecha_nacimiento"]

        # ── Validaciones básicas ────────────────────────────────────────────
        if not nombres:
            raise serializers.ValidationError("Nombres vacío.")
        if not apellidos:
            raise serializers.ValidationError("Apellidos vacío.")
        if not cedula:
            raise serializers.ValidationError("Cédula vacía.")

        # ── Validar fecha ───────────────────────────────────────────────────
        fecha_dt = None

        # Caso 1: openpyxl devuelve datetime/date
        if isinstance(fecha_raw, datetime):
            fecha_dt = fecha_raw.date()
        elif isinstance(fecha_raw, date):
            fecha_dt = fecha_raw
        # Caso 2: string YYYY-MM-DD
        elif isinstance(fecha_raw, str) and fecha_raw.strip():
            try:
                fecha_dt = datetime.strptime(fecha_raw.strip(), "%Y-%m-%d").date()
            except ValueError:
                raise serializers.ValidationError(
                    f"Fecha inválida: '{fecha_raw}'. Formato esperado: YYYY-MM-DD."
                )

        if not fecha_dt:
            raise serializers.ValidationError(
                "Fecha de nacimiento vacía o con formato inválido."
            )

        # ── Cédula única ────────────────────────────────────────────────────
        if Jugador.objects.filter(cedula=cedula).exists():
            raise serializers.ValidationError(
                f"Ya existe un jugador con la cédula {cedula}."
            )

        # ── Email válido si viene ───────────────────────────────────────────
        if email:
            try:
                validate_email(email)
            except DjangoValidationError:
                raise serializers.ValidationError(f"Email inválido: '{email}'.")

        # ── Resolver equipo/temporada/categoría ─────────────────────────────
        if not equipo_nombre:
            raise serializers.ValidationError("Equipo vacío.")
        if not temporada_nombre:
            raise serializers.ValidationError("Temporada vacía.")
        if not categoria_nombre:
            raise serializers.ValidationError("Categoría vacía.")

        try:
            equipo = Equipo.objects.get(nombre__iexact=equipo_nombre)
        except Equipo.DoesNotExist:
            raise serializers.ValidationError(f"Equipo '{equipo_nombre}' no existe.")

        try:
            temporada = Temporada.objects.get(nombre__iexact=temporada_nombre)
        except Temporada.DoesNotExist:
            raise serializers.ValidationError(
                f"Temporada '{temporada_nombre}' no existe."
            )

        try:
            categoria = Categoria.objects.get(nombre__iexact=categoria_nombre)
        except Categoria.DoesNotExist:
            raise serializers.ValidationError(
                f"Categoría '{categoria_nombre}' no existe."
            )

        # ── Verificar inscripción del equipo ────────────────────────────────
        if not EquipoTemporadaCategoria.objects.filter(
            equipo=equipo, temporada=temporada, categoria=categoria
        ).exists():
            raise serializers.ValidationError(
                f"El equipo '{equipo.nombre}' no está inscrito en "
                f"{temporada.nombre} · {categoria.nombre}."
            )

        # ── Crear jugador + inscripción ─────────────────────────────────────
        jugador = Jugador.objects.create(
            nombres=nombres,
            apellidos=apellidos,
            cedula=cedula,
            fecha_nacimiento=fecha_dt,
            telefono=telefono,
            email=email,
            direccion=direccion,
            estado_calificacion="pendiente",
            activo=True,
        )

        JugadorEquipoTemporada.objects.create(
            jugador=jugador,
            equipo=equipo,
            temporada=temporada,
            categoria=categoria,
            activo=True,
        )

        return jugador

    def _formatear_error(self, detail):
        """Convierte el detail de DRF a un string legible."""
        if isinstance(detail, dict):
            return "; ".join(
                f"{k}: {self._formatear_error(v)}" for k, v in detail.items()
            )
        if isinstance(detail, list):
            return "; ".join(self._formatear_error(v) for v in detail)
        return str(detail)
