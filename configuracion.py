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
│   ├── volcan/              -> "tipo" de enemigo usado en el Nivel 1
│   │   ├── normal/          -> frame_1.png, ... (enemigo patrulla normal)
│   │   ├── congelado/       -> frame_1.png, ... (patrulla congelado por Hielo)
│   │   ├── tirador/         -> frame_1.png, ... (enemigo que dispara)
│   │   └── tirador_congelado/ -> frame_1.png, ... (tirador congelado)
│   ├── hielo/               -> "tipo" usado en el Nivel 2 (misma estructura)
│   ├── bosque/              -> "tipo" usado en el Nivel 3 (misma estructura)
│   ├── viento/              -> "tipo" usado en el Nivel 4 (misma estructura)
│   ├── final/                -> "tipo" usado en el Nivel 5 (misma estructura)
│   └── default/             -> se usa si un nivel no tiene tipo asignado
│       ├── normal/
│       ├── congelado/
│       ├── tirador/
│       └── tirador_congelado/
│
├── monedas/
│   └── moneda/              -> frame_1.png, frame_2.png, ... (animación de giro)
│
├── puerta/
│   └── frame_1.png, frame_2.png, ...  (animación de la puerta de fin de nivel;
│       si solo pones 1 imagen, se mostrará fija sin animar)
│
└── proyectiles/
    ├── fuego/               -> frame_1.png, ... (proyectil del poder Fuego)
    ├── hielo/               -> frame_1.png, ... (proyectil del poder Hielo)
    ├── piedra/              -> frame_1.png, ... (proyectil del poder Piedra)
    ├── viento/              -> frame_1.png, ... (proyectil del poder Viento)
    └── enemigo/             -> frame_1.png, ... (proyectil del enemigo Tirador)
    (igual que el jugador, se dibujan mirando a la DERECHA y el juego los
     voltea automáticamente cuando van hacia la izquierda)

No necesitas crear TODAS las carpetas ahora mismo: agrega imágenes poco a
poco y el juego las irá tomando. Si un tipo de proyectil no tiene carpeta
o está vacía, el juego sigue dibujando el círculo/rectángulo de color de
siempre para ese proyectil.
------------------------------------------------------------------------------
ESTRUCTURA DE SONIDOS QUE ESPERA ESTE ARCHIVO
------------------------------------------------------------------------------
assets/
└── sonidos/
    ├── moneda.wav          -> se reproduce al tomar una moneda
    ├── vida_extra.wav      -> se reproduce al ganar una vida extra (cada 10
    │                          monedas)
    ├── dano.wav            -> se reproduce cuando el jugador recibe daño y
    │                          reaparece en el punto de inicio del nivel
    │                          (junto con las partículas verdes)
    ├── puerta.wav          -> se reproduce al tocar la puerta de fin de nivel
    ├── muerte.wav          -> se reproduce cuando se acaban las vidas (Game Over)
    └── musica_fondo.mp3    -> música que suena en bucle durante todo el juego

Igual que con las imágenes: si un archivo de sonido no existe, el juego NO
se rompe, simplemente no habrá sonido ahí (y se imprime un aviso una sola
vez en la consola).
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
    "dano":   f"{BASE_ASSETS}/jugador/dano"
}

VELOCIDAD_ANIMACION_JUGADOR = 80  # milisegundos entre cada frame


