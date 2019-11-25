import pygame
import pygame.draw
import json
import sys
from functools import reduce
import operator
from figures import TextBox, draw_line, draw_point, draw_textbox, draw_rect, draw_circle
from tools import Mode, ColorBox, Auth, Save, FontSizeBox, HandlePoint, HandleLine, HandleText, HandleRect, HandleCircle
import copy

'''
Ouverture de la configuration initiale
'''


def dict_to_binary(the_dict):
    str = json.dumps(the_dict)
    return bytes(str, 'utf-8')


def binary_to_dict(binary):
    try:
        jsn = ''.join(binary.decode("utf-8"))
        d = json.loads(jsn)
    except (TypeError, json.decoder.JSONDecodeError) as e:
        if e == TypeError:
            print("Le message reçu n'est pas du format attendu")
        else:
            print('A figure has been lost, it was unexcepted')
        return {"actions": [], "message": [], "auth": []}
    return d


class WhiteBoard:
    def __init__(self, client_name, start_config, start_hist=None):
        """
        Whiteboard initialization : we build the GUI using the config file and the potential history of actions made by
         other users. Returns a Whiteboard window ready to use.

        :param client_name: Name of the client who just opened a new whiteboard window (str)
        :param start_config: Whiteboard configuration stored in config.json and loaded as a dict (dict)
        :param start_hist: History of actions by other users (dict)
        """
        pygame.init()

        if not isinstance(client_name, str):
            raise TypeError("Client name must be a string")
        if not isinstance(start_config, dict):
            raise TypeError("Starting configuration file must be a dictionary")
        if start_hist is None:
            start_hist = {"actions": [], "message": [], "auth": []}
        elif not isinstance(start_hist, dict):
            raise TypeError("Starting history file must be a dictionary")

        self._done = False
        self._config = start_config
        self._name = client_name
        self._hist = start_hist
        self.__screen = pygame.display.set_mode([self._config["width"], self._config["length"]])
        self.__screen.fill(self._config["board_background_color"])
        self.__handler = {"line": HandleLine(self),
                          "point": HandlePoint(self),
                          "text": HandleText(self),
                          "rect": HandleRect(self),
                          "circle": HandleCircle(self)}

        pygame.draw.line(self.__screen, self._config["active_color"], [0, self._config["toolbar_y"]],
                         [self._config["width"], self._config["toolbar_y"]], 1)

        # We create a global variable to keep track of the position of the last mode box we create in order to make
        # sure that there is no overlapping between left and right boxes on the toolbar on the toolbar

        """
        Tracé de la box auth, qui permet de donner l'autorisation de modification des textbox
        """


        last_left_position = 0
        last_right_position = self._config["width"] - self._config["mode_box_size"][0]
        self._erasing_auth = False

        try:
            assert last_left_position < last_right_position + 1, "Too many tools to fit in the Whiteboard " \
                                                                 "toolbar, please increase width in config.json"
            self.__auth_box = Auth((last_left_position, 0), tuple(self._config["auth_box_size"]))
            last_left_position += self._config["mode_box_size"][0]
            self.__auth_box.add(self.__screen)
        except AssertionError as e:
            print(e)
            pygame.quit()
            sys.exit()

        """
        Tracé de la boite save qui permet d'enregistrer l'image
        """

        try:
            assert last_left_position < last_right_position + 1, "Too many tools to fit in the Whiteboard " \
                                                                 "toolbar, please increase width in config.json"
            self.__save_box = Save((last_left_position, 0), tuple(self._config["auth_box_size"]))
            last_left_position += self._config["mode_box_size"][0]
            self.__save_box.add(self.__screen)
        except AssertionError as e:
            print(e)
            pygame.quit()
            sys.exit()



        self.__modes = [Mode("point", (2 * self._config["mode_box_size"][0], 0), tuple(self._config["mode_box_size"])),
                        Mode("line", (3 * self._config["mode_box_size"][0], 0), tuple(self._config["mode_box_size"])),
                        Mode("text", (4 * self._config["mode_box_size"][0], 0), tuple(self._config["mode_box_size"])),
                        Mode("rect", (5 * self._config["mode_box_size"][0], 0), tuple(self._config["mode_box_size"])),
                        Mode("circle", (6 * self._config["mode_box_size"][0], 0), tuple(self._config["mode_box_size"]))
                        ]
        # If right and left boxes overlap, raise an error and close pygame
        try:
            for mod in self.__modes:
                assert last_left_position < last_right_position + 1, "Too many tools to fit in the Whiteboard " \
                                                                     "toolbar, please increase width in config.json"
                mod.add(self.__screen)
                last_left_position += self._config["mode_box_size"][0]
        except AssertionError as e:
            print(e)
            pygame.quit()
            sys.exit()

        """
        Choix des couleurs
        """
        self.__colors = []
        try:
            for key, value in self._config["color_palette"].items():
                assert last_left_position < last_right_position + 1, "Too many tools to fit in the Whiteboard " \
                                                                     "toolbar, please increase width in config.json"
                color_box = ColorBox(value, (last_right_position, 0), tuple(self._config["mode_box_size"]))
                last_right_position -= self._config["mode_box_size"][0]
                self.__colors.append(color_box)
                color_box.add(self.__screen)
        except AssertionError as e:
            print(e)
            pygame.quit()
            sys.exit()

        """
        Choix des épaisseurs
        """
        self.__font_sizes = []
        try:
            for size in self._config["pen_sizes"]:
                assert last_left_position < last_right_position + 1, "Too many tools to fit in the Whiteboard " \
                                                                     "toolbar, please increase width in config.json"
                font_size_box = FontSizeBox(size, (last_right_position, 0), tuple(self._config["mode_box_size"]))
                last_right_position -= self._config["mode_box_size"][0]
                self.__font_sizes.append(font_size_box)
                font_size_box.add(self.__screen)
        except AssertionError as e:
            print(e)
            pygame.quit()
            sys.exit()

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
        self._text_boxes = []  # Cette liste contiendra les objets de type Textbox

        self.active_box = None

        self.load_actions(self._hist)
        self.__modification_allowed = copy.deepcopy(self._hist["auth"])

        # if some client names are in this list, you will have the authorisation to edit their textboxes

        for action in self._hist["actions"]:
            if action["type"] == "Text_box":
                self.append_text_box(TextBox(**action["params"]))


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
    def name(self):
        return self._name

    @property
    def modification_allowed(self):
        return self.__modification_allowed

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

    def del_text_box(self, textbox):
        self._text_boxes.remove(textbox)

    def draw(self, obj, timestamp):
        """
        Method to draw figures defined in figures.py. Also adds drawn objects to history.

        :param obj: class of figure to draw
        :param timestamp: timestamp at which the drawing happens
        :return: None
        """

        # Draw object on screen
        obj.draw(self.__screen)

        # Create dict containing object parameters and right timestamp to add to history
        hist_obj = {"type": obj.type, "timestamp": timestamp, "params": obj.fetch_params(), "client": self._name}

        # Special case if it's a Text_box object, we need to get the correct box id
        if hist_obj["type"] == "Text_box":
            hist_obj["id"] = obj.id_counter
            hist_obj["owner"] = self._name
        self.add_to_hist(hist_obj)

    def switch_config(self, event):
        """
        Switch between different modes

        :param event: Action by the user : a mouse click on either modes, colors or font sizes
        :return: None
        """
        if event == "quit":
            self.set_config(["mode"], "quit")

        # We go through each mode, color and font size to see if that mode should be triggered by the event
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
            if self.__auth_box.is_triggered(event):
                self._erasing_auth = not self._erasing_auth
                self.__auth_box.switch(self.__screen, self._erasing_auth, self.__modification_allowed, self._name)
                self._hist["auth"] = [self._name, self._erasing_auth]
            if self.__save_box.is_triggered(event):
                self.__save_box.save(self.__screen, self)
                print("a drawing has been saved in the root folder")

    def set_active_box(self, box, new=True):
        """
        A method specific to text boxes : select an existing box or one that has just been created to edit. This box is
        thus said to be "active"

        :param box: instance of the TextBox class
        :param new: boolean to specify if the box was just created or already existed
        :return:
        """

        # If the selected box is already the active one, do nothing
        if box == self.active_box:
            return

        # If there is a box that is active we must turn it into "inactive"
        if self.active_box is not None:

            # Change its color to the "inactive color"
            self.active_box.set_textbox_color(self.get_config(["text_box", "inactive_color"]))
            # Select the id of previous active box
            id_counter = self.active_box.id_counter
            # Find the previous active box and change its color in history
            for action in [x for x in self.get_hist('actions') if x['type'] == 'Text_box']:
                if action['id'] == id_counter:
                    action["params"]["text"] = self.active_box.get_textbox_text()
                    action['params']["box_color"] = self.get_config(["text_box", "inactive_color"])
            # Render it
            self.active_box.draw(self.__screen)

        # If selected box already exists on the whiteboard we must turn it into "active"
        if not new:
            id_counter = box.id_counter
            for action in [x for x in self.get_hist('actions') if x['type'] == 'Text_box']:
                if action['id'] == id_counter:
                    action['params']["box_color"] = self.get_config(["text_box", "active_color"])

        # Draw the newly activated box
        self.active_box = box
        self.active_box.draw(self.__screen)
        pygame.display.flip()

    def draw_action(self, action):
        """
        Draw the result of an action by the user on the whiteboard

        :param action: usually a mouse action by the user
        :return:
        """
        if action["type"] == "Point":
            draw_point(action["params"], self.__screen)
        if action["type"] == "Line":
            draw_line(action["params"], self.__screen)
        if action["type"] == "Text_box":
            draw_textbox(action["params"], self.__screen)
        if action["type"] == "rect":
            draw_rect(action["params"], self.__screen)
        if action["type"] == "circle":
            draw_circle(action["params"], self.__screen)

    def load_actions(self, hist):
        """
        Load actions from history

        :param hist: list of dict representing the history of actions in the whiteboard session
        :return:
        """

        # Sort actions chronologically
        sred = sorted(hist["actions"],
                      key=lambda value: value["timestamp"])

        # Go through each action and draw it
        for action in sred:
            self.draw_action(action)
        pygame.display.flip()

    def start(self, connexion_avec_serveur):
        """
        Start and run a whiteboard window

        :param connexion_avec_serveur: socket to connect with server (socket.socket)
        :return:
        """

        # Initialize timestamp
        last_timestamp_sent = 0

        while not self.is_done():

            # Browse all events done by user
            for event in pygame.event.get():
                # If user closes the window, quit the whiteboard
                if self.get_config(["mode"]) == "quit":
                    self.end()
                    break
                # Use specific handling method for current drawing mode
                self.__handler[self.get_config(["mode"])].handle_all(event)

            # msg_a_envoyer["message"] = "CARRY ON"
            # Send dict history to server
            if self._hist["auth"] != [self._name, self._erasing_auth]:
                self._hist["auth"] = []
            new_modifs = [modif for modif in self.get_hist()["actions"] if
                          (modif["timestamp"] > last_timestamp_sent and self._name == modif["client"])]
            message_a_envoyer = {"message": "", 'actions': new_modifs, "auth": self._hist["auth"]}
            connexion_avec_serveur.send(dict_to_binary(message_a_envoyer))

            self._hist["auth"] = []
            # Update last timestamp sent
            if new_modifs:
                last_timestamp_sent = max([modif["timestamp"] for modif in new_modifs])

            # Dict received from server
            try:
                new_hist = binary_to_dict(connexion_avec_serveur.recv(2 ** 24))
            except (ConnectionResetError, ConnectionAbortedError) as e:
                print("The server has been shut down, please reboot the server")
                self._done = True
                pass


            # Consider actions made by another client after new_last_timestamp
            new_actions = [action for action in new_hist["actions"] if action["client"] != self._name]
            for action in new_actions:
                # Here there are two cases, a new figure (point, line, rect, circle, new text box) is created or an
                # existing text box is modified. For this second case, we use the variable "matched" as indicator
                matched = False
                if action["type"] == "Text_box":
                    # Find the text box id
                    for textbox in [x for x in self._hist["actions"] if x["type"] == "Text_box"]:
                        if action["id"] == textbox["id"]:
                            # Modify it with the newly acquired parameters from server
                            textbox["params"]["text"], textbox["params"]["w"] = action["params"]["text"], \
                                                                                action["params"]["w"]
                            action_to_update_textbox = action
                            for element in self.get_text_boxes():
                                if element.id_counter == action["id"]:
                                    self.del_text_box(element)
                                    self.append_text_box(TextBox(**action_to_update_textbox["params"]))

                            # Draw the modified text box with updated parameters
                            self.clear_screen()
                            self.load_actions(self._hist)
                            matched = True
                # If we are in the first case, we add the new actions to history and draw them
                if not matched:
                    self.add_to_hist(action)
                    if action["type"] == "Text_box":
                        self.append_text_box(TextBox(**action["params"]))
                    self.draw_action(action)
            if self._name in new_hist["auth"]:
                new_hist["auth"].remove(self._name)
            if new_hist["auth"] != self.__modification_allowed:
                self.__modification_allowed = copy.deepcopy(new_hist["auth"])
            pygame.display.flip()

        # Once we are done, we quit pygame and send end message
        pygame.quit()
        print("Fermeture de la connexion")
        message_a_envoyer["message"] = "END"
        try:
            connexion_avec_serveur.send(dict_to_binary(message_a_envoyer))
        except ConnectionResetError:
            print("There is no message to send to the server")
        connexion_avec_serveur.close()

    def start_local(self):
        """
        Starts Whiteboard locally. Used to test stuff and debug.
        :return:
        """
        while not self.is_done():
            for event in pygame.event.get():
                if self.get_config(["mode"]) == "quit":
                    self.end()
                    break
                self.__handler[self.get_config(["mode"])].handle_all(event)
            pygame.display.flip()
        pygame.quit()
