import pygame
import pygame.draw


class Point:
    def __init__(self, coord, clicktype, point_color, font_size):
        self.coord = coord
        self.clicktype = clicktype
        self.point_color = point_color
        self.font_size = font_size

    def draw(self, screen):
        if self.clicktype != 1:
            return
        pygame.draw.circle(screen, self.point_color, self.coord, self.font_size)
        pygame.display.flip()
        return


class Line:
    def __init__(self, line_color, start_pos, end_pos, font_size):
        self.line_color = line_color
        self.start_pos = start_pos
        self.end_pos = end_pos
        self.font_size = font_size

    def draw(self, screen):
        pygame.draw.line(screen, self.line_color, self.start_pos, self.end_pos, self.font_size)
        return


class TextBox:
    def __init__(self, x, y, w, h, color, font, font_size, text=''):
        self.rect = pygame.Rect(x, y, w, h)
        self.color = color
        self.text = text
        self.sysfont = pygame.font.SysFont(font, font_size)
        self.txt_surface = self.sysfont.render(text, True, self.color)
        self.active = False

    def update(self):
        # Resize the box if the text is too long.
        width = max(200, self.txt_surface.get_width() + 10)
        self.rect.w = width

    def draw(self, screen):
        # Blit the text.
        screen.blit(self.txt_surface, (self.rect.x + 5, self.rect.y + 5))
        # Blit the rect.
        pygame.draw.rect(screen, self.color, self.rect, 2)
