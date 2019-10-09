import pygame
import pygame.draw
from figures import Point, Line, TextBox, draw_line, draw_point, draw_textbox
from tools import mode, color_box, font_size_box, EventHandler, HandlePoint, HandleLine, HandleText
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

    def load_actions(self, hist):
        sred = sorted(hist["actions"],
                      key=lambda value: value["timestamp"])
        for action in sred:
            if action["type"] == "Point":
                draw_point(action["params"], self.screen)
            if action["type"] == "Line":
                draw_line(action["params"], self.screen)
            if action["type"] == "Text_box":
                draw_textbox(action["params"], self.screen, hist)

    def start(self):
        self.handler = {"line" : HandleLine(self),
                        "point" : HandlePoint(self),
                        "text" : HandleText(self),
                        }
        while not self.done:
            for event in pygame.event.get():
                if self.config["mode"] == "quit" :
                    self.done = True
                    break
                self.handler[self.config["mode"]].handle_all(event)
        pygame.quit()
