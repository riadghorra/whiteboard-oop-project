import pygame
import pygame.draw


def distance(v1,v2):
    return ((v1[0]-v2[0])**2+(v1[1]-v2[1])**2)**0.5

class Point:
    def __init__(self, coord, clicktype, point_color, font_size):
        self.coord = coord
        self.clicktype = clicktype
        self.point_color = point_color
        self.font_size = font_size
        self.type = "Point"

    def draw(self, screen):
        if self.clicktype != 1:
            return
        pygame.draw.circle(screen, self.point_color, self.coord, self.font_size)
        pygame.display.flip()
        return

    def fetch_params(self):
        return {"coord": self.coord, "clicktype": self.clicktype, "point_color": self.point_color,
                "font_size": self.font_size}


class Line:
    def __init__(self, line_color, start_pos, end_pos, font_size):
        self.line_color = line_color
        self.start_pos = start_pos
        self.end_pos = end_pos
        self.font_size = font_size
        self.type = "Line"

    def draw(self, screen):
        pygame.draw.line(screen, self.line_color, self.start_pos, self.end_pos, self.font_size)
        return

    def fetch_params(self):
        return {"line_color": self.line_color, "start_pos": self.start_pos, "end_pos": self.end_pos,
                "font_size": self.font_size}


class Rectangle:
    def __init__(self, c1, c2, color=[0, 0, 0]):
        self.c1 = c1
        self.c2 = c2
        self.color = color
        self.left = min(c1[0], c2[0])
        self.top = min(c1[1], c2[1])
        self.right = max(c1[0], c2[0])
        self.bottom = max(c1[1], c2[1])
        self.width = self.right - self.left
        self.length = self.bottom - self.top
        self.color = color
        self.rect = pygame.Rect(self.left, self.top, self.width, self.length)
        self.type = "rect"

    def draw(self, screen):
        pygame.draw.rect(screen, self.color, self.rect, 0)

    def fetch_params(self):
        return {"c1": self.c1, "c2": self.c2, "color": self.color}

class Circle:
    def __init__(self, center, point, color=[0, 0, 0], toolbar_size=0):
        self.toolbar_size = toolbar_size
        self.center = center
        self.point = point
        self.color = color
        self.radius = ((self.center[0]-self.point[0])**2+(self.center[1]-self.point[1])**2)**0.5
        self.color = color
        self.type = "circle"

    def draw(self, screen):
        pygame.draw.circle(screen, self.color, self.center, min(int(self.radius), self.center[1]-self.toolbar_size))

    def fetch_params(self):
        return {"center": self.center, "point": self.point, "color": self.color, "toolbar_size" : self.toolbar_size }

class TextBox:

    def __init__(self, x, y, w, h, box_color, font, font_size, text, text_color):
        self.__rect = pygame.Rect(x, y, w, h)
        self._color = box_color
        self._text = text
        self._font = font
        self._font_size = font_size
        self._sysfont = pygame.font.SysFont(font, font_size)
        self._text_color = text_color
        self._txt_surface = self._sysfont.render(text, True, self._text_color)
        self.id_counter = str(x) + "_" + str(y)
        self.type = "Text_box"

    """
    Encapsulation
    """

    def fetch_params(self):
        return {"x": self.__rect.x, "y": self.__rect.y, "w": self.__rect.w, "h": self.__rect.h,
                "box_color": self._color, "font": self._font, "font_size": self._font_size, "text": self._text,
                "text_color": self._text_color}

    def get_textbox_color(self):
        return self._color

    def set_textbox_color(self, new_color):
        self._color = new_color

    def get_textbox_text(self):
        return self._text

    def add_character_to_text(self, char):
        self._text += char

    def delete_char_from_text(self):
        self._text = self._text[:-1]

    def render_font(self, text, color, antialias=True):
        return self._sysfont.render(text, antialias, color)

    def set_txt_surface(self, value):
        self._txt_surface = value

    @property
    def rect(self):
        return self.__rect

    def update(self):
        # Resize the box if the text is too long.
        width = max(140, self._txt_surface.get_width() + 20)
        self.__rect.w = width
        return width

    def draw(self, screen):
        # Blit the text.
        screen.blit(self._txt_surface, (self.__rect.x + 5, self.__rect.y + 5))
        # Blit the rect.
        pygame.draw.rect(screen, self._color, self.__rect, 2)


def draw_point(params, screen):
    return Point(**params).draw(screen)


def draw_line(params, screen):
    return Line(**params).draw(screen)


def draw_textbox(params, screen):
    return TextBox(**params).draw(screen)


def draw_rect(params, screen):
    return Rectangle(**params).draw(screen)

def draw_circle(params, screen):
    return Circle(**params).draw(screen)
