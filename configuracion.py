"""
configuracion.py
==============================================================================
Archivo central para configurar TODAS las texturas del juego.

Aquí solo tienes que escribir las rutas de tus carpetas/imágenes. Las
funciones de carga (al final del archivo) se encargan de leerlas y
convertirlas en algo que main.py pueda usar. Si una carpeta no existe o
está vacía, el juego NO se rompe: simplemente no habrá sprite ahí y podrás
seguir usando las figuras de colores mientras consigues el arte.

------------------------------------------------------------------------------
ESTRUCTURA DE CARPETAS QUE ESPERA ESTE ARCHIVO (puedes cambiarla más abajo)
------------------------------------------------------------------------------
assets/
├── jugador/
│   ├── idle/        -> frame_1.png, frame_2.png, ...
│   ├── correr/      -> frame_1.png, frame_2.png, ...
│   ├── saltar/      -> frame_1.png, ...
│   └── caer/        -> frame_1.png, ...
│   (los sprites se dibujan mirando a la DERECHA; el juego los voltea
│    automáticamente cuando el jugador mira a la izquierda)
│
├── niveles/
│   ├── nivel_1/
│   │   ├── fondo.png
│   │   └── bloques/
│   │       ├── plataforma.png
│   │       └── pincho.png
│   ├── nivel_2/  (misma estructura, con TU propia textura de hielo, etc.)
│   ├── nivel_3/
│   ├── nivel_4/
│   └── nivel_5/
│
├── enemigos/
│   └── default/            -> puedes agregar más "tipos" (ver abajo)
│       ├── normal/         -> frame_1.png, frame_2.png, ...
│       └── congelado/      -> frame_1.png, frame_2.png, ...
│
└── monedas/
    └── moneda/              -> frame_1.png, frame_2.png, ... (animación de giro)

No necesitas crear TODAS las carpetas ahora mismo: agrega imágenes poco a
poco y el juego las irá tomando.
==============================================================================
"""

import os
import pygame

BASE_ASSETS = "assets"

EXTENSIONES_VALIDAS = (".png", ".jpg", ".jpeg", ".bmp", ".gif", ".webp")


# ==============================================================================
# 1. SPRITES DEL JUGADOR
# ==============================================================================
# Una carpeta por movimiento/animación. Agrega o quita estados según lo que
# necesites (por ejemplo "disparar", "agachado", "escalar", etc.)
SPRITES_JUGADOR = {
    "idle":   f"{BASE_ASSETS}/jugador/idle",
    "correr": f"{BASE_ASSETS}/jugador/correr",
    "saltar": f"{BASE_ASSETS}/jugador/saltar",
    "caer":   f"{BASE_ASSETS}/jugador/caer",
}

VELOCIDAD_ANIMACION_JUGADOR = 100  # milisegundos entre cada frame


# ==============================================================================
# 2. TEXTURAS POR NIVEL (bloques y fondo INDEPENDIENTES para cada nivel)
# ==============================================================================
# El diccionario "bloques" mapea el carácter del mapa de texto (en NIVELES,
# dentro de main.py) con la imagen que le corresponde:
#   "T" -> plataforma normal
#   "S" -> pincho / trampa
# Agrega más claves si en el futuro usas más símbolos en el mapa.
TEXTURAS_NIVELES = [
    {  # Nivel 1: Mundo del Volcán
        "fondo": f"{BASE_ASSETS}/niveles/nivel_1/fondo.png",
        "bloques": {
            "T": f"{BASE_ASSETS}/niveles/nivel_1/bloques/plataforma.png",
            "S": f"{BASE_ASSETS}/niveles/nivel_1/bloques/pincho.png",
        },
    },
    {  # Nivel 2: Cavernas de Hielo
        "fondo": f"{BASE_ASSETS}/niveles/nivel_2/fondo.png",
        "bloques": {
            "T": f"{BASE_ASSETS}/niveles/nivel_2/bloques/plataforma.png",
            "S": f"{BASE_ASSETS}/niveles/nivel_2/bloques/pincho.png",
        },
    },
    {  # Nivel 3: Bosque de Piedra
        "fondo": f"{BASE_ASSETS}/niveles/nivel_3/fondo.png",
        "bloques": {
            "T": f"{BASE_ASSETS}/niveles/nivel_3/bloques/plataforma.png",
            "S": f"{BASE_ASSETS}/niveles/nivel_3/bloques/pincho.png",
        },
    },
    {  # Nivel 4: Cumbres del Viento
        "fondo": f"{BASE_ASSETS}/niveles/nivel_4/fondo.png",
        "bloques": {
            "T": f"{BASE_ASSETS}/niveles/nivel_4/bloques/plataforma.png",
            "S": f"{BASE_ASSETS}/niveles/nivel_4/bloques/pincho.png",
        },
    },
    {  # Nivel 5: El Desafío Final
        "fondo": f"{BASE_ASSETS}/niveles/nivel_5/fondo.png",
        "bloques": {
            "T": f"{BASE_ASSETS}/niveles/nivel_5/bloques/plataforma.png",
            "S": f"{BASE_ASSETS}/niveles/nivel_5/bloques/pincho.png",
        },
    },
]


