from .temporada import Temporada
from .categoria import Categoria
from .equipo import Equipo, EquipoTemporadaCategoria
from .jugador import Jugador, JugadorEquipoTemporada, CapitanEquipoTemporada
from .jornada import Jornada, Partido
from .vocalia import Vocalia, VocaliaJugador




__all__ = ["Temporada", "Categoria", "Equipo",
            "EquipoTemporadaCategoria", "Jugador",
            "JugadorEquipoTemporada", "CapitanEquipoTemporada", 
            "Jornada", "Partido", "Vocalia", "VocaliaJugador"]