# ==============================================================================
# 2. TEXTURAS POR NIVEL (bloques y fondo INDEPENDIENTES para cada nivel)
# ==============================================================================
# El diccionario "bloques" mapea el carácter del mapa de texto (en NIVELES,
# dentro de main.py) con la imagen que le corresponde:s
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
# 3. SPRITES DE ENEMIGOS (patrulla + tirador, cada uno con variante "congelado")
# ==============================================================================
# Puedes definir cuantos "tipos" de enemigo quieras (uno por nivel/tema, por
# ejemplo). Cada tipo tiene CUATRO animaciones posibles:
#   "normal"             -> enemigo patrulla (el de siempre) caminando
#   "congelado"          -> enemigo patrulla congelado por un proyectil de Hielo
#   "tirador"             -> enemigo que dispara proyectiles al jugador
#   "tirador_congelado"  -> enemigo tirador congelado por un proyectil de Hielo
# Si "congelado" o "tirador_congelado" no existen, el juego reutiliza la
# animación normal correspondiente pintada con un tinte azulado.
# Si "tirador" no existe, el juego reutiliza el sprite "normal" del mismo tipo.
SPRITES_ENEMIGOS = {
    "volcan": {  # Nivel 1
        "normal":            f"{BASE_ASSETS}/enemigos/volcan/normal",
        "congelado":         f"{BASE_ASSETS}/enemigos/volcan/congelado",
        "tirador":           f"{BASE_ASSETS}/enemigos/volcan/tirador",
        "tirador_congelado": f"{BASE_ASSETS}/enemigos/volcan/tirador_congelado",
    },
    "hielo": {  # Nivel 2
        "normal":            f"{BASE_ASSETS}/enemigos/hielo/normal",
        "congelado":         f"{BASE_ASSETS}/enemigos/hielo/congelado",
        "tirador":           f"{BASE_ASSETS}/enemigos/hielo/tirador",
        "tirador_congelado": f"{BASE_ASSETS}/enemigos/hielo/tirador_congelado",
    },
    "bosque": {  # Nivel 3
        "normal":            f"{BASE_ASSETS}/enemigos/bosque/normal",
        "congelado":         f"{BASE_ASSETS}/enemigos/bosque/congelado",
        "tirador":           f"{BASE_ASSETS}/enemigos/bosque/tirador",
        "tirador_congelado": f"{BASE_ASSETS}/enemigos/bosque/tirador_congelado",
    },
    "viento": {  # Nivel 4
        "normal":            f"{BASE_ASSETS}/enemigos/viento/normal",
        "congelado":         f"{BASE_ASSETS}/enemigos/viento/congelado",
        "tirador":           f"{BASE_ASSETS}/enemigos/viento/tirador",
        "tirador_congelado": f"{BASE_ASSETS}/enemigos/viento/tirador_congelado",
    },
    "final": {  # Nivel 5
        "normal":            f"{BASE_ASSETS}/enemigos/final/normal",
        "congelado":         f"{BASE_ASSETS}/enemigos/final/congelado",
        "tirador":           f"{BASE_ASSETS}/enemigos/final/tirador",
        "tirador_congelado": f"{BASE_ASSETS}/enemigos/final/tirador_congelado",
    },
    "default": {  # respaldo si un nivel no tiene tipo asignado
        "normal":            f"{BASE_ASSETS}/enemigos/default/normal",
        "congelado":         f"{BASE_ASSETS}/enemigos/default/congelado",
        "tirador":           f"{BASE_ASSETS}/enemigos/default/tirador",
        "tirador_congelado": f"{BASE_ASSETS}/enemigos/default/tirador_congelado",
    },
}

# Qué tipo de enemigo (y por lo tanto qué carpeta de texturas) usar en cada
# nivel (índice de NIVELES en main.py). Como cada tipo es independiente,
# cada nivel puede tener su propio arte tanto para el enemigo patrulla como
# para el enemigo tirador. Si un nivel no aparece aquí, se usa "default".
TIPO_ENEMIGO_POR_NIVEL = {
    0: "default",
    1: "default",
    2: "default",
    3: "default",
    4: "default",
}

VELOCIDAD_ANIMACION_ENEMIGO = 50  # ms entre frames (animación normal)
VELOCIDAD_ANIMACION_ENEMIGO_CONGELADO = 400  # más lento cuando está congelado
VELOCIDAD_ANIMACION_TIRADOR = 150  # ms entre frames del enemigo tirador


# ==============================================================================
# 4. MONEDAS
# ==============================================================================
SPRITES_MONEDA = f"{BASE_ASSETS}/monedas/moneda"
VELOCIDAD_ANIMACION_MONEDA = 120  # ms entre frames


# ==============================================================================
# 4b. PUERTA (fin de nivel)
# ==============================================================================
# Carpeta con los frames de la animación de la puerta (por ejemplo, un brillo
# o un portal pulsante). Si solo hay una imagen, se mostrará fija sin animar.
SPRITES_PUERTA = f"{BASE_ASSETS}/puerta"
VELOCIDAD_ANIMACION_PUERTA = 150  # ms entre frames


