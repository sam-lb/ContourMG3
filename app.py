import pygame, os
import tkinter as tk
import core
from math import sin, cos, tan, exp, sqrt


WIDTH = HEIGHT = 500
HWIDTH = WIDTH / 2
HHEIGHT = HEIGHT / 2


def on_close(*args):
    plot.kill()
    root.destroy()

root = tk.Tk()
interface = core.Interface(root, width=WIDTH, height=HEIGHT)
interface.grid(row=0, column=0, rowspan=16)
os.environ["SDL_WINDOWID"] = str(interface.winfo_id())
os.environ["SDL_VIDEODRIVER"] = "windib"
root.protocol("WM_DELETE_WINDOW", on_close)
root.bind("<Escape>", on_close)
root.resizable(False, False)
root.update()

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Contour plotter")
pygame.key.set_repeat(100, 50)

plot = core.Plot(screen, gui=interface)
interface.set_plot(plot)


while plot.alive:
    plot.update()
    root.update()
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            plot.kill()
            break
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
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
