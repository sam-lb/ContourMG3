import pygame
from colors import themes
from core import Plot, Contour
from math import sin, cos, tan, exp, sqrt


pygame.init()
WIDTH = HEIGHT = 500
HWIDTH = WIDTH / 2
HHEIGHT = HEIGHT / 2
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Contour plotter")
pygame.key.set_repeat(100, 50)


plot = Plot(screen)
contour = Contour(plot, lambda x, y: x+y*y/10 + 15*(sin(x)*sin(y))**4, 5, themes["rainbow"])
plot.set_function(contour)
running = True

while running:
    plot.update()
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            break
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False
                break
            elif event.key == pygame.K_UP:
                plot.resolve(1)
            elif event.key == pygame.K_DOWN:
                plot.resolve(-1)
            elif event.key == pygame.K_RIGHT:
                plot.resolve(4)
            elif event.key == pygame.K_LEFT:
                plot.resolve(-4)
            elif event.key == pygame.K_i:
                plot.zoom_in()
            elif event.key == pygame.K_o:
                plot.zoom_out()
        elif event.type == pygame.MOUSEMOTION:
            if pygame.mouse.get_pressed()[0]:
                plot.scroll(-event.rel[0] / plot.scales[0], event.rel[1] / plot.scales[1])
                
pygame.quit()
