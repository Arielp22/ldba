# armenia/serializers/__init__.py
from .auth import CustomTokenSerializer, CustomTokenView
from .user import (
    RegisterSerializer,
    UserSerializer,
    UserProfileSerializer,
    ChangePasswordSerializer,
)

# Bloque 1: Configuración base
from .temporada import TemporadaSerializer
from .categoria import CategoriaSerializer
from .equipo import EquipoSerializer, EquipoTemporadaCategoriaSerializer

# Bloque 2: Jugadores y capitanes
from .jugador import (
    JugadorSerializer,
    JugadorCalificacionSerializer,
    JugadorEquipoTemporadaSerializer,
    JugadorEquipoTemporadaCreateSerializer,
    CapitanEquipoTemporadaSerializer,
)

# Bloque 3: Jornadas y partidos
from .jornada import (JornadaSerializer,PartidoSerializer,
                      PartidoResultadoSerializer,)

# Bloque 4: Vocalias
from .vocalia import (
    VocaliaSerializer,
    VocaliaJugadorSerializer,
    VocaliaRechazoSerializer,
)

# Bloque 5: Sanciones
from .sancion import (
    SancionSerializer,
    HistorialSancionSerializer,
    MultaSerializer,
    ReciboSerializer,
)

# Bloque 6: Finanzas
from .finanza import (
    MovimientoFinancieroSerializer,
    InformeFinancieroSemanalSerializer,
)

# Bloque 7: Lesiones
from .lesion import (
    LesionSerializer,
    LesionCambioEstadoSerializer,
)

__all__ = [
    # Auth
    "CustomTokenSerializer",
    "CustomTokenView",
    
    # User
    "RegisterSerializer",
    "UserSerializer",
    "UserProfileSerializer",
    "ChangePasswordSerializer",

    # Configuración base
    "TemporadaSerializer",
    "CategoriaSerializer",
    "EquipoSerializer",
    "EquipoTemporadaCategoriaSerializer",

    # Jugadores y capitanes
    "JugadorSerializer",
    "JugadorEquipoTemporadaSerializer",
    "CapitanEquipoTemporadaSerializer",

    # Jornadas y partidos
    "JornadaSerializer",
    "PartidoSerializer",
    "PartidoResultadoSerializer",   

    # Vocalias
    "VocaliaSerializer",
    "VocaliaJugadorSerializer",
    "VocaliaRechazoSerializer",

    # Sanciones
    "SancionSerializer",
    "HistorialSancionSerializer",
    "MultaSerializer",
    "ReciboSerializer",

    # Finanzas
    "MovimientoFinancieroSerializer",
    "InformeFinancieroSemanalSerializer",

    # Lesiones
    "LesionSerializer",
    "LesionCambioEstadoSerializer",
]