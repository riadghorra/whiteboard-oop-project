import socket
import json
import pygame
import pygame.draw
from figures import Point, Line, TextBox, draw_line, draw_point, draw_textbox
from tools import Mode, ColorBox, FontSizeBox, EventHandler, HandlePoint, HandleLine, HandleText
import json

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
    return bytes(str,'utf-8')


def binary_to_dict(the_binary):
    jsn = ''.join(the_binary.decode("utf-8"))
    d = json.loads(jsn)
    return d

connexion_avec_serveur = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
connexion_avec_serveur.connect((hote, port))
print("Connexion réussie avec le serveur")


msg_recu = connexion_avec_serveur.recv(2**20)
msg_decode=binary_to_dict(msg_recu)
start_hist=msg_decode








class WhiteBoard:
    def __init__(self):
        pygame.init()
        self.done = False
        self.config = start_config
        self.hist = start_hist
        self.screen = pygame.display.set_mode([self.config["width"], self.config["length"]])
        self.screen.fill(self.config["board_background_color"])
        pygame.draw.line(self.screen, self.config["active_color"], [0, 30], [self.config["width"], 30], 1)

        self.modes = [Mode("point", (0, 0), tuple(self.config["mode_box_size"])),
                      Mode("line", (self.config["mode_box_size"][0], 0), tuple(self.config["mode_box_size"])),
                      Mode("text", (2 * self.config["mode_box_size"][0], 0), tuple(self.config["mode_box_size"]))
                      ]
        for mod in self.modes:
            mod.add(self.screen)

        """
        Choix des couleurs
        """
        self.colors = []
        box_counter = 1
        for key, value in self.config["color_palette"].items():
            color_box = ColorBox(value, (self.config["width"] - box_counter * self.config["mode_box_size"][0], 0),
                                 tuple(self.config["mode_box_size"]))
            box_counter += 1
            self.colors.append(color_box)
            color_box.add(self.screen)

        """
        Choix des épaisseurs
        """
        self.font_sizes = []
        for size in self.config["pen_sizes"]:
            font_size_box = FontSizeBox(size, (self.config["width"] - box_counter * self.config["mode_box_size"][0], 0),
                                        tuple(self.config["mode_box_size"]))
            box_counter += 1
            self.font_sizes.append(font_size_box)
            font_size_box.add(self.screen)

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
        self.load_actions(self.hist)

    def switch_config(self, event=None):
        if event == "quit":
            self.config["mode"] = "quit"
        else:
            for mod in self.modes:
                if mod.is_triggered(event):
                    self.config["mode"] = mod.name
            for col in self.colors:
                if col.is_triggered(event):
                    self.config["text_box"]["text_color"] = col.color
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
        pygame.display.flip()

    def start(self):
        self.handler = {"line": HandleLine(self),
                        "point": HandlePoint(self),
                        "text": HandleText(self),
                        }
        while not self.done:
            for event in pygame.event.get():
                if self.config["mode"] == "quit":
                    self.done = True
                    break
                self.handler[self.config["mode"]].handle_all(event)
        pygame.quit()



whiteboard=WhiteBoard()
whiteboard.start()
