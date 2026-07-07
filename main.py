import pygame
import sys
import configuracion as config

# ==============================================================================
# CONFIGURACIÓN INICIAL Y CONSTANTES
# ==============================================================================
pygame.init()

ANCHO, ALTO = 900, 700
PANTALLA = pygame.display.set_mode((ANCHO, ALTO))
pygame.display.set_caption("Plataformas - Poderes Elementales")
RELOJ = pygame.time.Clock()
FPS = 60

# Tamaños con los que se escala cada sprite (deben coincidir con los rects
# de colisión que ya usa el juego, para que la textura calce con la caja).
TAMANO_JUGADOR = (30, 30)
TAMANO_ENEMIGO = (30, 30)
TAMANO_MONEDA = (20, 20)

# Sprites que NO cambian por nivel: se cargan una sola vez al iniciar.
ANIMACIONES_JUGADOR = config.cargar_animaciones_jugador(TAMANO_JUGADOR)
ANIMACION_MONEDA = config.cargar_animacion_moneda(TAMANO_MONEDA)

# Sprites que SÍ cambian por nivel (bloques, fondo, enemigos). Se actualizan
# cada vez que se llama a cargar_nivel().
TEXTURAS_NIVEL_ACTUAL = {"fondo": None, "bloques": {}}
ANIMACIONES_ENEMIGO_ACTUAL = {"normal": [], "congelado": []}

# Colores (RGB)
NEGRO = (0, 0, 0)
BLANCO = (255, 255, 255)
AZUL_CIELO = (135, 206, 235)
VERDE = (34, 139, 34)
ROJO = (220, 20, 60)
AMARILLO = (255, 215, 0)
CAFE = (139, 69, 19)
GRIS = (105, 105, 105)
MORADO = (138, 43, 226)

# Colores de Proyectiles
C_FUEGO = (255, 69, 0)
C_HIELO = (0, 255, 255)
C_PIEDRA = (169, 169, 169)
C_VIENTO = (240, 255, 255)

TAMANO_TILE = 40

FUENTE_UI = pygame.font.SysFont("Arial", 18, bold=True)
FUENTE_TITULO = pygame.font.SysFont("Arial", 50, bold=True)

NOMBRES_NIVELES = [
    "1: Mundo del Volcán",
    "2: Cavernas de Hielo",
    "3: Bosque de Piedra",
    "4: Cumbres del Viento",
    "5: El Desafío Final"
]

# ==============================================================================
# DISEÑO DE LOS 5 NIVELES
# ==============================================================================
NIVELES = [
    # Nivel 1 (Mundo del Volcán)
    [   "                                        ",
        "                                        ",
        "                                        ",
        "                                        ",
        "                                        ",
        "                                        ",
        "                                       D",
        "         C C           C             TTT",
        "        TTTTT         TTT               ",
        "                                        ",
        "    T               T        T          ",
        "       C   C                            ",
        "  TTTTTTTTTTTT    TTT      TT      TTT  ",
        "                                        ",
        "                                  E     ",
        "@                                TTTTT  ",
        "TTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTT"
    ],
    # Nivel 2 (Cavernas de Hielo)
    [   "                                        ",
        "                                        ",
        "                                        ",
        "                                        ",
        "                                       D",
        "                                      TT",
        "                                     T  ",
        "      C C   T       C C     T       T   ",
        "     TTTTT T       TTTTT   TT      T    ",
        "                                        ",
        "  C                 C             T     ",
        " TTT       C C     TTT     C            ",
        "          TTTTT           TT            ",
        "               T                 T      ",
        "       C       T   E           C T      ",
        "@   TTTTT SSSSS TTTTTTTT    TTTTTT SSS  ",
        "TTTT     TTTTTTT        TTTT      TTTTTT"
    ],
    # Nivel 3 (Bosque de Piedra)
    [   "                                        ",
        "                                        ",
        "                                        ",
        "                                       D",
        "        TTT                           TT",
        "                                        ",
        "      T     T             C       T     ",
        "                         TTT            ",
        "    T  C C C  T   T  E  T       T       ",
        "       TTTTT       TTTTT                ",
        "  T           T                 T       ",
        "                                        ",
        "    C       C       C               C   ",
        "   TT       TT     TT  E           TT   ",
        "       S S             TTT     S        ",
        "@ TTT TTTTTTT TTT TTT         TTT TTT   ",
        "TT   T       T   T   TTTTTTTTT   T   TTT"
    ],
    # Nivel 4 (Cumbres del Viento)
    [   "                                        ",
        "                                        ",
        "                                        ",
        "                                        ",
        "D                                       ",
        "TT                                      ",
        "                                        ",
        "  T   C                                 ",
        "      T   C             T  E  T         ",
        "          T         C C  TTTTT          ",
        "              T     TTT        T        ",
        "            C                  T        ",
        "          TTT                  T        ",
        "      TTT             C C  E   T        ",
        "  TTT                TTTTTTTTTT         ",
        "@                E                     T",
        "TTSSSSSSSSSSSSSSSTTTTTTTSSSSSSSSSSSSTTTT"
    ],
    # Nivel 5 (El Desafío Final)
    [   "                                        ",
        "                                        ",
        "                                        ",
        "                                        ",
        "                                       D",
        "                                      TT",
        "          C   T          C       T      ",
        "  T      TTT            TTT             ",
        "      T          T E T                  ",
        "   TTT       C    TTT        T          ",
        "            TT                      C   ",
        "       C                C  E       TT   ",
        "      TTT              TTTTTT           ",
        "             C                C         ",
        "          TTTTT   T E T    TTTTT        ",
        "@  SSS             TTT  SSS             ",
        "TTTTTTTT   SSSSSS      TTTTT   SSSSSS TT"
    ]
]

