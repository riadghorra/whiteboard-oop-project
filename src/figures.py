"""
Module contenant toutes les figures et opérations de base
"""

import pygame
import pygame.draw


def distance(v1, v2):
    """
    Calcule la distance euclidienne entre deux vecteurs
    """
    try:
        return ((v1[0] - v2[0]) ** 2 + (v1[1] - v2[1]) ** 2) ** 0.5
    except TypeError:
        return "Ce ne sont pas des vecteurs"


class Point:
    """
    Classe d'un point prêt à être tracé sur le tableau
    coord (list) : coordonées
    point_color (list) : couleur en RGB
    font_size (int) : epaisseur en pixels
    toolbar_size (int) : epaisseur de la toolbar en haut du tableau sur laquelle on ne veut pas que le point depasse
    """

    def __init__(self, coord, point_color, font_size, toolbar_size=0):
        self.point_color = point_color
        self.font_size = font_size

        # used to not write on the toolbar if the font size is big
        self.coord = [coord[0], max(coord[1], toolbar_size + font_size + 1)]
        self.type = "Point"

    def draw(self, screen):
        """
        Dessine le point sur l'ecran
        """
        pygame.draw.circle(screen, self.point_color, self.coord, self.font_size)
        pygame.display.flip()
        return

    def fetch_params(self):
        """
        Retourne un dictionnaire des parametres
        """
        return {"coord": self.coord, "point_color": self.point_color, "font_size": self.font_size}


class Line:
    """
    Classe d'une ligne droite
    line_color (list) : couleur de la ligne en RGB
    start_pos (list): coordonee du debut de la ligne droite
    end_pos (list) : coordonee de la fin de la ligne droite
    font_size (int): epaisseur
    """

    def __init__(self, line_color, start_pos, end_pos, font_size):
        self.line_color = line_color
        self.start_pos = start_pos
        self.end_pos = end_pos
        self.font_size = font_size
        self.type = "Line"

    def draw(self, screen):
        """
        Dessine la ligne sur l'ecran
        """
        pygame.draw.line(screen, self.line_color, self.start_pos, self.end_pos, self.font_size)
        return

    def fetch_params(self):
        """
        Retourne un dictionnaire des parametres
        """
        return {"line_color": self.line_color, "start_pos": self.start_pos, "end_pos": self.end_pos,
                "font_size": self.font_size}


class Rectangle:
    """
    Classe d un rectangle
    color (list) : couleur du rectangle
    left, right (int) : coordonees d'absice a gauche, droite du rectangle
    bottom, top (int) : coordonees d'ordonnee en haut et en bas du rectangle
    """

    def __init__(self, c1, c2, color):
        """
        On definit les parametres du rectangle a partir des coordonees de deux coins
        c1, c2 (lists): coordonees de deux coins du rectangle
        """
        self.c1 = c1
        self.c2 = c2
        self.color = color
        # on recupere left avec le min des abscisses et on fait pareil pour right top et bottom
        self.left = min(c1[0], c2[0])
        self.top = min(c1[1], c2[1])
        self.right = max(c1[0], c2[0])
        self.bottom = max(c1[1], c2[1])
        self.width = self.right - self.left
        self.length = self.bottom - self.top
        self.rect = pygame.Rect(self.left, self.top, self.width, self.length)
        self.type = "rect"

    def draw(self, screen):
        """
        Dessine le rectangle sur l'ecran
        """
        pygame.draw.rect(screen, self.color, self.rect, 0)

    def fetch_params(self):
        """
        Retourne un dictionnaire des parametres
        """
        return {"c1": self.c1, "c2": self.c2, "color": self.color}


class Circle:
    """
    Classe d un cercle
    center (list) : les coordonees du centre
    extremity (list) : les coordonees d'une extremite
    color (list) : couleur
    toolbar_size (int) : la taille de la toolbar en pixel pour ne pas dessiner dessus
    radius (int) : rayon
    """

    def __init__(self, center, extremity, color, toolbar_size=0):
        self.center = center
        # on ne veut pas depasser sur la toolbar donc on reduit le rayon
        self.radius = min(int(distance(center, extremity)), center[1] - toolbar_size - 1)
        self.extremity = [center[0] + self.radius, center[1]]
        self.color = color
        self.type = "circle"

    def draw(self, screen):
        """
        dessine le cercle sur l ecran
        """
        pygame.draw.circle(screen, self.color, self.center, self.radius)

    def fetch_params(self):
        """
        Retourne un dictionnaire des parametres
        """
        return {"center": self.center, "extremity": self.extremity, "color": self.color}