# ==============================================================================
# 3. SPRITES DE ENEMIGOS (con variantes y estado "congelado")
# ==============================================================================
# Puedes definir cuantos "tipos" de enemigo quieras (por ejemplo para tener
# enemigos distintos en cada nivel). Cada tipo tiene su propia animación
# "normal" y su propia animación "congelado" (se usa cuando le pega un
# proyectil de Hielo). Si no defines "congelado", el juego reutiliza la
# animación "normal" pintada con un tinte azulado.
SPRITES_ENEMIGOS = {
    "default": {
        "normal":    f"{BASE_ASSETS}/enemigos/default/normal",
        "congelado": f"{BASE_ASSETS}/enemigos/default/congelado",
    },
    # Ejemplo de cómo agregar más variantes de enemigo por nivel/tema:
    # "volcan": {
    #     "normal":    f"{BASE_ASSETS}/enemigos/volcan/normal",
    #     "congelado": f"{BASE_ASSETS}/enemigos/volcan/congelado",
    # },
    # "hielo": {
    #     "normal":    f"{BASE_ASSETS}/enemigos/hielo/normal",
    #     "congelado": f"{BASE_ASSETS}/enemigos/hielo/congelado",
    # },
}

# Qué tipo de enemigo usar en cada nivel (índice de NIVELES en main.py).
# Si un nivel no aparece aquí, se usa "default".
TIPO_ENEMIGO_POR_NIVEL = {
    0: "default",
    1: "default",
    2: "default",
    3: "default",
    4: "default",
}

VELOCIDAD_ANIMACION_ENEMIGO = 150  # ms entre frames (animación normal)
VELOCIDAD_ANIMACION_ENEMIGO_CONGELADO = 400  # más lento cuando está congelado


# ==============================================================================
# 4. MONEDAS
# ==============================================================================
SPRITES_MONEDA = f"{BASE_ASSETS}/monedas/moneda"
VELOCIDAD_ANIMACION_MONEDA = 120  # ms entre frames


# ==============================================================================
# FUNCIONES DE CARGA (no necesitas tocar nada de aquí para abajo)
# ==============================================================================
_avisos_mostrados = set()


def _avisar_una_vez(mensaje):
    """Evita llenar la consola con el mismo aviso repetido cada frame."""
    if mensaje not in _avisos_mostrados:
        print(mensaje)
        _avisos_mostrados.add(mensaje)


def cargar_imagen(ruta, tamano=None):
    """
    Carga una sola imagen desde disco. Si no existe, devuelve None
    (así main.py puede decidir usar su dibujo de respaldo/color).
    """
    if not ruta or not os.path.isfile(ruta):
        _avisar_una_vez(f"[configuracion] Aviso: no se encontró la imagen '{ruta}'.")
        return None

    try:
        imagen = pygame.image.load(ruta)
        try:
            imagen = imagen.convert_alpha()
        except pygame.error:
            pass  # display aún no inicializado; se usa la imagen sin convertir

        if tamano:
            imagen = pygame.transform.smoothscale(imagen, tamano)
        return imagen
    except pygame.error as error:
        _avisar_una_vez(f"[configuracion] Error cargando '{ruta}': {error}")
        return None