# ==============================================================================
# CLASES DEL JUEGO
# ==============================================================================
class Jugador:
    def __init__(self, x, y, animaciones=None):
        self.rect = pygame.Rect(x, y, 30, 30)
        self.vel_y = 0
        self.velocidad = 5
        self.fuerza_salto = -15
        self.gravedad = 0.5
        self.en_suelo = False
        self.direccion = 1 # 1: derecha, -1: izquierda

        # --- Animación / sprites (configuracion.py) ---
        self.animaciones = animaciones or {}
        self.estado = "idle"
        self.tiempo_inicio_estado = pygame.time.get_ticks()

    def mover(self, dx, dy, plataformas):
        self.rect.x += dx
        for p in plataformas:
            if self.rect.colliderect(p):
                if dx > 0: self.rect.right = p.left
                if dx < 0: self.rect.left = p.right

        self.rect.y += dy
        self.en_suelo = False
        for p in plataformas:
            if self.rect.colliderect(p):
                if dy > 0:
                    self.rect.bottom = p.top
                    self.vel_y = 0
                    self.en_suelo = True
                if dy < 0:
                    self.rect.top = p.bottom
                    self.vel_y = 0

    def actualizar(self, plataformas):
        self.vel_y += self.gravedad
        if self.vel_y > 12: self.vel_y = 12
        
        teclas = pygame.key.get_pressed()
        dx = 0
        if teclas[pygame.K_a]: 
            dx = -self.velocidad
            self.direccion = -1
        if teclas[pygame.K_d]: 
            dx = self.velocidad
            self.direccion = 1
            
        if (teclas[pygame.K_w] or teclas[pygame.K_SPACE]) and self.en_suelo:
            self.vel_y = self.fuerza_salto

        self.mover(dx, self.vel_y, plataformas)

        # --- Determinar estado de animación ---
        if not self.en_suelo and self.vel_y < 0:
            nuevo_estado = "saltar"
        elif not self.en_suelo and self.vel_y > 0:
            nuevo_estado = "caer"
        elif dx != 0:
            nuevo_estado = "correr"
        else:
            nuevo_estado = "idle"

        if nuevo_estado != self.estado:
            self.estado = nuevo_estado
            self.tiempo_inicio_estado = pygame.time.get_ticks()

    def dibujar(self, superficie, cam_x, cam_y):
        rect_pantalla = self.rect.move(-cam_x, -cam_y)

        frames = self.animaciones.get(self.estado, [])
        sprite = config.obtener_frame_actual(
            frames, self.tiempo_inicio_estado, config.VELOCIDAD_ANIMACION_JUGADOR
        )

        if sprite is not None:
            if self.direccion == -1:
                sprite = pygame.transform.flip(sprite, True, False)
            superficie.blit(sprite, rect_pantalla)
        else:
            # --- Dibujo de respaldo (sin sprite configurado todavía) ---
            pygame.draw.rect(superficie, AZUL_CIELO, rect_pantalla)
            ojo_x = rect_pantalla.x + (20 if self.direccion == 1 else 5)
            pygame.draw.rect(superficie, NEGRO, (ojo_x, rect_pantalla.y + 5, 5, 5))
            pygame.draw.rect(superficie, NEGRO, rect_pantalla, 2)

