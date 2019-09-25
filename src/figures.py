import pygame
import pygame.draw


class Point:
    def __init__(self):
        pass

    def draw(self, screen, coord, clicktype, point_color, point_radius):
        if clicktype != 1:
            return
        pygame.draw.circle(screen, point_color, coord, point_radius)
        pygame.display.flip()
        return
