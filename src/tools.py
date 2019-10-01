import pygame
import pygame.draw

black = [0,0,0]
red = [255,0,0]
green = [0,255,0]
blue  = [0,0,255]
white = [255,255,255]

class trigger_box():
    def __init__(self, top_left, size):
        self.rect = pygame.Rect(top_left, size)
        self.coords = top_left
    
    def is_triggered(self, event):
        return self.rect.collidepoint(event.pos)

class mode(trigger_box):
    def __init__(self, name, top_left, size):
        super(mode,self).__init__(top_left, size)
        self.name = name
        
    def add(self, screen):
        pygame.draw.rect(screen, black, self.rect,1)
        font = pygame.font.Font(None,18)
        legend = {"text" : font.render(self.name,True,[0,0,0]), "coords" : self.coords}
        screen.blit(legend["text"], legend["coords"])
        
class color_box(trigger_box):
    def __init__(self, color, top_left, size):
        super(color_box,self).__init__(top_left, size)
        self.color = color
        
    def add(self, screen):
        pygame.draw.rect(screen, self.color, self.rect)

class font_size_box(trigger_box):
    def __init__(self, font_size, top_left, size):
        super(font_size_box,self).__init__(top_left, size)
        self.font_size = font_size
        self.center = [top_left[0]+size[0]//2,top_left[1]+size[1]//2]

    def add(self, screen):
        pygame.draw.rect(screen, black, self.rect, 1)
        pygame.draw.circle(screen,black,self.center,self.font_size)
