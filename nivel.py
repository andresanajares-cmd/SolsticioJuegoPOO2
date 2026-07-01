"""
nivel.py
--------
Clase Nivel, segun el GDD (seccion 2.3): "Nivel esta en composicion con
Juego (rombo relleno). Contiene listas de entidades por nivel."

Los niveles se "dibujan" con un mapa de texto: cada fila del nivel es un
string donde cada caracter representa una casilla de la cuadricula.
    'P' = hay una plataforma en esa casilla
    '.' = espacio vacio (no hay nada)

Esto es mucho mas facil de visualizar y editar que calcular coordenadas
en pixeles a mano: el mapa de texto ES el dibujo del nivel.
"""

from entidades import Plataforma


# Tamano de cada casilla de la cuadricula, en pixeles.
TILE_ANCHO = 40
TILE_ALTO = 40
GROSOR_PLATAFORMA = 20  # que tan "delgada" se ve cada plataforma


def parsear_mapa(mapa, tile_ancho=TILE_ANCHO, tile_alto=TILE_ALTO, grosor=GROSOR_PLATAFORMA):
    """
    Convierte un mapa de texto (lista de strings) en una lista de tuplas
    (x, y, ancho, alto) para crear plataformas.

    Las 'P' consecutivas en una misma fila se combinan en una sola
    plataforma ancha, en vez de crear una plataforma diminuta por cada
    casilla.
    """
    datos_plataformas = []

    for fila_idx, fila in enumerate(mapa):
        col = 0
        while col < len(fila):
            if fila[col] == 'P':
                inicio_col = col
                while col < len(fila) and fila[col] == 'P':
                    col += 1
                cantidad_casillas = col - inicio_col

                x = inicio_col * tile_ancho
                y = fila_idx * tile_alto
                ancho = cantidad_casillas * tile_ancho

                datos_plataformas.append((x, y, ancho, grosor))
            else:
                col += 1

    return datos_plataformas


class Nivel:
    """
    Representa un escenario/zona del juego (ej: "Volcan de Fuego").

    Guarda las entidades propias del nivel -por ahora, plataformas- y
    sabe dibujarlas. El Juego (controlador general) sera quien tenga un
    Nivel activo en composicion.
    """

    def __init__(self, nombre: str, mapa):
        self.nombre = nombre
        datos_plataformas = parsear_mapa(mapa)
        self.plataformas = [
            Plataforma(x, y, ancho, alto)
            for (x, y, ancho, alto) in datos_plataformas
        ]

    def dibujar(self, pantalla):
        for plataforma in self.plataformas:
            plataforma.dibujar(pantalla)


# ---------------------------------------------------------------------
# Mapa del Nivel 1: Volcan de Fuego (GDD, tabla de niveles).
#
# Cada fila = una franja horizontal de 40px. Cada columna = 40px.
# Pon una 'P' donde quieras que exista una plataforma; el resto son
# puntos '.' (vacio). Para modificar el nivel, edita este dibujo
# directamente: agrega, quita o mueve las 'P'.
#
# La ventana mide 800x600 y el suelo ocupa los ultimos 80px, asi que
# hay espacio util de 20 columnas x 13 filas (20*40=800, 13*40=520).
# ---------------------------------------------------------------------
MAPA_NIVEL_1 = [
    ".....................................",  # 0
    ".....................................",  # 1
    ".....................................",  # 2
    "......PPP............................",  # 3
    ".....................................",  # 4
    ".............PPPP....................",  # 5
    ".....................................",  # 6
    "..PPP................................",  # 7
    ".....................................",  # 8
    "......................PPP............",  # 9
    ".....................................",  # 10
    "............PPPPP....................",  # 11
    ".....................................",  # 12
    ".........................PP..........",  # 13
    ".....................................",  # 14
    "..............................PPPP...",  # 15
      # 16 (suelo)
]

def crear_nivel_1() -> Nivel:
    """Fabrica el Nivel 1 a partir de su mapa de texto."""
    return Nivel("Volcan de Fuego", MAPA_NIVEL_1)