def cargar_carpeta_animacion(carpeta, tamano=None):
    """
    Carga todas las imágenes de una carpeta (ordenadas alfabéticamente) como
    los frames de una animación. Devuelve una lista de Surfaces, o una lista
    vacía si la carpeta no existe o no tiene imágenes válidas.
    """
    if not carpeta or not os.path.isdir(carpeta):
        _avisar_una_vez(f"[configuracion] Aviso: no se encontró la carpeta '{carpeta}'.")
        return []

    archivos = sorted(
        f for f in os.listdir(carpeta)
        if f.lower().endswith(EXTENSIONES_VALIDAS)
    )

    frames = []
    for archivo in archivos:
        imagen = cargar_imagen(os.path.join(carpeta, archivo), tamano)
        if imagen is not None:
            frames.append(imagen)

    if not frames:
        _avisar_una_vez(f"[configuracion] Aviso: la carpeta '{carpeta}' no tiene imágenes.")

    return frames


def cargar_animaciones_jugador(tamano=None):
    """
    Devuelve un diccionario { "idle": [frames...], "correr": [frames...], ... }
    listo para usar en la clase Jugador.
    """
    return {
        estado: cargar_carpeta_animacion(ruta, tamano)
        for estado, ruta in SPRITES_JUGADOR.items()
    }


def cargar_texturas_nivel(indice_nivel, tamano_bloque=None):
    """
    Devuelve { "fondo": Surface|None, "bloques": {"T": Surface|None, "S": Surface|None} }
    para el nivel indicado.
    """
    if indice_nivel < 0 or indice_nivel >= len(TEXTURAS_NIVELES):
        return {"fondo": None, "bloques": {}}

    datos = TEXTURAS_NIVELES[indice_nivel]
    fondo = cargar_imagen(datos.get("fondo"))
    bloques = {
        simbolo: cargar_imagen(ruta, tamano_bloque)
        for simbolo, ruta in datos.get("bloques", {}).items()
    }
    return {"fondo": fondo, "bloques": bloques}


def cargar_animaciones_enemigo(tipo="default", tamano=None):
    """
    Devuelve { "normal": [frames...], "congelado": [frames...] } para el
    tipo de enemigo pedido. Si el tipo no existe, usa "default".
    """
    datos = SPRITES_ENEMIGOS.get(tipo, SPRITES_ENEMIGOS.get("default", {}))
    normal = cargar_carpeta_animacion(datos.get("normal"), tamano)
    congelado = cargar_carpeta_animacion(datos.get("congelado"), tamano)

    # Si no hay animación de congelado, reutiliza la normal como respaldo.
    if not congelado:
        congelado = normal

    return {"normal": normal, "congelado": congelado}


def obtener_tipo_enemigo_para_nivel(indice_nivel):
    """Devuelve el nombre del tipo de enemigo configurado para ese nivel."""
    return TIPO_ENEMIGO_POR_NIVEL.get(indice_nivel, "default")


def cargar_animacion_moneda(tamano=None):
    """Devuelve la lista de frames de la animación de la moneda."""
    return cargar_carpeta_animacion(SPRITES_MONEDA, tamano)


def obtener_frame_actual(frames, tiempo_inicio_animacion, velocidad_ms):
    """
    Utilidad para animar: dado un tiempo de referencia (por ejemplo
    pygame.time.get_ticks() de cuando empezó el estado actual) y la lista
    de frames, devuelve la Surface que corresponde mostrar ahora mismo.
    Devuelve None si la lista está vacía.
    """
    if not frames:
        return None
    tiempo_transcurrido = pygame.time.get_ticks() - tiempo_inicio_animacion
    indice = (tiempo_transcurrido // velocidad_ms) % len(frames)
    return frames[indice]
