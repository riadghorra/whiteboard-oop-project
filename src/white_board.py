import pygame
import pygame.draw
from figures import Point
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
        pygame.draw.line(self.screen, self.config["line_color"], [0, 30], [30, 30], 1)
        pygame.draw.line(self.screen, self.config["line_color"], [30, 30], [30, 0], 1)

    def switch_mode(self):
        if self.config["mode"] == "point":
            self.config["mode"] = "line"
        else:
            self.config["mode"] = "point"

    def start(self):
        while not self.done:
            while self.config["mode"] == "point":
                for event in pygame.event.get():
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        coord = event.dict['pos']
                        if max(coord) <= 30:
                            self.switch_mode()
                        else:
                            to_draw = Point()
                            to_draw.draw(self.screen, coord, event.dict['button'], self.config["point_color"],
                                         self.config["point_radius"])
                    if event.type == pygame.QUIT:
                        self.done = True
                        self.switch_mode()
            draw = False
            last_pos = None
            mouse_position = (0, 0)
            while self.config["mode"] == "line":
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        self.done = True
                        self.switch_mode()
                    elif event.type == pygame.MOUSEMOTION:
                        if (draw):
                            mouse_position = pygame.mouse.get_pos()
                            if last_pos is not None:
                                pygame.draw.line(self.screen, self.config["line_color"], last_pos, mouse_position, 1)
                            last_pos = mouse_position
                    elif event.type == pygame.MOUSEBUTTONUP:
                        mouse_position = (0, 0)
                        draw = False
                        last_pos = None
                    elif event.type == pygame.MOUSEBUTTONDOWN:
                        coord = event.dict['pos']
                        if max(coord) <= 30:
                            self.switch_mode()
                        else:
                            draw = True
                pygame.display.update()
        pygame.quit()
