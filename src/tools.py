import pygame
import pygame.draw
from figures import Point, Line, TextBox
from datetime import datetime

client = "client"


class TriggerBox:
    def __init__(self, top_left, size):
        self.rect = pygame.Rect(top_left, size)
        self.coords = top_left

    def is_triggered(self, event):
        return self.rect.collidepoint(event.pos)


class Mode(TriggerBox):
    def __init__(self, name, top_left, size):
        super(Mode, self).__init__(top_left, size)
        self.name = name

    def add(self, screen):
        pygame.draw.rect(screen, [0, 0, 0], self.rect, 1)
        font = pygame.font.Font(None, 18)
        legend = {"text": font.render(self.name, True, [0, 0, 0]), "coords": self.coords}
        screen.blit(legend["text"], legend["coords"])


class ColorBox(TriggerBox):
    def __init__(self, color, top_left, size):
        super(ColorBox, self).__init__(top_left, size)
        self.color = color

    def add(self, screen):
        pygame.draw.rect(screen, self.color, self.rect)


class FontSizeBox(TriggerBox):
    def __init__(self, font_size, top_left, size):
        super(FontSizeBox, self).__init__(top_left, size)
        self.font_size = font_size
        self.center = [top_left[0] + size[0] // 2, top_left[1] + size[1] // 2]

    def add(self, screen):
        pygame.draw.rect(screen, [0, 0, 0], self.rect, 1)
        pygame.draw.circle(screen, [0, 0, 0], self.center, self.font_size)


class EventHandler:
    def __init__(self, whiteboard):
        self.whiteboard = whiteboard

    def handle(self, event):
        out = False
        if event.type == pygame.QUIT:
            self.whiteboard.end()
            self.whiteboard.switch_config("quit")
            out = True
        if event.type == pygame.MOUSEBUTTONDOWN:
            coord = event.dict['pos']
            if coord[1] <= self.whiteboard.get_config(["toolbar_y"]):
                self.whiteboard.switch_config(event)
                out = True
        return out


class HandlePoint(EventHandler):
    def __init__(self, whiteboard):
        EventHandler.__init__(self, whiteboard)

    def handle_all(self, event):
        handled = self.handle(event)
        if handled:
            return
        if event.type == pygame.MOUSEBUTTONDOWN:
            coord = event.dict["pos"]
            to_draw = Point(coord,
                            event.dict['button'],
                            self.whiteboard.get_config(["active_color"]),
                            self.whiteboard.get_config(["font_size"]))
            to_draw.draw(self.whiteboard.get_screen())
            now = datetime.now()
            timestamp = datetime.timestamp(now)
            self.whiteboard.add_to_hist("actions", {"type": "Point", "timestamp": timestamp,
                                                    "params": {"coord": coord, "clicktype": event.dict['button'],
                                                               "point_color": self.whiteboard.get_config(
                                                                   ["active_color"]),
                                                               "font_size": self.whiteboard.get_config(["font_size"])},
                                                    "client": client})


class HandleLine(EventHandler):
    def __init__(self, whiteboard):
        EventHandler.__init__(self, whiteboard)

    def handle_mouse_motion(self):
        if self.whiteboard.draw:
            self.whiteboard.mouse_position = pygame.mouse.get_pos()
            if self.whiteboard.mouse_position[1] <= self.whiteboard.get_config(["toolbar_y"]):
                self.whiteboard.draw = False
            elif self.whiteboard.last_pos is not None:
                to_draw = Line(self.whiteboard.get_config(["active_color"]), self.whiteboard.last_pos,
                               self.whiteboard.mouse_position,
                               self.whiteboard.get_config(["font_size"]))
                to_draw.draw(self.whiteboard.get_screen())
                now = datetime.now()
                timestamp = datetime.timestamp(now)
                self.whiteboard.add_to_hist("actions", {"type": "Line", "timestamp": timestamp,
                                                        "params": {
                                                            "line_color": self.whiteboard.get_config(["active_color"]),
                                                            "start_pos": self.whiteboard.last_pos,
                                                            "end_pos": self.whiteboard.mouse_position,
                                                            "font_size": self.whiteboard.get_config(["font_size"])},
                                                        "client": client})
            self.whiteboard.last_pos = self.whiteboard.mouse_position

    def handle_mouse_button_up(self):
        self.whiteboard.mouse_position = (0, 0)
        self.whiteboard.draw = False
        self.whiteboard.last_pos = None

    def handle_mouse_button_down(self):
        self.whiteboard.draw = True

    def handle_all(self, event):
        handled = self.handle(event)
        if handled:
            return
        elif event.type == pygame.MOUSEMOTION:
            self.handle_mouse_motion()
        elif event.type == pygame.MOUSEBUTTONUP:
            self.handle_mouse_button_up()
        elif event.type == pygame.MOUSEBUTTONDOWN:
            self.handle_mouse_button_down()
        pygame.display.flip()


class HandleText(EventHandler):
    def __init__(self, whiteboard):
        EventHandler.__init__(self, whiteboard)

    def box_selection(self, event):
        if event.dict["button"] == 3:
            coord = event.dict['pos']
            text_box = TextBox(*coord, self.whiteboard.get_config(["text_box", "textbox_width"]),
                               self.whiteboard.get_config(["text_box", "textbox_length"]),
                               self.whiteboard.get_config(["text_box", "active_color"]),
                               self.whiteboard.get_config(["text_box", "font"]),
                               self.whiteboard.get_config(["text_box", "font_size"]), "",
                               self.whiteboard.get_config(["active_color"]))
            self.whiteboard.text_boxes.append(text_box)
            now = datetime.now()
            timestamp = datetime.timestamp(now)
            self.whiteboard.add_to_hist("actions", {"type": "Text_box", "timestamp": timestamp,
                                                    "id": text_box.id_counter,
                                                    "params": {"x": coord[0], "y": coord[1],
                                                               "w": self.whiteboard.get_config(
                                                                   ["text_box", "textbox_width"]),
                                                               "h": self.whiteboard.get_config(
                                                                   ["text_box", "textbox_length"]),
                                                               "box_color": self.whiteboard.get_config(
                                                                   ["text_box", "active_color"]),
                                                               "font": self.whiteboard.get_config(["text_box", "font"]),
                                                               "font_size": self.whiteboard.get_config(
                                                                   ["text_box", "font_size"]),
                                                               "text": "",
                                                               "text_color": self.whiteboard.get_config(
                                                                   ["active_color"])},
                                                    "client": client})
            text_box.draw(self.whiteboard.get_screen())
            if self.whiteboard.active_box is not None:
                self.whiteboard.active_box.color = self.whiteboard.get_config(["text_box", "inactive_color"])
                id_counter = self.whiteboard.active_box.id_counter
                for action in [x for x in self.whiteboard.get_hist('actions') if x['type'] == 'Text_box']:
                    if action['id'] == id_counter:
                        action['params']["text"] = self.whiteboard.active_box.text
                        action['params']["box_color"] = self.whiteboard.get_config(["text_box", "inactive_color"])
                        self.whiteboard.load_actions(self.whiteboard.get_hist())
            self.whiteboard.active_box = text_box
        elif event.dict["button"] == 1:
            for box in self.whiteboard.text_boxes:
                if box.rect.collidepoint(event.pos):
                    if self.whiteboard.active_box is not None:
                        self.whiteboard.active_box.color = self.whiteboard.get_config(["text_box", "inactive_color"])
                    id_counter = self.whiteboard.active_box.id_counter
                    for action in [x for x in self.whiteboard.get_hist('actions') if x['type'] == 'Text_box']:
                        if action['id'] == id_counter:
                            action['params']["text"] = self.whiteboard.active_box.text
                            action['params']["box_color"] = self.whiteboard.get_config(["text_box", "inactive_color"])
                    self.whiteboard.active_box.draw(self.whiteboard.get_screen())
                    self.whiteboard.active_box = box
                    self.whiteboard.active_box.color = self.whiteboard.get_config(["text_box", "active_color"])
                    id_counter = self.whiteboard.active_box.id_counter
                    for action in [x for x in self.whiteboard.get_hist('actions') if x['type'] == 'Text_box']:
                        if action['id'] == id_counter:
                            action['params']["box_color"] = self.whiteboard.get_config(["text_box", "active_color"])
                    box.draw(self.whiteboard.get_screen())

    def write_in_box(self, event):
        if self.whiteboard.active_box is not None:
            if event.key == pygame.K_BACKSPACE:
                self.whiteboard.active_box.text = self.whiteboard.active_box.text[:-1]
                id_counter = self.whiteboard.active_box.id_counter
                for action in [x for x in self.whiteboard.get_hist('actions') if x['type'] == 'Text_box']:
                    if action['id'] == id_counter:
                        action['params']["text"] = self.whiteboard.active_box.text
                self.whiteboard.clear_screen()
                self.whiteboard.load_actions(self.whiteboard.get_hist())
            elif event.key == pygame.K_TAB or event.key == pygame.K_RETURN:
                pass
            else:
                self.whiteboard.active_box.text += event.unicode
                id_counter = self.whiteboard.active_box.id_counter
                for action in [x for x in self.whiteboard.get_hist('actions') if x['type'] == 'Text_box']:
                    if action['id'] == id_counter:
                        action['params']["text"] = self.whiteboard.active_box.text
                self.whiteboard.active_box.update(self.whiteboard.get_hist())
                self.whiteboard.clear_screen()
                self.whiteboard.load_actions(self.whiteboard.get_hist())

        if self.whiteboard.active_box is not None:
            # Re-render the text.
            self.whiteboard.active_box.txt_surface = self.whiteboard.active_box.sysfont.render(
                self.whiteboard.active_box.text, True,
                self.whiteboard.active_box.color)

    def handle_all(self, event):
        handled = self.handle(event)
        if handled:
            return
        if event.type == pygame.MOUSEBUTTONDOWN:
            self.box_selection(event)
        if event.type == pygame.KEYDOWN:
            self.write_in_box(event)
        pygame.display.flip()
