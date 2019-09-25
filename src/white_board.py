import pygame
import pygame.draw
from figures import point
import json

with open('config.json') as json_file:
    config = json.load(json_file)


class white_board():
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode([config["width"], config["length"]])
        self.screen.fill(config["board_background_color"])
        self.done = False

    def start(self):
        while self.done == False:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.done = True
                if event.type == pygame.MOUSEBUTTONDOWN:
                    to_draw = point()
                    to_draw.draw(self.screen, event.dict['pos'], event.dict['button'], config["point_color"],
                                 config["point_radius"])
        pygame.quit()


