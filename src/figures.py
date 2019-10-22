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
    id_counter = 0

    def __init__(self, x, y, w, h, box_color, font, font_size, text, text_color):
        self.rect = pygame.Rect(x, y, w, h)
        self._color = box_color
        self._text = text
        self._sysfont = pygame.font.SysFont(font, font_size)
        self._text_color = text_color
        self._txt_surface = self._sysfont.render(text, True, self._text_color)
        self.id_counter = TextBox.id_counter
        TextBox.id_counter += 1

    """
    Encapsulation
    """

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

    def update(self, hist):
        # Resize the box if the text is too long.
        width = max(140, self._txt_surface.get_width() + 20)
        self.rect.w = width
        for action in [x for x in hist['actions'] if x['type'] == 'Text_box']:
            if action['id'] == self.id_counter:
                action['params']["w"] = width

    def draw(self, screen):
        # Blit the text.
        screen.blit(self._txt_surface, (self.rect.x + 5, self.rect.y + 5))
        # Blit the rect.
        pygame.draw.rect(screen, self._color, self.rect, 2)


def draw_point(params, screen):
    return Point(**params).draw(screen)


def draw_line(params, screen):
    return Line(**params).draw(screen)


def draw_textbox(params, screen):
    return TextBox(**params).draw(screen)