class TextBox:
    """
    Classe d une textbox
    x, y (int) : l'abscisse a gauche et l'ordonee a droite de la textbox ie (x,y) est le topleft
    w (int) : longueur de la textbox
    h (int) : hauteur de la textbox
    box_color (list) : couleur du contour de la box
    font (string) : police du texte
    font_size (int) : taille des caracteres
    text (string) : texte de la texbox
    text_color (list) : couleur du texte
    """

    def __init__(self, x, y, w, h, box_color, font, font_size, text, text_color):
        self.__rect = pygame.Rect(x, y, w, h)
        self._color = box_color
        self._text = text
        self._font = font
        self._font_size = font_size
        self._sysfont = pygame.font.SysFont(font, font_size)
        self._text_color = text_color
        self._txt_surface = self._sysfont.render(text, True, self._text_color)
        self.id_counter = str(x) + "_" + str(y)
        self.type = "Text_box"

    """
    Encapsulation
    """

    def fetch_params(self):
        """
        Retourne un dictionnaire des parametres
        """
        return {"x": self.__rect.x, "y": self.__rect.y, "w": self.__rect.w, "h": self.__rect.h,
                "box_color": self._color, "font": self._font, "font_size": self._font_size, "text": self._text,
                "text_color": self._text_color}

    def get_textbox_color(self):
        return self._color

    def set_textbox_color(self, new_color):
        self._color = new_color

    def get_textbox_text(self):
        return self._text

    def add_character_to_text(self, char):
        """
        rajoute un caractere au texte
        """
        self._text += char

    def delete_char_from_text(self):
        """
        efface le dernier caractere du texte
        """
        self._text = self._text[:-1]

    def render_font(self, text, color, antialias=True):
        """
        effectue le rendu du texte
        """
        return self._sysfont.render(text, antialias, color)

    def set_txt_surface(self, value):
        self._txt_surface = value

    @property
    def rect(self):
        return self.__rect

    def update(self):
        """
        Change la taille du rectangle de contour si le texte est trop long
        """
        width = max(140, self._txt_surface.get_width() + 20)
        self.__rect.w = width
        return width

    def draw(self, screen):
        """
        dessine la textbox
        """
        # Blit le texte
        screen.blit(self._txt_surface, (self.__rect.x + 5, self.__rect.y + 5))
        # Blit le rectangle
        pygame.draw.rect(screen, self._color, self.__rect, 2)


# =============================================================================
# fonction de dessins instantanees
# =============================================================================

def draw_point(params, screen):
    """
    dessine un point sur l'ecran avec les parametres d entree
    params (dict) : dictionnaires des parametres
    screen (pygame screen) : ecran sur lequel dessiner
    """
    try:
        return Point(**params).draw(screen)
    except TypeError:
        return "Parametres incorrect"


def draw_line(params, screen):
    """
    dessine une ligne sur l'ecran avec les parametres d entree
    params (dict) : dictionnaires des parametres
    screen (pygame screen) : ecran sur lequel dessiner
    """
    try:
        return Line(**params).draw(screen)
    except TypeError:
        return "Parametres incorrect"


def draw_textbox(params, screen):
    """
    dessine une textbox sur l'ecran avec les parametres d entree
    params (dict) : dictionnaires des parametres
    screen (pygame screen) : ecran sur lequel dessiner
    """
    try:
        return TextBox(**params).draw(screen)
    except TypeError:
        return "Parametres incorrect"


def draw_rect(params, screen):
    """
    dessine un rectangle sur l'ecran avec les parametres d entree
    params (dict) : dictionnaires des parametres
    screen (pygame screen) : ecran sur lequel dessiner
    """
    try:
        return Rectangle(**params).draw(screen)
    except TypeError:
        return "Parametres incorrect"


def draw_circle(params, screen):
    """
    dessine un cercle sur l'ecran avec les parametres d entree
    params (dict) : dictionnaires des parametres
    screen (pygame screen) : ecran sur lequel dessiner
    """
    try:
        return Circle(**params).draw(screen)
    except TypeError:
        return "Parametres incorrect"