# ==============================================================================
# 5. PROYECTILES (uno por tipo de poder, más el del enemigo Tirador)
# ==============================================================================
# Igual que con los enemigos: si una carpeta no tiene imágenes, el juego
# sigue dibujando el círculo/rectángulo de color de siempre para ese
# proyectil, así que puedes ir agregando arte de a poco.
SPRITES_PROYECTILES = {
    "Fuego":   f"{BASE_ASSETS}/proyectiles/fuego",
    "Hielo":   f"{BASE_ASSETS}/proyectiles/hielo",
    "Piedra":  f"{BASE_ASSETS}/proyectiles/piedra",
    "Viento":  f"{BASE_ASSETS}/proyectiles/viento",
    "Enemigo": f"{BASE_ASSETS}/proyectiles/enemigo",
}

VELOCIDAD_ANIMACION_PROYECTIL = 90  # ms entre cada frame


# ==============================================================================
# 6. SONIDOS
# ==============================================================================
# Sonidos cortos (efectos). Agrega la ruta de tu archivo de sonido para cada
# evento. Formatos recomendados: .wav u .ogg (más compatibles que .mp3 para
# efectos cortos). Si un archivo no existe, ese evento simplemente queda en
# silencio, el juego no se rompe.
BASE_SONIDOS = f"{BASE_ASSETS}/sonidos"

SONIDOS = {
    "moneda":     f"{BASE_SONIDOS}/moneda.wav",      # al tomar una moneda
    "vida_extra": f"{BASE_SONIDOS}/vida_extra.wav",  # al ganar una vida extra
    "dano":       f"{BASE_SONIDOS}/dano.wav",        # al recibir daño / reaparecer
    "puerta":     f"{BASE_SONIDOS}/puerta.wav",      # al tocar la puerta de fin de nivel
    "muerte":     f"{BASE_SONIDOS}/muerte.wav",      # al quedarse sin vidas (Game Over)
}

VOLUMEN_EFECTOS = 0.6  # volumen de los sonidos de arriba (0.0 a 1.0)

# Música de fondo: se reproduce en bucle mientras se está jugando.
# Formato recomendado: .mp3 u .ogg.
MUSICA_FONDO = f"{BASE_SONIDOS}/musica_fondo.mp3"
VOLUMEN_MUSICA_FONDO = 0.4  # volumen de la música de fondo (0.0 a 1.0)


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


def cargar_miniaturas_niveles(tamano=None):
    """
    Devuelve una lista de Surfaces (o None si no se encontró el archivo) con
    una versión en miniatura del fondo de cada nivel, en el mismo orden que
    TEXTURAS_NIVELES / NIVELES. Se usa para mostrar una previsualización de
    cada nivel (su imagen de fondo) en el menú de selección de nivel.

    Como solo se usa como decoración pequeña en el menú, se carga una sola
    vez al iniciar el juego (no cada vez que se entra al menú).
    """
    return [cargar_imagen(datos.get("fondo"), tamano) for datos in TEXTURAS_NIVELES]


def cargar_animaciones_enemigo(tipo="default", tamano=None):
    """
    Devuelve { "normal": [...], "congelado": [...], "tirador": [...],
    "tirador_congelado": [...] } para el tipo de enemigo pedido. Si el tipo
    no existe, usa "default". Los estados sin arte propio se rellenan con
    un respaldo razonable (ver comentarios abajo) para que el juego nunca
    se rompa por falta de imágenes.
    """
    datos = SPRITES_ENEMIGOS.get(tipo, SPRITES_ENEMIGOS.get("default", {}))
    normal = cargar_carpeta_animacion(datos.get("normal"), tamano)
    congelado = cargar_carpeta_animacion(datos.get("congelado"), tamano)
    tirador = cargar_carpeta_animacion(datos.get("tirador"), tamano)
    tirador_congelado = cargar_carpeta_animacion(datos.get("tirador_congelado"), tamano)

    # Si no hay animación de congelado, reutiliza la normal como respaldo.
    if not congelado:
        congelado = normal

    # Si no hay arte propio para el tirador, reutiliza el enemigo normal.
    if not tirador:
        tirador = normal
    if not tirador_congelado:
        tirador_congelado = congelado if congelado else tirador

    return {
        "normal": normal,
        "congelado": congelado,
        "tirador": tirador,
        "tirador_congelado": tirador_congelado,
    }


