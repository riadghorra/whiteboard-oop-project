"""
Module contenant les differents outils de gestion du tableau
"""
import pygame
import pygame.draw
from datetime import datetime
from figures import Point, Line, TextBox, Rectangle, Circle
import time


# =============================================================================
# classes de gestion des changements de parametres utilisateur
# =============================================================================

class TriggerBox:
    """
    Classe mere abstraite qui represente une zone carree de l'ecran sur laquelle on peut cliquer
    top_left (list) : coordonees du pixel en haut a gauche
    size (int) : taille en pixel du cote du carre
    """

    def __init__(self, top_left, size):
        self.rect = pygame.Rect(top_left, size)
        self.coords = top_left

    def is_triggered(self, event):
        """
        retourne le booleen : l'utilisateur clique sur la triggerbox
        event (pygame event) : clic de souris d un utilisateur
        """
        return self.rect.collidepoint(event.pos)

class Auth(TriggerBox):
    """
    Classe d'un bouton qui change l'autorisation de modification
    """
    def __init__(self, top_left, size):
        TriggerBox.__init__(self, top_left, size)
        self._size = size

    def add(self, screen):
        """
        Dessine la authbox
        """
        pygame.draw.rect(screen, [0, 0, 0], self.rect, 1)
        pygame.draw.circle(screen, [255, 0, 0], [int(self.coords[0]+self._size[0]/2), int(self.coords[1]+self._size[1]/2)], int(min(self._size[0], self._size[1]/3)))
        font = pygame.font.Font(None, 18)
        legend = {"text": font.render("auth", True, [0, 0, 0]), "coords": self.coords}
        screen.blit(legend["text"], legend["coords"])

    def switch(self, screen, erasing_auth, modification_allowed, name):
        if erasing_auth:
            pygame.draw.circle(screen, [0, 255, 0], [int(self.coords[0]+self._size[0]/2), int(self.coords[1]+self._size[1]/2)], int(min(self._size[0], self._size[1]/3)))
            print("{} gave his auth".format(name))

        else:
            pygame.draw.circle(screen, [255, 0, 0], [int(self.coords[0]+self._size[0]/2), int(self.coords[1]+self._size[1]/2)], int(min(self._size[0], self._size[1]/3)))
            print("{} removed his auth".format(name))
        return [name, erasing_auth]


class Mode(TriggerBox):
    """
    Classe d'un mode de dessin du tableau dans lequel on peut rentrer via la triggerbox dont il herite
    name (string) : nom du mode qui sera inscrit dans sa triggerbox sur l'ecran
    """

    def __init__(self, name, top_left, size):
        super(Mode, self).__init__(top_left, size)
        self.name = name

    def add(self, screen):
        """
        Dessine la triggerbox du mode et la rend active sur l'ecran
        """
        pygame.draw.rect(screen, [0, 0, 0], self.rect, 1)
        font = pygame.font.Font(None, 18)
        legend = {"text": font.render(self.name, True, [0, 0, 0]), "coords": self.coords}
        screen.blit(legend["text"], legend["coords"])


class ColorBox(TriggerBox):
    """
    Classe d'une triggerbox de choix de couleur sur l'ecran
    color (list) : color of the box
    """

    def __init__(self, color, top_left, size):
        super(ColorBox, self).__init__(top_left, size)
        self.color = color

    def add(self, screen):
        """
        Dessine la colorbox
        """
        pygame.draw.rect(screen, self.color, self.rect)


