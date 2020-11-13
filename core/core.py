import pygame
from .colors import themes


white = (255, 255, 255)
black = (0, 0, 0)
pygame.font.init()
font = pygame.font.SysFont("arial", 16)

def constrain(x, min_, max_):
    return min(max(min_, x), max_)

def text(text, x, y, surface, color=(255, 255, 255)):
    """ draws text to a surface """
    surf = font.render(text, 1, color);
    surface.blit(surf, (x, y));


class Polygon:

    def __init__(self, points, color):
        self.points = points
        self.color = color

    def __repr__(self):
        return "polygon({})\n".format(list(map(lambda p: (int(p[0]),int(p[1])), self.points)))
    

class Contour:

    def __init__(self, plot, function, resolution=100, colors=None):
        # resolution: samples per dimension (res=10 -> 10x10=100 samples)
        self.plot = plot
        self.function = function
        self.resolution = resolution

        if colors is None: colors = themes["original"]
        self.set_colors(colors)

    def set_colors(self, colors):
        self.colors = colors
        self.colors_length = len(self.colors)
        self.plot.needs_update = True
        self.generate()

    def get_color(self, val):
        if self.span == 0: return self.colors[0]
        normalized = (val - self.min) / self.span
        index = int(normalized * self.colors_length)
        if index == self.colors_length: index -= 1

        color_interval = 1 / self.colors_length
        past_the_post = normalized - index * color_interval
        color = self.lerp(self.colors[index-1], self.colors[index], past_the_post / color_interval)
        return color

    def lerp(self, c1, c2, pct):
        comp = 1-pct
        return comp*c1[0]+pct*c2[0],comp*c1[1]+pct*c2[1],comp*c1[2]+pct*c2[2]

    def generate(self):
        self.precompute()
        self.generate_mesh()
        self.plot.needs_update = True

    def precompute(self):
        self.steps = self.plot.units[0] / self.resolution, self.plot.units[1] / self.resolution
        self.min = self.max = None
        x = self.plot.bounds[0]
        y = self.plot.bounds[2]
        self.samples = []
        
        for i in range(self.resolution+1):
            column = []
            for j in range(self.resolution+1):
                try:
                    value = self.function(x, y)
                except Exception:
                    column.append(None)
                    raise
                else:
                    self.min = value if self.min is None else min(self.min, value)
                    self.max = value if self.max is None else max(self.max, value)
                    column.append(value)
                y += self.steps[1]
            x += self.steps[0]
            y = self.plot.bounds[2]
            self.samples.append(column[:])
            #pygame.event.get() # prevent application from hanging

        if self.min is None:
            self.min = 0
            self.max = 0
        self.span = self.max - self.min

    def generate_mesh(self):
        self.mesh = []
        x = self.plot.bounds[0]
        y = self.plot.bounds[2]

        for i in range(self.resolution):
            for j in range(self.resolution):
                samples = self.samples[i][j], self.samples[i+1][j], self.samples[i+1][j+1], self.samples[i][j+1]
                if not any((v is None for v in samples)):
                    val = sum(samples) / 4
                    self.mesh.append(Polygon(tuple(self.plot.transform(point) for point in [(x, y),
                                                                                            (x+self.steps[0], y),
                                                                                            (x+self.steps[0], y+self.steps[1]),
                                                                                            (x, y+self.steps[1])]),
                                             self.get_color(val)))
                y += self.steps[1]
            y = self.plot.bounds[2]
            x += self.steps[0]
            #pygame.event.get() # prevent application from hanging

    def draw(self, surface):
        for polygon in self.mesh:
            pygame.draw.polygon(surface, polygon.color, polygon.points)
            

class Plot:

    def __init__(self, surface, gui, bounds=None):
        self.functions = []
        self.surface = surface
        self.function = None
        self.clock = pygame.time.Clock()
        self.alive = True
        self.gui = gui

        if bounds is None: bounds = [-4, 4, -4, 4]
        self.set_bounds(bounds)

    def __repr__(self):
        return "Window\n--------------------\nBounds: {}\nUnits: {}\nScales: {}".format(
            self.bounds, self.units, self.scales
        )

    def kill(self):
        self.alive = False

    def set_bounds(self, bounds):
        if not (1/100 <= bounds[1] - bounds[0] <= 1000000) or not (1/100 <= bounds[3] - bounds[2] <= 1000000): return
        self.bounds = bounds
        self.units = bounds[1] - bounds[0], bounds[3] - bounds[2]
        self.on_window_scale()

    def on_window_scale(self):
        self.width, self.height = self.surface.get_width(), self.surface.get_height()
        self.scales = self.width / self.units[0], self.height / self.units[1]
        self.origin = -self.bounds[0] * self.scales[0], self.bounds[3] * self.scales[1]
        self.max_res = max(self.width, self.height)
        
        self.needs_update = True
        if self.function is not None: self.function.generate()

    def set_function(self, function):
        self.function = function
        self.needs_update = True

    def set_theme(self, theme):
        if self.function is not None: self.function.set_colors(themes[theme])

    def resolve(self, diff):
        if self.function is not None:
            self.function.resolution = constrain(self.function.resolution + diff, 1, self.max_res)
            self.function.generate()

    def zoom_in(self):
        self.set_bounds([
            self.bounds[0] + self.units[0] / 4,
            self.bounds[1] - self.units[0] / 4,
            self.bounds[2] + self.units[1] / 4,
            self.bounds[3] - self.units[1] / 4,
        ])

    def zoom_out(self):
        self.set_bounds([
            self.bounds[0] - self.units[0] / 4,
            self.bounds[1] + self.units[0] / 4,
            self.bounds[2] - self.units[1] / 4,
            self.bounds[3] + self.units[1] / 4,
        ])

    def scroll(self, dx, dy):
        self.set_bounds([
            self.bounds[0] + dx,
            self.bounds[1] + dx,
            self.bounds[2] + dy,
            self.bounds[3] + dy,
        ])

    def transform(self, point):
        # cartesian -> pixel
        return point[0] * self.scales[0] + self.origin[0], self.origin[1] - point[1] * self.scales[1]

    def reverse(self, point):
        # pixel -> cartesian
        return (point[0] - self.origin[0]) / self.scales[0], (self.origin[1] - point[1]) / self.scales[1]

    def export(self, filename, max_res=True):
        if self.function is not None:
            if max_res:
                self.surface.fill(white)
                text("Saving image...", 10, 10, self.surface, color=black)
                pygame.display.flip()
                
                temp = self.function.resolution
                self.function.resolution = self.max_res
                self.function.generate()
                self.update()
                self.function.resolution = temp
                self.function.generate()
            pygame.image.save(self.surface, filename)
            self.update()
            
    def get_window_data(self):
        mouse_position = self.reverse(pygame.mouse.get_pos())
        mouse_position = round(mouse_position[0], 2), round(mouse_position[1], 2)
        window_x = round(self.bounds[0], 2), round(self.bounds[1], 2)
        window_y = round(self.bounds[2], 2), round(self.bounds[3], 2)

        return [
            "[{}, {}]".format(*window_x),
            "[{}, {}]".format(*window_y),
            "({}, {})".format(*mouse_position)
        ]

    def update(self):
        if self.needs_update:
            self.surface.fill(white)
            if self.function is not None: self.function.draw(self.surface)
            self.needs_update = False

        pygame.draw.rect(self.surface, black, (0, 0, self.width, self.height), 3)
        self.gui.update_data()
        pygame.display.flip()
        self.clock.tick(50)