def cargar_animaciones_proyectiles(tamanos=None):
    """
    Devuelve { "Fuego": [frames...], "Hielo": [frames...], ... } listo para
    usar en la clase Proyectil. Si un tipo no tiene carpeta o está vacía,
    su lista queda vacía y main.py usará su dibujo de respaldo (círculo o
    rectángulo de color) para ese proyectil.

    tamanos: diccionario opcional { "Fuego": (ancho, alto), ... } para
    escalar cada tipo de proyectil a su propio tamaño (normalmente el de
    su rect de colisión). Si no se especifica un tamaño para un tipo, la
    imagen se carga a su tamaño original.
    """
    tamanos = tamanos or {}
    return {
        tipo: cargar_carpeta_animacion(ruta, tamanos.get(tipo))
        for tipo, ruta in SPRITES_PROYECTILES.items()
    }


def obtener_tipo_enemigo_para_nivel(indice_nivel):
    """Devuelve el nombre del tipo de enemigo configurado para ese nivel."""
    return TIPO_ENEMIGO_POR_NIVEL.get(indice_nivel, "default")


def cargar_animacion_moneda(tamano=None):
    """Devuelve la lista de frames de la animación de la moneda."""
    return cargar_carpeta_animacion(SPRITES_MONEDA, tamano)


def cargar_animacion_puerta(tamano=None):
    """Devuelve la lista de frames de la animación de la puerta de fin de nivel."""
    return cargar_carpeta_animacion(SPRITES_PUERTA, tamano)


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


# ==============================================================================
# FUNCIONES DE SONIDO (no necesitas tocar nada de aquí para abajo)
# ==============================================================================
def cargar_sonido(ruta, volumen=1.0):
    """
    Carga un efecto de sonido corto (pygame.mixer.Sound) desde disco. Si no
    existe o el mezclador de audio no está disponible, devuelve None (así
    main.py puede simplemente no reproducir nada para ese evento).
    """
    if not ruta or not os.path.isfile(ruta):
        _avisar_una_vez(f"[configuracion] Aviso: no se encontró el sonido '{ruta}'.")
        return None

    try:
        sonido = pygame.mixer.Sound(ruta)
        sonido.set_volume(volumen)
        return sonido
    except pygame.error as error:
        _avisar_una_vez(f"[configuracion] Error cargando sonido '{ruta}': {error}")
        return None


def cargar_sonidos_efectos(volumen=None):
    """
    Devuelve un diccionario { "moneda": Sound|None, "vida_extra": Sound|None }
    listo para usar en main.py (sonido.play() cuando ocurra el evento).
    """
    volumen = VOLUMEN_EFECTOS if volumen is None else volumen
    return {
        nombre: cargar_sonido(ruta, volumen)
        for nombre, ruta in SONIDOS.items()
    }


def reproducir_musica_fondo(volumen=None, loops=-1):
    """
    Carga y reproduce en bucle infinito (loops=-1) la música de fondo
    definida en MUSICA_FONDO. Si el archivo no existe, no hace nada y
    devuelve False (el juego sigue funcionando sin música).
    """
    volumen = VOLUMEN_MUSICA_FONDO if volumen is None else volumen

    if not MUSICA_FONDO or not os.path.isfile(MUSICA_FONDO):
        _avisar_una_vez(f"[configuracion] Aviso: no se encontró la música de fondo '{MUSICA_FONDO}'.")
        return False

    try:
        pygame.mixer.music.load(MUSICA_FONDO)
        pygame.mixer.music.set_volume(volumen)
        pygame.mixer.music.play(loops)
        return True
    except pygame.error as error:
        _avisar_una_vez(f"[configuracion] Error cargando música de fondo: {error}")
        return False
