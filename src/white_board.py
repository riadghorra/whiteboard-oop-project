import pygame
import pygame.draw
from figures import Point, Line, TextBox, draw_line, draw_point, draw_textbox
from tools import mode, color_box, font_size_box
import json


'''
Ouverture de la configuration initiale
'''

with open('config.json') as json_file:
    start_config = json.load(json_file)

with open('historique.json') as json_file:
    start_hist = json.load(json_file)

black = [0, 0, 0]
red = [255, 0, 0]
green = [0, 255, 0]
blue = [0, 0, 255]
white = [255, 255, 255]

client = "client"
"""
Adresse client connecté au serveur
"""


class WhiteBoard:
    def __init__(self):
        pygame.init()
        self.done = False
        self.config = start_config
        self.hist = start_hist
        self.screen = pygame.display.set_mode([self.config["width"], self.config["length"]])
        self.screen.fill(self.config["board_background_color"])
        pygame.draw.line(self.screen, black, [0, 30], [self.config["width"], 30], 1)

        self.modes = [mode("point", (0, 0), tuple(self.config["mode_box_size"])),
                      mode("line", (self.config["mode_box_size"][0], 0), tuple(self.config["mode_box_size"])),
                      mode("text", (2 * self.config["mode_box_size"][0], 0), tuple(self.config["mode_box_size"]))
                      ]
        for mod in self.modes:
            mod.add(self.screen)

        """
        Choix des couleurs
        """
        self.colors = [color_box(red, (self.config["width"] - self.config["mode_box_size"][0], 0),
                                 tuple(self.config["mode_box_size"])),
                       color_box(green, (self.config["width"] - 2 * self.config["mode_box_size"][0], 0),
                                 tuple(self.config["mode_box_size"])),
                       color_box(blue, (self.config["width"] - 3 * self.config["mode_box_size"][0], 0),
                                 tuple(self.config["mode_box_size"])),
                       color_box(black, (self.config["width"] - 4 * self.config["mode_box_size"][0], 0),
                                 tuple(self.config["mode_box_size"]))
                       ]
        for color in self.colors:
            color.add(self.screen)

        """
        Choix des épaisseurs
        """
        self.font_sizes = [font_size_box(5, (self.config["width"] - 5 * self.config["mode_box_size"][0], 0),
                                         tuple(self.config["mode_box_size"])),
                           font_size_box(8, (self.config["width"] - 6 * self.config["mode_box_size"][0], 0),
                                         tuple(self.config["mode_box_size"])),
                           font_size_box(10, (self.config["width"] - 7 * self.config["mode_box_size"][0], 0),
                                         tuple(self.config["mode_box_size"])),
                           font_size_box(12, (self.config["width"] - 8 * self.config["mode_box_size"][0], 0),
                                         tuple(self.config["mode_box_size"]))
                           ]
        for font_size in self.font_sizes:
            font_size.add(self.screen)

        """
        initialisation des variables de dessin
        """
        pygame.display.flip()
        self.draw = False
        self.last_pos = None
        self.mouse_position = (0, 0)

        """
        Initialisation des paramètres des text boxes
        """
        self.text_boxes = []
        self.active_box = None

    def switch_config(self, event=None):
        if event == "quit":
            self.config["mode"] = "quit"
        else:
            for mod in self.modes:
                if mod.is_triggered(event):
                    self.config["mode"] = mod.name
            for col in self.colors:
                if col.is_triggered(event):
                    self.config["active_color"] = col.color
            for font_size_ in self.font_sizes:
                if font_size_.is_triggered(event):
                    self.config["font_size"] = font_size_.font_size

    def handle_event_point_mode(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            coord = event.dict['pos']
            if coord[1] <= 30:
                self.switch_config(event)
            else:
                to_draw = Point(coord, event.dict['button'], self.config["active_color"], self.config["font_size"])
                to_draw.draw(self.screen)

        if event.type == pygame.QUIT:
            self.done = True
            self.switch_config("quit")

    def handle_event_line_mode(self, event):
        if event.type == pygame.QUIT:
            self.done = True
            self.switch_config("quit")
        elif event.type == pygame.MOUSEMOTION:
            if self.draw:
                self.mouse_position = pygame.mouse.get_pos()
                if self.mouse_position[1] <= 30:
                    self.draw = False
                elif self.last_pos is not None:
                    to_draw = Line(self.config["active_color"], self.last_pos, self.mouse_position,
                                   self.config["font_size"])
                    to_draw.draw(self.screen)
                self.last_pos = self.mouse_position
        elif event.type == pygame.MOUSEBUTTONUP:
            self.mouse_position = (0, 0)
            self.draw = False
            self.last_pos = None
        elif event.type == pygame.MOUSEBUTTONDOWN:
            coord = event.dict['pos']
            if coord[1] <= 30:
                self.switch_config(event)
            else:
                self.draw = True

    def handle_event_text_mode(self, event):
        if event.type == pygame.QUIT:
            self.done = True
            self.switch_config("quit")
        if event.type == pygame.MOUSEBUTTONDOWN:
            coord = event.dict['pos']
            if coord[1] <= 30:
                self.switch_config(event)
                self.active_box = None
            else:
                if event.dict["button"] == 3:
                    text_box = TextBox(*coord, self.config["text_box"]["textbox_width"],
                                       self.config["text_box"]["textbox_length"],
                                       self.config["text_box"]["active_color"], self.config["text_box"]["font"],
                                       self.config["text_box"]["font_size"])
                    self.text_boxes.append(text_box)
                    if self.active_box is not None:
                        self.active_box.color = self.config["text_box"]["inactive_color"]
                    self.active_box = text_box
                elif event.dict["button"] == 1:
                    for box in self.text_boxes:
                        if box.rect.collidepoint(event.pos):
                            self.active_box.color = self.config["text_box"]["inactive_color"]
                            self.active_box = box
                            self.active_box.color = self.config["text_box"]["active_color"]

        if event.type == pygame.KEYDOWN:
            if self.active_box is not None:
                if event.key == pygame.K_RETURN:
                    self.active_box = None
                elif event.key == pygame.K_BACKSPACE:
                    self.active_box.text = self.active_box.text[:-1]
                else:
                    self.active_box.text += event.unicode

            if self.active_box is not None:
                # Re-render the text.
                self.active_box.txt_surface = self.active_box.sysfont.render(self.active_box.text, True,
                                                                             self.active_box.color)

        for box in self.text_boxes:
            box.update()

        self.screen.fill((255, 255, 255))# de la merde il faut stocker toutes les text box
        
        for box in self.text_boxes:
            box.draw(self.screen)

        pygame.display.flip()
    
    def load_actions(self, hist):
        sred = sorted(hist["actions"],
                           key=lambda value: value["timestamp"])
        for action in sred :
            if action["type"] == "Point":
                draw_point(action["params"], self.screen)
            if action["type"] == "Line":
                draw_line(action["params"], self.screen)
            if action["type"] == "Text_box":
                draw_textbox(action["params"], self.screen)
                
    def start(self):
        while not self.done:
            while self.config["mode"] == "point":
                for event in pygame.event.get():
                    self.handle_event_point_mode(event)
            while self.config["mode"] == "line":
                for event in pygame.event.get():
                    self.handle_event_line_mode(event)
                pygame.display.update()
            while self.config["mode"] == "text":
                for event in pygame.event.get():
                    self.handle_event_text_mode(event)
        pygame.quit()