class Proyectil:
    def __init__(self, x, y, direccion, tipo):
        self.tipo = tipo
        self.direccion = direccion
        
        if tipo == "Fuego":
            self.rect = pygame.Rect(x, y, 12, 12)
            self.velocidad = 7
            self.color = C_FUEGO
            self.dano = 35
        elif tipo == "Hielo":
            self.rect = pygame.Rect(x, y, 10, 10)
            self.velocidad = 6
            self.color = C_HIELO
            self.dano = 20
        elif tipo == "Piedra":
            self.rect = pygame.Rect(x, y, 16, 16)
            self.velocidad = 5
            self.color = C_PIEDRA
            self.dano = 55
        elif tipo == "Viento":
            self.rect = pygame.Rect(x, y, 15, 20)
            self.velocidad = 10
            self.color = C_VIENTO
            self.dano = 15

    def actualizar(self):
        self.rect.x += self.velocidad * self.direccion

    def dibujar(self, superficie, cam_x, cam_y):
        rect_pantalla = self.rect.move(-cam_x, -cam_y)
        if self.tipo in ["Fuego", "Hielo"]:
            pygame.draw.circle(superficie, self.color, rect_pantalla.center, self.rect.width//2)
        else:
            pygame.draw.rect(superficie, self.color, rect_pantalla)

class Enemigo:
    def __init__(self, x, y, animaciones=None):
        self.rect = pygame.Rect(x + 5, y + 10, 30, 30)
        self.velocidad_base = 2
        self.direccion = 1
        self.vel_y = 0
        
        # Sistema de Vida
        self.max_hp = 100
        self.hp = 100
        
        # Estados
        self.tiempo_congelado = 0

        # --- Animación / sprites (configuracion.py) ---
        self.animaciones = animaciones or {"normal": [], "congelado": []}

    def actualizar(self, plataformas):
        # Gravedad para que no floten
        self.vel_y += 0.5
        if self.vel_y > 10: self.vel_y = 10
        self.rect.y += self.vel_y
        
        for p in plataformas:
            if self.rect.colliderect(p):
                if self.vel_y > 0:
                    self.rect.bottom = p.top
                    self.vel_y = 0
                elif self.vel_y < 0:
                    self.rect.top = p.bottom
                    self.vel_y = 0

        # Ralentización por Hielo
        velocidad_actual = self.velocidad_base
        if pygame.time.get_ticks() < self.tiempo_congelado:
            velocidad_actual = self.velocidad_base * 0.4 # Muy lento

        # Mover en X
        self.rect.x += velocidad_actual * self.direccion
        for p in plataformas:
            if self.rect.colliderect(p):
                if self.direccion == 1: self.rect.right = p.left
                else: self.rect.left = p.right
                self.direccion *= -1 # Dar la vuelta

    def aplicar_empuje(self, direccion_proyectil, plataformas):
        self.rect.x += 40 * direccion_proyectil
        # Evitar atravesar paredes por el empuje
        for p in plataformas:
            if self.rect.colliderect(p):
                if direccion_proyectil == 1: self.rect.right = p.left
                else: self.rect.left = p.right

    def dibujar(self, superficie, cam_x, cam_y):
        rect_pantalla = self.rect.move(-cam_x, -cam_y)

        esta_congelado = pygame.time.get_ticks() < self.tiempo_congelado
        if esta_congelado:
            frames = self.animaciones.get("congelado", [])
            velocidad_anim = config.VELOCIDAD_ANIMACION_ENEMIGO_CONGELADO
        else:
            frames = self.animaciones.get("normal", [])
            velocidad_anim = config.VELOCIDAD_ANIMACION_ENEMIGO

        # Se usa tiempo_inicio=0 para que la animación corra de forma
        # continua con el reloj global del juego (no hace falta guardar
        # un "inicio" por enemigo).
        sprite = config.obtener_frame_actual(frames, 0, velocidad_anim)

        if sprite is not None:
            if self.direccion == -1:
                sprite = pygame.transform.flip(sprite, True, False)
            superficie.blit(sprite, rect_pantalla)
        else:
            # --- Dibujo de respaldo (sin sprite configurado todavía) ---
            color_enemigo = C_HIELO if esta_congelado else MORADO
            pygame.draw.rect(superficie, color_enemigo, rect_pantalla)
            pygame.draw.rect(superficie, NEGRO, rect_pantalla, 2)
        
        # Barra de Vida
        largo_barra = 30 * (self.hp / self.max_hp)
        barra_rect = pygame.Rect(rect_pantalla.x, rect_pantalla.y - 10, largo_barra, 5)
        pygame.draw.rect(superficie, ROJO, (rect_pantalla.x, rect_pantalla.y - 10, 30, 5)) # Fondo rojo
        pygame.draw.rect(superficie, VERDE, barra_rect) # Vida actual verde

def cargar_nivel(indice_nivel):
    global TEXTURAS_NIVEL_ACTUAL, ANIMACIONES_ENEMIGO_ACTUAL

    # --- Cargar texturas específicas de este nivel (configuracion.py) ---
    TEXTURAS_NIVEL_ACTUAL = config.cargar_texturas_nivel(indice_nivel, (TAMANO_TILE, TAMANO_TILE))
    if TEXTURAS_NIVEL_ACTUAL.get("fondo") is not None:
        TEXTURAS_NIVEL_ACTUAL["fondo"] = pygame.transform.scale(TEXTURAS_NIVEL_ACTUAL["fondo"], (ANCHO, ALTO))

    tipo_enemigo = config.obtener_tipo_enemigo_para_nivel(indice_nivel)
    ANIMACIONES_ENEMIGO_ACTUAL = config.cargar_animaciones_enemigo(tipo_enemigo, TAMANO_ENEMIGO)

    mapa = NIVELES[indice_nivel]
    plataformas, pinchos, monedas, enemigos = [], [], [], []
    puerta = None
    inicio_x, inicio_y = 0, 0
    ancho_nivel = len(mapa[0]) * TAMANO_TILE
    alto_nivel = len(mapa) * TAMANO_TILE

    for fila_idx, fila in enumerate(mapa):
        for col_idx, celda in enumerate(fila):
            x, y = col_idx * TAMANO_TILE, fila_idx * TAMANO_TILE
            if celda == "T": plataformas.append(pygame.Rect(x, y, TAMANO_TILE, TAMANO_TILE))
            elif celda == "S": pinchos.append(pygame.Rect(x, y + TAMANO_TILE//2, TAMANO_TILE, TAMANO_TILE//2))
            elif celda == "C": monedas.append(pygame.Rect(x + 10, y + 10, 20, 20))
            elif celda == "E": enemigos.append(Enemigo(x, y, ANIMACIONES_ENEMIGO_ACTUAL))
            elif celda == "D": puerta = pygame.Rect(x, y, TAMANO_TILE, TAMANO_TILE)
            elif celda == "@": inicio_x, inicio_y = x, y + (TAMANO_TILE - 30)

    return inicio_x, inicio_y, plataformas, pinchos, monedas, enemigos, puerta, ancho_nivel, alto_nivel

def dibujar_corazon(superficie, x, y):
    pygame.draw.circle(superficie, ROJO, (x - 6, y), 6)
    pygame.draw.circle(superficie, ROJO, (x + 6, y), 6)
    pygame.draw.polygon(superficie, ROJO, [(x - 12, y + 2), (x + 12, y + 2), (x, y + 14)])

def obtener_poder_por_nivel(nivel):
    if nivel == 0: return "Ninguno"
    elif nivel == 1: return "Fuego"
    elif nivel == 2: return "Hielo"
    elif nivel == 3: return "Piedra"
    else: return "Viento"

# ==============================================================================
# BUCLE PRINCIPAL DEL JUEGO
# ==============================================================================
def main():
    vidas = 3
    monedas_totales = 0
    nivel_actual = 0
    estado_juego = "JUGANDO"

    inicio_x, inicio_y, plataformas, pinchos, monedas, enemigos, puerta, ancho_nivel, alto_nivel = cargar_nivel(nivel_actual)
    jugador = Jugador(inicio_x, inicio_y, ANIMACIONES_JUGADOR)
    poder_actual = obtener_poder_por_nivel(nivel_actual)
    proyectiles = []
    ultimo_disparo = 0

    corriendo = True
    while corriendo:
        RELOJ.tick(FPS)
        tiempo_actual = pygame.time.get_ticks()

        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                corriendo = False
            
            if evento.type == pygame.KEYDOWN and evento.key == pygame.K_r:
                if estado_juego != "JUGANDO":
                    vidas = 3
                    monedas_totales = 0
                    nivel_actual = 0
                    poder_actual = obtener_poder_por_nivel(nivel_actual)
                    estado_juego = "JUGANDO"
                    inicio_x, inicio_y, plataformas, pinchos, monedas, enemigos, puerta, ancho_nivel, alto_nivel = cargar_nivel(nivel_actual)
                    jugador.rect.topleft = (inicio_x, inicio_y)
                    jugador.vel_y = 0
                    proyectiles.clear()

        if estado_juego == "JUGANDO":
            # --- DISPARAR ---
            teclas = pygame.key.get_pressed()
            if teclas[pygame.K_j] and poder_actual != "Ninguno" and tiempo_actual - ultimo_disparo > 400:
                proyectiles.append(Proyectil(jugador.rect.centerx, jugador.rect.centery, jugador.direccion, poder_actual))
                ultimo_disparo = tiempo_actual

            jugador.actualizar(plataformas)

            cam_x = max(0, min(jugador.rect.centerx - ANCHO // 2, ancho_nivel - ANCHO))
            cam_y = max(0, min(jugador.rect.centery - ALTO // 2, alto_nivel - ALTO))

            # --- PROYECTILES ---
            for proy in proyectiles[:]:
                proy.actualizar()
                eliminado = False
                
                # Choque con plataformas
                for p in plataformas:
                    if proy.rect.colliderect(p):
                        proyectiles.remove(proy)
                        eliminado = True
                        break
                
                if eliminado: continue

                # Choque con enemigos
                for enemigo in enemigos:
                    if proy.rect.colliderect(enemigo.rect):
                        enemigo.hp -= proy.dano
                        if proy.tipo == "Hielo":
                            enemigo.tiempo_congelado = tiempo_actual + 2000 # 2 segundos
                        elif proy.tipo == "Viento":
                            enemigo.aplicar_empuje(proy.direccion, plataformas)
                        
                        proyectiles.remove(proy)
                        break

            # Limpiar proyectiles fuera de pantalla y enemigos muertos
            proyectiles = [p for p in proyectiles if 0 < p.rect.x < ancho_nivel]
            enemigos = [e for e in enemigos if e.hp > 0]

            # --- COLISIONES CON ENEMIGOS ---
            for enemigo in enemigos:
                enemigo.actualizar(plataformas)
                if jugador.rect.colliderect(enemigo.rect):
                    # Como ya no se aplastan, chocar resta vida directamente
                    vidas -= 1
                    jugador.rect.topleft = (inicio_x, inicio_y)
                    jugador.vel_y = 0
                    if vidas <= 0: estado_juego = "GAMEOVER"

            for pincho in pinchos:
                if jugador.rect.colliderect(pincho):
                    vidas -= 1
                    jugador.rect.topleft = (inicio_x, inicio_y)
                    jugador.vel_y = 0
                    if vidas <= 0: estado_juego = "GAMEOVER"

            for moneda in monedas[:]:
                if jugador.rect.colliderect(moneda):
                    monedas.remove(moneda)
                    monedas_totales += 1
                    if monedas_totales % 10 == 0: vidas += 1

            if jugador.rect.colliderect(puerta):
                nivel_actual += 1
                if nivel_actual < len(NIVELES):
                    poder_actual = obtener_poder_por_nivel(nivel_actual) # Asignar nuevo poder
                    proyectiles.clear()
                    inicio_x, inicio_y, plataformas, pinchos, monedas, enemigos, puerta, ancho_nivel, alto_nivel = cargar_nivel(nivel_actual)
                    jugador.rect.topleft = (inicio_x, inicio_y)
                    jugador.vel_y = 0
                else:
                    estado_juego = "VICTORIA"

            if jugador.rect.y > alto_nivel:
                vidas -= 1
                jugador.rect.topleft = (inicio_x, inicio_y)
                if vidas <= 0: estado_juego = "GAMEOVER"

        # 3. DIBUJADO EN PANTALLA
        fondo_nivel = TEXTURAS_NIVEL_ACTUAL.get("fondo") if estado_juego == "JUGANDO" else None
        if fondo_nivel is not None:
            PANTALLA.blit(fondo_nivel, (0, 0))
        else:
            PANTALLA.fill((30, 30, 40))

        if estado_juego == "JUGANDO":
            bloques_nivel = TEXTURAS_NIVEL_ACTUAL.get("bloques", {})
            sprite_plataforma = bloques_nivel.get("T")
            sprite_pincho = bloques_nivel.get("S")
            sprite_moneda = config.obtener_frame_actual(ANIMACION_MONEDA, 0, config.VELOCIDAD_ANIMACION_MONEDA)

            for p in plataformas:
                p_pantalla = p.move(-cam_x, -cam_y)
                if sprite_plataforma is not None:
                    PANTALLA.blit(sprite_plataforma, p_pantalla)
                else:
                    pygame.draw.rect(PANTALLA, VERDE, p_pantalla)
                    pygame.draw.rect(PANTALLA, NEGRO, p_pantalla, 1)

            for p in pinchos:
                p_pantalla = p.move(-cam_x, -cam_y)
                if sprite_pincho is not None:
                    PANTALLA.blit(sprite_pincho, p_pantalla)
                else:
                    pygame.draw.polygon(PANTALLA, GRIS, [(p_pantalla.left, p_pantalla.bottom), (p_pantalla.centerx, p_pantalla.top), (p_pantalla.right, p_pantalla.bottom)])

            for c in monedas:
                c_pantalla = c.move(-cam_x, -cam_y)
                if sprite_moneda is not None:
                    PANTALLA.blit(sprite_moneda, c_pantalla)
                else:
                    pygame.draw.circle(PANTALLA, AMARILLO, c_pantalla.center, 10)
                    pygame.draw.circle(PANTALLA, (218, 165, 32), c_pantalla.center, 10, 2)
            
            for proy in proyectiles: proy.dibujar(PANTALLA, cam_x, cam_y)
            for e in enemigos: e.dibujar(PANTALLA, cam_x, cam_y)

            pygame.draw.rect(PANTALLA, CAFE, puerta.move(-cam_x, -cam_y))
            pygame.draw.circle(PANTALLA, NEGRO, (puerta.move(-cam_x, -cam_y).right - 10, puerta.move(-cam_x, -cam_y).centery), 4)

            jugador.dibujar(PANTALLA, cam_x, cam_y)

            # --- DIBUJAR INTERFAZ (UI) ---
            for i in range(vidas): dibujar_corazon(PANTALLA, 30 + (i * 30), 30)
            
            # Textos
            PANTALLA.blit(FUENTE_UI.render(f"Monedas: {monedas_totales}", True, BLANCO), (20, 50))
            PANTALLA.blit(FUENTE_UI.render(f"Poder: {poder_actual}", True, AMARILLO), (20, 75))
            PANTALLA.blit(FUENTE_UI.render(NOMBRES_NIVELES[nivel_actual], True, BLANCO), (ANCHO - 220, 20))
            PANTALLA.blit(FUENTE_UI.render("Mover: Flechas | Saltar: Espacio | Disparar: Z", True, BLANCO), (ANCHO//2 - 200, 20))

        elif estado_juego == "GAMEOVER":
            PANTALLA.blit(FUENTE_TITULO.render("¡FIN DEL JUEGO!", True, ROJO), (ANCHO//2 - 200, ALTO//2 - 50))
            PANTALLA.blit(FUENTE_UI.render("Presiona 'R' para reiniciar", True, BLANCO), (ANCHO//2 - 120, ALTO//2 + 20))

        elif estado_juego == "VICTORIA":
            PANTALLA.blit(FUENTE_TITULO.render("¡HAS GANADO!", True, AMARILLO), (ANCHO//2 - 180, ALTO//2 - 50))
            PANTALLA.blit(FUENTE_UI.render(f"Monedas: {monedas_totales} | Presiona 'R' para jugar de nuevo", True, BLANCO), (ANCHO//2 - 200, ALTO//2 + 20))

        pygame.display.flip()

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()