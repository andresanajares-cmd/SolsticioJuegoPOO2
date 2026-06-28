import pygame
pygame.init()

ventana = pygame.display.set_mode((600, 400))
reloj = pygame.time.Clock()        
 
x = 100  
y = 100
velocidad = 2   



jugando = True
while jugando:
      
    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            jugando = False
    teclas = pygame.key.get_pressed()
    if teclas[pygame.K_a]:
        x = x - velocidad
    if teclas[pygame.K_d]:
        x = x + velocidad
    if teclas[pygame.K_w]:
        y = y - velocidad
    if teclas[pygame.K_s]:
        y = y + velocidad
      
    
 
    ventana.fill((30, 30, 60))     
    
                      
# DIBUJAR fondo
    pygame.draw.rect(ventana, 
(255,140,40),(x,y,60,60)) 
    pygame.display.flip()                            
# MOSTRAR
    reloj.tick(60)                 
 
pygame.quit()