import socket
import json
import pygame
import pygame.draw
from figures import Point, Line, TextBox, draw_line, draw_point, draw_textbox
from tools import Mode, ColorBox, FontSizeBox, EventHandler, HandlePoint, HandleLine, HandleText
# from white_board import WhiteBoard
import json
from functools import reduce
import operator

'''
Ouverture de la configuration initiale
'''

with open('config.json') as json_file:
    start_config = json.load(json_file)

hote = '127.0.0.1'
'''IP d'Arthur
'''
port = 5001


def dict_to_binary(the_dict):
    str = json.dumps(the_dict)
    return bytes(str, 'utf-8')


def binary_to_dict(the_binary):
    jsn = ''.join(the_binary.decode("utf-8"))
    d = json.loads(jsn)
    return d



class WhiteBoard:
    def __init__(self, name, start_hist=None):
        pygame.init()
        self._done = False
        self._config = start_config
        self._name=name
        if start_hist is None:
            start_hist = {"actions": []}
        self._hist = start_hist
        self.__screen = pygame.display.set_mode([self._config["width"], self._config["length"]])
        self.__screen.fill(self._config["board_background_color"])
        self.__handler = {"line": HandleLine(self),
                          "point": HandlePoint(self),
                          "text": HandleText(self),
                          }
        pygame.draw.line(self.__screen, self._config["active_color"], [0, self._config["toolbar_y"]],
                         [self._config["width"], self._config["toolbar_y"]], 1)

        self.__modes = [Mode("point", (0, 0), tuple(self._config["mode_box_size"])),
                        Mode("line", (self._config["mode_box_size"][0], 0), tuple(self._config["mode_box_size"])),
                        Mode("text", (2 * self._config["mode_box_size"][0], 0), tuple(self._config["mode_box_size"]))
                        ]
        for mod in self.__modes:
            mod.add(self.__screen)

        """
        Choix des couleurs
        """
        self.__colors = []
        box_counter = 1
        for key, value in self._config["color_palette"].items():
            color_box = ColorBox(value, (self._config["width"] - box_counter * self._config["mode_box_size"][0], 0),
                                 tuple(self._config["mode_box_size"]))
            box_counter += 1
            self.__colors.append(color_box)
            color_box.add(self.__screen)

        """
        Choix des épaisseurs
        """
        self.__font_sizes = []
        for size in self._config["pen_sizes"]:
            font_size_box = FontSizeBox(size,
                                        (self._config["width"] - box_counter * self._config["mode_box_size"][0], 0),
                                        tuple(self._config["mode_box_size"]))
            box_counter += 1
            self.__font_sizes.append(font_size_box)
            font_size_box.add(self.__screen)

        """
        initialisation des variables de dessin
        """
        pygame.display.flip()
        self._draw = False
        self._last_pos = None
        self._mouse_position = (0, 0)

        """
        Initialisation des paramètres des text boxes
        """
        self._text_boxes = []
        for action in self._hist["actions"]:
            if action["type"] == "Text_box":
                self._text_boxes.append(TextBox(**action["params"]))


        self.active_box = None

        self.load_actions(self._hist)

    """
    Encapsulation
    """

    def is_done(self):
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

    def add_to_hist(self, value):
        self._hist["actions"].append(value)

    @property
    def screen(self):
        return self.__screen

    def clear_screen(self):
        """
        Clear the screen by coloring it to background color. Does not color the toolbar
        :return:
        """
        self.__screen.fill(self.get_config(["board_background_color"]), (0, self.get_config(["toolbar_y"]) + 1,
                                                                         self.get_config(["width"]),
                                                                         self.get_config(["length"]) - self.get_config(
                                                                             ["toolbar_y"]) + 1))

    def is_drawing(self):
        return self._draw

    def pen_up(self):
        self._draw = False

    def pen_down(self):
        self._draw = True

    @property
    def last_pos(self):
        return self._last_pos

    def reset_last_pos(self):
        self._last_pos = None

    def update_last_pos(self):
        self._last_pos = self._mouse_position

    def __get_mouse_position(self):
        return self._mouse_position

    def __set_mouse_position(self, value):
        self._mouse_position = value

    mouse_position = property(__get_mouse_position, __set_mouse_position)

    def get_text_boxes(self):
        return self._text_boxes

    def append_text_box(self, textbox):
        self._text_boxes.append(textbox)

    def draw(self, obj, timestamp):
        obj.draw(self.__screen)
        hist_obj = {"type": obj.type, "timestamp": timestamp, "params": obj.fetch_params(), "client": self._name}
        if hist_obj["type"] == "Text_box":
            hist_obj["id"] = obj.id_counter
        self.add_to_hist(hist_obj)

    def switch_config(self, event=None):
        if event == "quit":
            self.set_config(["mode"], "quit")
        else:
            for mod in self.__modes:
                if mod.is_triggered(event):
                    self.set_config(["mode"], mod.name)
            for col in self.__colors:
                if col.is_triggered(event):
                    self.set_config(["text_box", "text_color"], col.color)
                    self.set_config(["active_color"], col.color)
            for font_size_ in self.__font_sizes:
                if font_size_.is_triggered(event):
                    self.set_config(["font_size"], font_size_.font_size)

    def load_actions(self, hist):
        sred = sorted(hist["actions"],
                      key=lambda value: value["timestamp"])
        for action in sred:
            if action["type"] == "Point":
                draw_point(action["params"], self.__screen)
            if action["type"] == "Line":
                draw_line(action["params"], self.__screen)
            if action["type"] == "Text_box":
                draw_textbox(action["params"], self.__screen)
        pygame.display.flip()

    def start(self):
        print("bla")
        last_timestamp=0
        for action in hist["actions"]:
            if action["timestamp"] > last_timestamp:
                last_timestamp=action["timestamp"]
        while not self.is_done():
            for event in pygame.event.get():
                if self.get_config(["mode"]) == "quit":
                    self.end()
                    break
                self.__handler[self.get_config(["mode"])].handle_all(event)
            msg_a_envoyer = self.get_hist()
            msg_a_envoyer["message"] = "CARRY ON"
            #print(msg_a_envoyer)
            connexion_avec_serveur.send(dict_to_binary(msg_a_envoyer))
            #print("hist envoyé")
            msg_recu = connexion_avec_serveur.recv(2 ** 24)
            new_hist = binary_to_dict(msg_recu)
            new_last_timestamp=last_timestamp
            for action in new_hist["actions"]:
                if action["timestamp"] > last_timestamp:
                    self.add_to_hist(action)
                    print('UPDATE')
                    if action["timestamp"] > new_last_timestamp:
                        new_last_timestamp=action["timestamp"]
            last_timestamp=new_last_timestamp

        pygame.quit()
        print("Fermeture de la connexion")
        msg_a_envoyer["message"] = "END"
        connexion_avec_serveur.send(dict_to_binary(msg_a_envoyer))
        connexion_avec_serveur.close()



connexion_avec_serveur = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
connexion_avec_serveur.connect((hote, port))
print("Connexion réussie avec le serveur")

msg_recu = connexion_avec_serveur.recv(2 ** 24)
msg_decode = binary_to_dict(msg_recu)
hist = msg_decode
whiteboard = WhiteBoard("client2", hist)
whiteboard.start()
