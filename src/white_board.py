import pygame
import pygame.draw
from figures import Point, Line
import json

with open('config.json') as json_file:
    start_config = json.load(json_file)


class WhiteBoard:
    def __init__(self):
        pygame.init()
        self.done = False
        self.config = start_config
        self.screen = pygame.display.set_mode([self.config["width"], self.config["length"]])
        self.screen.fill(self.config["board_background_color"])
        pygame.draw.line(self.screen, self.config["line_color"], [0, 30], [self.config["length"], 30], 1)
        pygame.draw.line(self.screen, self.config["line_color"], [30, 30], [30, 0], 1)
        pygame.draw.line(self.screen, self.config["line_color"], [60, 30], [60, 0], 1)
        pygame.draw.line(self.screen, self.config["line_color"], [90, 30], [90, 0], 1)
        self.draw = False
        self.last_pos = None
        self.mouse_position = (0, 0)

    def switch_mode(self, coord=None):
        if coord == "quit":
            self.config["mode"] = "quit"
        else:
            if 30 <= coord[0] and coord[0] <= 60:
                self.config["mode"] = "point"
            if 60 <= coord[0] and coord[0] <= 90:
                self.config["mode"] = "text"
            if coord[0] <=30 :
                self.config["mode"] = "line"
            else :
                pass
            
    def handle_event_point_mode(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            coord = event.dict['pos']
            if coord[1] <= 30:
                self.switch_mode(coord)
            else:
                to_draw = Point()
                to_draw.draw(self.screen, coord, 
                             event.dict['button'],
                             self.config["point_color"],
                             self.config["point_radius"])
        if event.type == pygame.QUIT:
            self.done = True
            self.switch_mode("quit")
    
    def handle_event_line_mode(self, event):
        if event.type == pygame.QUIT:
            self.done = True
            self.switch_mode("quit")
        elif event.type == pygame.MOUSEMOTION:
            if (self.draw):
                self.mouse_position = pygame.mouse.get_pos()
                if self.last_pos is not None:
                    to_draw = Line()
                    to_draw.draw(self.screen,
                                 self.config["line_color"], 
                                 self.last_pos, 
                                 self.mouse_position)
                self.last_pos = self.mouse_position
        elif event.type == pygame.MOUSEBUTTONUP:
            self.mouse_position = (0, 0)
            self.draw = False
            self.last_pos = None
        elif event.type == pygame.MOUSEBUTTONDOWN:
            coord = event.dict['pos']
            if coord[1] <= 30:
                self.switch_mode(coord)
            else:
                self.draw = True
                
    def handle_event_text_mode(self, event):
        if event.type == pygame.QUIT:
            self.done = True
            self.switch_mode("quit")
        if event.type == pygame.MOUSEBUTTONDOWN:
            coord = event.dict['pos']
            if coord[1] <= 30:
                self.switch_mode(coord)
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
