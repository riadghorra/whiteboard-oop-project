import pygame
import pygame.draw
import json
from functools import reduce
import operator

from figures import Point, Line, TextBox, draw_line, draw_point, draw_textbox
from tools import Mode, ColorBox, FontSizeBox, EventHandler, HandlePoint, HandleLine, HandleText

'''
Ouverture de la configuration initiale
'''

with open('config.json') as json_file:
    start_config = json.load(json_file)

with open('historique.json') as json_file:
    start_hist = json.load(json_file)

"""
Adresse client connecté au serveur
"""


class WhiteBoard:
    def __init__(self):
        pygame.init()
        self._done = False
        self._config = start_config
        self._hist = start_hist
        self._screen = pygame.display.set_mode([self._config["width"], self._config["length"]])
        self._screen.fill(self._config["board_background_color"])
        self._handler = {"line": HandleLine(self),
                        "point": HandlePoint(self),
                        "text": HandleText(self),
                        }
        pygame.draw.line(self._screen, self._config["active_color"], [0, self._config["toolbar_y"]],
                         [self._config["width"], self._config["toolbar_y"]], 1)

        self._modes = [Mode("point", (0, 0), tuple(self._config["mode_box_size"])),
                      Mode("line", (self._config["mode_box_size"][0], 0), tuple(self._config["mode_box_size"])),
                      Mode("text", (2 * self._config["mode_box_size"][0], 0), tuple(self._config["mode_box_size"]))
                      ]
        for mod in self._modes:
            mod.add(self._screen)

        """
        Choix des couleurs
        """
        self._colors = []
        box_counter = 1
        for key, value in self._config["color_palette"].items():
            color_box = ColorBox(value, (self._config["width"] - box_counter * self._config["mode_box_size"][0], 0),
                                 tuple(self._config["mode_box_size"]))
            box_counter += 1
            self._colors.append(color_box)
            color_box.add(self._screen)

        """
        Choix des épaisseurs
        """
        self._font_sizes = []
        for size in self._config["pen_sizes"]:
            font_size_box = FontSizeBox(size,
                                        (self._config["width"] - box_counter * self._config["mode_box_size"][0], 0),
                                        tuple(self._config["mode_box_size"]))
            box_counter += 1
            self._font_sizes.append(font_size_box)
            font_size_box.add(self._screen)

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

    """
    Encapsulation
    """

    def _get_is_done(self):
        return self._done

    def end(self):
        self._done = True

    def get_config(self, maplist):
        """
        Getter of config file. Uses a list of keys to traverse the config dict
        :param maplist: list of keys from parent to child to get the wanted value (list)
        :return: value of a key in the config file (object)
        """
        if not type(maplist) == list:
            maplist = list(maplist)
        try:
            return reduce(operator.getitem, maplist, self._config)
        except (KeyError, TypeError):
            return None

    def set_config(self, maplist, value):
        """
        Setter of config file. Uses the getter and assigns value to a key
        :param maplist: list of keys from parent to child to get the wanted value (list)
        :param value: value to set (object)
        :return: None if failed
        """
        if not type(maplist) == list:
            maplist = list(maplist)
        try:
            self.get_config(maplist[:-1])[maplist[-1]] = value
        except (KeyError, TypeError):
            return None

    def get_hist(self, key=None):
        if key is None:
            return self._hist
        else:
            return self._hist[key]

    def add_to_hist(self, key, value):
        self._hist[key].append(value)

    def get_screen(self):
        return self._screen

    def clear_screen(self):
        """
        Clear the screen by coloring it to background color. Does not color the toolbar
        :return:
        """
        self._screen.fill(self.get_config(["board_background_color"]), (0, self.get_config(["toolbar_y"]) + 1,
                                                                        self.get_config(["width"]),
                                                                        self.get_config(["length"]) - self.get_config(
                                                                            ["toolbar_y"]) + 1))

    def switch_config(self, event=None):
        if event == "quit":
            self.set_config(["mode"], "quit")
        else:
            for mod in self._modes:
                if mod.is_triggered(event):
                    self.set_config(["mode"], mod.name)
            for col in self._colors:
                if col.is_triggered(event):
                    self.set_config(["text_box", "text_color"], col.color)
                    self.set_config(["active_color"], col.color)
            for font_size_ in self._font_sizes:
                if font_size_.is_triggered(event):
                    self.set_config(["font_size"], font_size_.font_size)

    def load_actions(self, hist):
        sred = sorted(hist["actions"],
                      key=lambda value: value["timestamp"])
        for action in sred:
            if action["type"] == "Point":
                draw_point(action["params"], self.get_screen())
            if action["type"] == "Line":
                draw_line(action["params"], self.get_screen())
            if action["type"] == "Text_box":
                draw_textbox(action["params"], self.get_screen())

    def start(self):
        while not self._get_is_done():
            for event in pygame.event.get():
                if self.get_config(["mode"]) == "quit":
                    self.end()
                    break
                self._handler[self.get_config(["mode"])].handle_all(event)
        pygame.quit()
