import pygame
import pygame.draw
from figures import Point, Line, TextBox

black = [0, 0, 0]
red = [255, 0, 0]
green = [0, 255, 0]
blue = [0, 0, 255]
white = [255, 255, 255]


class trigger_box():
    def __init__(self, top_left, size):
        self.rect = pygame.Rect(top_left, size)
        self.coords = top_left

    def is_triggered(self, event):
        return self.rect.collidepoint(event.pos)


class mode(trigger_box):
    def __init__(self, name, top_left, size):
        super(mode, self).__init__(top_left, size)
        self.name = name

    def add(self, screen):
        pygame.draw.rect(screen, black, self.rect, 1)
        font = pygame.font.Font(None, 18)
        legend = {"text": font.render(self.name, True, [0, 0, 0]), "coords": self.coords}
        screen.blit(legend["text"], legend["coords"])


class color_box(trigger_box):
    def __init__(self, color, top_left, size):
        super(color_box, self).__init__(top_left, size)
        self.color = color

    def add(self, screen):
        pygame.draw.rect(screen, self.color, self.rect)


class font_size_box(trigger_box):
    def __init__(self, font_size, top_left, size):
        super(font_size_box, self).__init__(top_left, size)
        self.font_size = font_size
        self.center = [top_left[0] + size[0] // 2, top_left[1] + size[1] // 2]

    def add(self, screen):
        pygame.draw.rect(screen, black, self.rect, 1)
        pygame.draw.circle(screen, black, self.center, self.font_size)


class EventHandler:
    def __init__(self):
        pass

    @staticmethod
    def handle(whiteboard, event):
        out = False
        if event.type == pygame.QUIT:
            whiteboard.done = True
            whiteboard.switch_config("quit")
            out = True
        if event.type == pygame.MOUSEBUTTONDOWN:
            coord = event.dict['pos']
            if coord[1] <= 30:
                whiteboard.switch_config(event)
                out = True
        return out


class HandlePoint(EventHandler, Point):
    def __init__(self):
        EventHandler.__init__(self)
        Point.__init__(self)

    @staticmethod
    def draw_point(event, color, font_size, screen):
        coord = event.dict['pos']
        to_draw = Point(coord, event.dict['button'], color, font_size)
        to_draw.draw(screen)


class HandleLine(EventHandler, Line):
    def __init__(self):
        EventHandler.__init__(self)
        Line.__init__(self)

    @staticmethod
    def handle_mouse_motion(whiteboard):
        if whiteboard.draw:
            whiteboard.mouse_position = pygame.mouse.get_pos()
            if whiteboard.mouse_position[1] <= 30:
                whiteboard.draw = False
            elif whiteboard.last_pos is not None:
                to_draw = Line(whiteboard.config["active_color"], whiteboard.last_pos, whiteboard.mouse_position,
                               whiteboard.config["font_size"])
                to_draw.draw(whiteboard.screen)
            whiteboard.last_pos = whiteboard.mouse_position

    @staticmethod
    def handle_mouse_button_up(whiteboard):
        whiteboard.mouse_position = (0, 0)
        whiteboard.draw = False
        whiteboard.last_pos = None

    @staticmethod
    def handle_mouse_button_down(whiteboard):
        whiteboard.draw = True

    @staticmethod
    def handle_all(whiteboard, event):
        if event.type == pygame.MOUSEMOTION:
            HandleLine.handle_mouse_motion(whiteboard)
        elif event.type == pygame.MOUSEBUTTONUP:
            HandleLine.handle_mouse_button_up(whiteboard)
        elif event.type == pygame.MOUSEBUTTONDOWN:
            whiteboard.draw = True
