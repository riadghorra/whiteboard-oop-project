import pygame
import pygame.draw
from figures import Point, Line
from tools import mode, color_box
import json

with open('config.json') as json_file:
    start_config = json.load(json_file)


black = [0,0,0]
red = [255,0,0]
green = [0,255,0]
blue  = [0,0,255]
white = [255,255,255]

class WhiteBoard:
    def __init__(self):
        pygame.init()
        self.done = False
        self.config = start_config
        self.screen = pygame.display.set_mode([self.config["width"], self.config["length"]])
        self.screen.fill(self.config["board_background_color"])
        
        self.modes = [mode("point", (0,0), tuple(self.config["mode_box_size"])),
                      mode("line", (self.config["mode_box_size"][0],0), tuple(self.config["mode_box_size"])),
                      mode("text", (2*self.config["mode_box_size"][0],0), tuple(self.config["mode_box_size"]))
                      ]
        for mod in self.modes :
            mod.add(self.screen)
        
        """
        Choix des couleurs
        """
        self.colors = [color_box(red, (self.config["width"]-self.config["mode_box_size"][0], 0), tuple(self.config["mode_box_size"])),
                       color_box(green, (self.config["width"]-2*self.config["mode_box_size"][0], 0), tuple(self.config["mode_box_size"])),
                       color_box(blue, (self.config["width"]-3*self.config["mode_box_size"][0], 0), tuple(self.config["mode_box_size"])),
                       color_box(black, (self.config["width"]-4*self.config["mode_box_size"][0], 0), tuple(self.config["mode_box_size"]))                        
                       ]
        for color in self.colors:
            color.add(self.screen)
        
        """
        initialisation des variables de dessin
        """
        pygame.display.flip()
        self.draw = False
        self.last_pos = None
        self.mouse_position = (0, 0)
        
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
            
    def handle_event_point_mode(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            coord = event.dict['pos']
            if coord[1] <= 30:
                self.switch_config(event)
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