class FontSizeBox(TriggerBox):
    """
    Classe des triggerbox de choix de l'epaisseur du trait
    font_size (int) : epaisseur du trait en pixel
    """

    def __init__(self, font_size, top_left, size):
        super(FontSizeBox, self).__init__(top_left, size)
        self.font_size = font_size
        self.center = [top_left[0] + size[0] // 2,
                       top_left[1] + size[1] // 2]  # pour dessiner un cercle representant l epaisseur de selection

    def add(self, screen):
        """
        Dessine la fontsizebox
        """
        pygame.draw.rect(screen, [0, 0, 0], self.rect, 1)
        pygame.draw.circle(screen, [0, 0, 0], self.center, self.font_size)


# =============================================================================
# classes de gestion des evenements utilisateur
# =============================================================================

class EventHandler:
    """
    Classe mere des gestionnaires d'evenements utilisateur en fontcion des modes
    whiteboard : classe whiteboard sur laquelle notre handler va gerer les evenements utilisateur
    """

    def __init__(self, whiteboard):
        self.whiteboard = whiteboard

    def handle(self, event):
        """
        Ce test commun a tous les modes verifie si l'utilisateur quitte ou change de mode
        """
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
    """
    Classe du gestionnaire d'evenement en mode point
    """

    def __init__(self, whiteboard):
        EventHandler.__init__(self, whiteboard)

    def handle_all(self, event):
        """
        En mode point on s'interesse aux clics gauches de souris et on dessine un point
        """
        handled = self.handle(event)

        # commun a tous les handler qui verifie si on change de mode ou on quitte
        if handled:
            return
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.dict["button"] != 1:
                return
            coord = event.dict["pos"]
            to_draw = Point(coord,
                            self.whiteboard.get_config(["active_color"]),
                            self.whiteboard.get_config(["font_size"]), self.whiteboard.get_config(["toolbar_y"]))
            now = datetime.now()
            timestamp = datetime.timestamp(now)
            self.whiteboard.draw(to_draw, timestamp)


class HandleLine(EventHandler):
    """
    Classe du gestionnaire d'evenement en mode ligne
    """

    def __init__(self, whiteboard):
        EventHandler.__init__(self, whiteboard)

    def handle_mouse_motion(self):
        """
        Gere les mouvements de souris : l'utilisateur a le clic enfonce le rendu du trait est en direct
        """
        if self.whiteboard.is_drawing():
            self.whiteboard.mouse_position = pygame.mouse.get_pos()
            if self.whiteboard.mouse_position[1] <= self.whiteboard.get_config(["toolbar_y"]):
                self.whiteboard.pen_up()
            elif self.whiteboard.last_pos is not None:
                to_draw = Line(self.whiteboard.get_config(["active_color"]), self.whiteboard.last_pos,
                               self.whiteboard.mouse_position,
                               self.whiteboard.get_config(["font_size"]))
                now = datetime.now()
                timestamp = datetime.timestamp(now)
                self.whiteboard.draw(to_draw, timestamp)
            self.whiteboard.update_last_pos()

    def handle_mouse_button_up(self):
        """
        Gere la levee du doigt sur le clic : on effectue un pen up
        """
        self.whiteboard.mouse_position = (0, 0)
        self.whiteboard.pen_up()
        self.whiteboard.reset_last_pos()

    def handle_mouse_button_down(self):
        """
        Gere le clic de l'utilisateur : pen down
        """
        self.whiteboard.pen_down()

    def handle_all(self, event):
        """
        Gere tous les evenements avec la methode associe via un arbre de if
        """
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
    """
    Classe du gestionnaire d'evenement en mode textbox
    """

    def __init__(self, whiteboard):
        EventHandler.__init__(self, whiteboard)

    def box_selection(self, event):
        """
        Gere les clics utilisateur
        S'il s'agit d'un clic droit, on cree une nouvelle box
        S'il s'agit d'un clic gauche on regarde si cela selectionne une zone d une ancienne box qui deviendra la box
         active
        """
        if event.dict["button"] == 3:
            coord = event.dict['pos']
            text_box = TextBox(*coord, self.whiteboard.get_config(["text_box", "textbox_width"]),
                               self.whiteboard.get_config(["text_box", "textbox_length"]),
                               self.whiteboard.get_config(["text_box", "active_color"]),
                               self.whiteboard.get_config(["text_box", "font"]),
                               self.whiteboard.get_config(["text_box", "font_size"]), "",
                               self.whiteboard.get_config(["active_color"]))
            self.whiteboard.append_text_box(text_box)
            now = datetime.now()
            timestamp = datetime.timestamp(now)
            self.whiteboard.draw(text_box, timestamp)
            self.whiteboard.set_active_box(text_box)

        elif event.dict["button"] == 1:
            for box in self.whiteboard.get_text_boxes():
                if box.rect.collidepoint(event.pos):
                    self.whiteboard.set_active_box(box, new=False)


    def write_in_box(self, event):
        """
        Gere les entrees clavier de l'utilisateur
        Si une box est selectionnee cela modifie le texte en consequence
        """
        if self.whiteboard.active_box is not None:

            # on efface un caractere
            if event.key == pygame.K_BACKSPACE:
                self.whiteboard.active_box.delete_char_from_text(self.whiteboard)

                # pour modifier la box il est malheureusement necessaire de re-render tout le tableau
                self.whiteboard.clear_screen()
                self.whiteboard.load_actions(self.whiteboard.get_hist())
            elif event.key == pygame.K_TAB or event.key == pygame.K_RETURN:
                pass
            else:
                self.whiteboard.active_box.add_character_to_text(event.unicode, self.whiteboard)

                # on re-render tout aussi ici pour éviter de superposer des écritures
                self.whiteboard.clear_screen()
                self.whiteboard.load_actions(self.whiteboard.get_hist())

        if self.whiteboard.active_box is not None:
            # Re-render the text.
            self.whiteboard.active_box.set_txt_surface(self.whiteboard.active_box.render_font(
                self.whiteboard.active_box.get_textbox_text(),
                self.whiteboard.active_box.get_textbox_color()))

    def handle_all(self, event):
        """
        Gere tous les evenements avec la methode associée via un arbre de if
        """
        handled = self.handle(event)
        if handled:
            return
        if event.type == pygame.MOUSEBUTTONDOWN:
            self.box_selection(event)
        if event.type == pygame.KEYDOWN:
            self.write_in_box(event)
        pygame.display.flip()


class HandleRect(EventHandler):
    """
    Classe du gestionnaire d'evenement en mode rectangle
    Nous avons decidé de faire un systeme de clic drag pour tracer un rectangle
    """

    def __init__(self, whiteboard):
        EventHandler.__init__(self, whiteboard)
        self.c1 = None

    def handle_mouse_button_up(self, coord):
        """
        Recupere la deuxieme coordonee d'un coin du rectangle a tracer quand l'utilisateur arrete de cliquer
        """
        if self.c1 is not None:
            coord = list(coord)
            # on ne veut pas depasser sur la toolbar
            coord[1] = max(self.whiteboard.get_config(["toolbar_y"]), coord[1])
            to_draw = Rectangle(self.c1, coord, self.whiteboard.get_config(["active_color"]))
            now = datetime.now()
            timestamp = datetime.timestamp(now)
            self.whiteboard.draw(to_draw, timestamp)
            self.c1 = None

    def handle_mouse_button_down(self, event):
        """
        Recupere une coordonee d'un coin du rectangle a tracer quand l'utilisateur démarre un clic
        """
        if event.dict["button"] != 1:
            return
        self.c1 = event.dict['pos']

    def handle_all(self, event):
        """
        Gere tous les evenements avec la methode associe via un arbre de if
        """
        handled = self.handle(event)
        if handled:
            return
        elif event.type == pygame.MOUSEBUTTONUP:
            self.handle_mouse_button_up(coord=event.dict['pos'])
        elif event.type == pygame.MOUSEBUTTONDOWN:
            self.handle_mouse_button_down(event)
        pygame.display.flip()


class HandleCircle(EventHandler):
    """
    Classe du gestionnaire d'evenement en mode Cercle
    Nous avons decidé de faire un systeme de clic drag la-encore pour tracer un cercle
    """

    def __init__(self, whiteboard):
        EventHandler.__init__(self, whiteboard)
        self.center = None

    def handle_mouse_button_up(self, coord):
        """
        Recupere la coordonee d'un point sur le cercle quand l'utilisateur arrete de cliquer
        """
        if self.center is not None:
            coord = list(coord)
            to_draw = Circle(self.center, coord, self.whiteboard.get_config(["active_color"]),
                             self.whiteboard.get_config(["toolbar_y"]))
            now = datetime.now()
            timestamp = datetime.timestamp(now)
            self.whiteboard.draw(to_draw, timestamp)
            self.center = None

    def handle_mouse_button_down(self, event):
        """
        Recupere la coordonnee du centre du cercle quand l'utilisateur demarre un clic
        """
        if event.dict["button"] != 1:
            return
        self.center = event.dict['pos']

    def handle_all(self, event):
        """
        Gere tous les evenements avec la methode associe via un arbre de if
        """
        handled = self.handle(event)
        if handled:
            return
        elif event.type == pygame.MOUSEBUTTONUP:
            self.handle_mouse_button_up(coord=event.dict['pos'])
        elif event.type == pygame.MOUSEBUTTONDOWN:
            self.handle_mouse_button_down(event)
        pygame.display.flip()
