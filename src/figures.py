import pygame
import pygame.draw


class point():
    def __init__(self):
        pass
    def draw(self, screen, coord, clictype, point_color, point_radius):
        if clictype !=1 :
            return
        pygame.draw.circle(screen, point_color, coord, point_radius)
        pygame.display.flip()
        return


 