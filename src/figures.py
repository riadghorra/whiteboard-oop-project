import pygame
import pygame.draw

class point():
    def __init__(self):
        pass
    def draw(self, screen, coord, clictype):
        if clictype !=1 :
            return
        pygame.draw.circle(screen, [0,0,0], coord, 0, 0)
        pygame.display.flip()
        return


 