import pygame
import sys


pygame.init()

WIDTH, HEIGHT = 800, 600


screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Laboraorul 1 - Grafica 2D cu Pygame")


ALB = (255, 255, 255)
ROSU = (255, 0, 0)
VERDE = (0, 255, 0)
ALBASTRU = (0, 0, 255)
PORTOCALIU=(255,165,0)
MARO=(165, 42, 42)

circle_x=100
circle_y=390
circle_radius=80
circle_speed=5

rect_x=100
rect_y=100
rect_width=200
rect_height=150


running = True

while running:
    
 
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    circle_x+=circle_speed

    if circle_x +circle_radius >WIDTH:
        circle_speed=-0.3

    if circle_x -circle_radius <0:
        circle_speed=0.3

    pos_x,pos_y=pygame.mouse.get_pos()

    rect_x=pos_x-(rect_width/2)
    rect_y =pos_y-(rect_height/2)
    
    
    screen.fill(PORTOCALIU)

    pygame.draw.circle(screen, ALBASTRU, (circle_x, circle_y), circle_radius)
    

    pygame.draw.rect(screen, VERDE, (rect_x,rect_y,rect_width,rect_height))
    
   
    pygame.draw.line(screen, ROSU, (0, 0), (800, 600), 5)

    pygame.draw.rect(screen, MARO, (300,200,200,200))
    
    pygame.draw.polygon(screen,ROSU,((300,200),(500,200),(400,50)))

    pygame.draw.rect(screen,ALBASTRU,(330,230,40,40))

    pygame.draw.rect(screen,ALBASTRU,(430,230,40,40))

    pygame.draw.rect(screen,VERDE,(380,320,40,80))

    pygame.display.flip()

    


pygame.quit()
sys.exit()