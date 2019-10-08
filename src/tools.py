import pygame
import pygame.draw
from figures import Point, Line, TextBox
from datetime import datetime

black = [0, 0, 0]
red = [255, 0, 0]
green = [0, 255, 0]
blue = [0, 0, 255]
white = [255, 255, 255]
client = "client"


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
    def draw_point(event, color, font_size, screen, hist):
        coord = event.dict['pos']
        to_draw = Point(coord, event.dict['button'], color, font_size)
        to_draw.draw(screen)
        now = datetime.now()
        timestamp = datetime.timestamp(now)
        hist["actions"].append({"type": "Point",
                                "timestamp": timestamp,
                                "params": [coord, event.dict['button'], color, font_size],
                                "client": client})


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
                now = datetime.now()
                timestamp = datetime.timestamp(now)
                whiteboard.hist["actions"].append({"type": "Line",
                                                   "timestamp": timestamp,
                                                   "params": [whiteboard.config["active_color"], whiteboard.last_pos,
                                                              whiteboard.mouse_position,
                                                              whiteboard.config["font_size"]],
                                                   "client": client})
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


class HandleText(EventHandler, TextBox):
    def __init__(self):
        EventHandler.__init__(self)
        TextBox.__init__(self)

    @staticmethod
    def box_selection(whiteboard, event):
        if event.dict["button"] == 3:
            coord = event.dict['pos']
            text_box = TextBox(*coord, whiteboard.config["text_box"]["textbox_width"],
                               whiteboard.config["text_box"]["textbox_length"],
                               whiteboard.config["text_box"]["active_color"], whiteboard.config["text_box"]["font"],
                               whiteboard.config["text_box"]["font_size"])
            whiteboard.text_boxes.append(text_box)
            now = datetime.now()
            timestamp = datetime.timestamp(now)
            whiteboard.hist["actions"].append({"type": "Text_box",
                                               "timestamp": timestamp,
                                               "id": text_box.id_counter,
                                               "params": [*coord, whiteboard.config["text_box"]["textbox_width"],
                                                          whiteboard.config["text_box"]["textbox_length"],
                                                          whiteboard.config["text_box"]["active_color"],
                                                          whiteboard.config["text_box"]["font"],
                                                          whiteboard.config["text_box"]["font_size"],
                                                          ""],
                                               "client": client})
            text_box.draw(whiteboard.screen)
            if whiteboard.active_box is not None:
                whiteboard.active_box.color = whiteboard.config["text_box"]["inactive_color"] #supprimable
                id_counter = whiteboard.active_box.id_counter
                for action in [x for x in whiteboard.hist['actions'] if x['type'] == 'Text_box']:
                    if action['id'] == id_counter:
                        action['params'][-1] = whiteboard.active_box.text
                        action['params'][4] = whiteboard.config["text_box"]["inactive_color"]
                        whiteboard.load_actions(whiteboard.hist)
            whiteboard.active_box = text_box
        elif event.dict["button"] == 1:
            for box in whiteboard.text_boxes:
                if box.rect.collidepoint(event.pos):
                    whiteboard.active_box.color = whiteboard.config["text_box"]["inactive_color"]
                    id_counter = whiteboard.active_box.id_counter
                    for action in [x for x in whiteboard.hist['actions'] if x['type'] == 'Text_box']:
                        if action['id'] == id_counter:
                            action['params'][-1] = whiteboard.active_box.text
                            action['params'][4] = whiteboard.config["text_box"]["inactive_color"]
                    whiteboard.active_box.draw(whiteboard.screen)
                    whiteboard.active_box = box
                    whiteboard.active_box.color = whiteboard.config["text_box"]["active_color"]
                    id_counter = whiteboard.active_box.id_counter
                    for action in [x for x in whiteboard.hist['actions'] if x['type'] == 'Text_box']:
                        if action['id'] == id_counter:
                            action['params'][4] = whiteboard.config["text_box"]["active_color"]
                    box.draw(whiteboard.screen)

    @staticmethod
    def write_in_box(whiteboard, event):
        if whiteboard.active_box is not None:
            if event.key == pygame.K_RETURN:
                whiteboard.active_box.color = whiteboard.config["text_box"]["inactive_color"]
                whiteboard.active_box = None
            elif event.key == pygame.K_BACKSPACE:
                whiteboard.active_box.text = whiteboard.active_box.text[:-1]
                id_counter = whiteboard.active_box.id_counter
                for action in [x for x in whiteboard.hist['actions'] if x['type'] == 'Text_box']:
                    if action['id'] == id_counter:
                        action['params'][-1] = whiteboard.active_box.text
                whiteboard.screen.fill((255, 255, 255), (0, 31, whiteboard.config["width"], whiteboard.config["length"]-31))
                whiteboard.load_actions(whiteboard.hist)
            else:
                whiteboard.active_box.text += event.unicode
                id_counter = whiteboard.active_box.id_counter
                for action in [x for x in whiteboard.hist['actions'] if x['type'] == 'Text_box']:
                    if action['id'] == id_counter:
                        action['params'][-1] = whiteboard.active_box.text
                whiteboard.active_box.update(whiteboard.hist)
                whiteboard.screen.fill((255, 255, 255), (0, 31, whiteboard.config["width"], whiteboard.config["length"]-31))
                whiteboard.load_actions(whiteboard.hist)


        if whiteboard.active_box is not None:
            # Re-render the text.
            whiteboard.active_box.txt_surface = whiteboard.active_box.sysfont.render(whiteboard.active_box.text, True,
                                                                                     whiteboard.active_box.color)
