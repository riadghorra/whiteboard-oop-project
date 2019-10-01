import pygame
import pygame.draw


class Point:
    def __init__(self):
        pass

    def draw(self, screen, coord, clicktype, point_color, font_size):
        if clicktype != 1:
            return
        pygame.draw.circle(screen, point_color, coord, font_size)
        pygame.display.flip()
        return

class Line:
    def __init__(self):
        pass

    def draw(self, screen, line_color, start_pos, end_pos, font_size):
        pygame.draw.line(screen, 
                         line_color, 
                         start_pos, 
                         end_pos, 
                         font_size)
        return
