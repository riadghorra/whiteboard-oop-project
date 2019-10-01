import pygame
import pygame.draw
from figures import Point, Line
import json

with open('config.json') as json_file:
    start_config = json.load(json_file)


black = [0,0,0]
red = [255,0,0]
green = [0,255,0]
blue  = [0,0,255]

class WhiteBoard:
    def __init__(self):
        pygame.init()
        self.done = False
        self.config = start_config
        self.screen = pygame.display.set_mode([self.config["width"], self.config["length"]])
        self.screen.fill(self.config["board_background_color"])
        pygame.draw.line(self.screen, black, [0, 30], [self.config["width"], 30], 1)
        pygame.draw.line(self.screen, black, [30, 30], [30, 0], 1)
        pygame.draw.line(self.screen, black, [60, 30], [60, 0], 1)
        pygame.draw.line(self.screen, black, [90, 30], [90, 0], 1)
        self.draw = False
        self.last_pos = None
        self.mouse_position = (0, 0)
        
        """
        legendage des modes
        """
        self.font = pygame.font.Font(None,18)
        legendes = [{"text" : self.font.render("Point",True,[0,0,0]), "coords" : (0, 0)},
                   {"text" : self.font.render("Line",True,[0,0,0]), "coords" : (30, 0)},
                   {"text" : self.font.render("Text",True,[0,0,0]), "coords" : (60, 0)}]
        
        for legend in legendes:
            self.screen.blit(legend["text"], legend["coords"])
        
        """
        Choix des couleurs
        """
        self.color_boxes ={
        "red" : {"rect" : pygame.Rect((self.config["width"]-30, 0), (30, 30)), "color" :red},
        "green" : {"rect" : pygame.Rect((self.config["width"]-60, 0), (30, 30)), "color" : green},
        "blue" : {"rect" : pygame.Rect((self.config["width"]-90, 0), (30, 30)), "color" : blue},
        "black" : {"rect" : pygame.Rect((self.config["width"]-120, 0), (30, 30)), "color" : black}
        }
        for box in self.color_boxes.values():
            pygame.draw.rect(self.screen, box["color"], box["rect"])


        """
        Choix de l'épaisseur
        """

        self.width_boxes ={
        "large" : {"rect" : pygame.Rect((self.config["width"]-150, 0), (30, 30))},
        "medium" : {"rect" : pygame.Rect((self.config["width"]-180, 0), (30, 30))},
        "small" : {"rect" : pygame.Rect((self.config["width"]-210, 0), (30, 30))},
        }

        for box in self.width_boxes.values():
            pygame.draw.rect(self.screen,black, box["rect"], 1)

        self.width_circles={
        "large" : {"circle" : ((self.config["width"]-135, 15), 10)},
        "medium" : {"circle" : ((self.config["width"]-165, 15), 8)},
        "small" : {"circle" : ((self.config["width"]-195, 15), 5)}
        }

        for circle in self.width_circles.values():
            pygame.draw.circle(self.screen, black, circle["circle"][0],circle["circle"][1])


        pygame.display.flip()

    def switch_config(self, coord=None):
        if coord == "quit":
            self.config["mode"] = "quit"
        else:
            if 30 <= coord[0] and coord[0] <= 60:
                self.config["mode"] = "line"
            elif 60 <= coord[0] and coord[0] <= 90:
                self.config["mode"] = "text"
            elif coord[0] <=30 :
                self.config["mode"] = "point"
            elif self.config["width"]-60 <= coord[0] and coord[0] <= self.config["width"]-30:
                self.config["active_color"] = green
            elif self.config["width"]-90 <= coord[0] and coord[0] <= self.config["width"]-60:
                self.config["active_color"] = blue
            elif self.config["width"]-120 <= coord[0] and coord[0] <= self.config["width"]-90:
                self.config["active_color"] = black
            elif self.config["width"]-30 <= coord[0]:
                self.config["active_color"] = red
            else :
                pass
            
    def handle_event_point_mode(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            coord = event.dict['pos']
            if coord[1] <= 30:
                self.switch_config(coord)
            else:
                to_draw = Point()
                to_draw.draw(self.screen, coord, 
                             event.dict['button'],
                             self.config["active_color"],
                             self.config["point_radius"])
        if event.type == pygame.QUIT:
            self.done = True
            self.switch_config("quit")
    
    def handle_event_line_mode(self, event):
        if event.type == pygame.QUIT:
            self.done = True
            self.switch_config("quit")
        elif event.type == pygame.MOUSEMOTION:
            if (self.draw):
                self.mouse_position = pygame.mouse.get_pos()
                if self.last_pos is not None:
                    to_draw = Line()
                    to_draw.draw(self.screen,
                                 self.config["active_color"], 
                                 self.last_pos, 
                                 self.mouse_position,
                                 self.config["line_width"])
                self.last_pos = self.mouse_position
        elif event.type == pygame.MOUSEBUTTONUP:
            self.mouse_position = (0, 0)
            self.draw = False
            self.last_pos = None
        elif event.type == pygame.MOUSEBUTTONDOWN:
            coord = event.dict['pos']
            if coord[1] <= 30:
                self.switch_config(coord)
            else:
                self.draw = True
                
    def handle_event_text_mode(self, event):
        if event.type == pygame.QUIT:
            self.done = True
            self.switch_config("quit")
        if event.type == pygame.MOUSEBUTTONDOWN:
            coord = event.dict['pos']
            if coord[1] <= 30:
                self.switch_config(coord)
            else : 
                print("une textbox apparait la")
        
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
