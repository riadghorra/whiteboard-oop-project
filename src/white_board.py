import pygame
import pygame.draw
from figures import point
import json

with open('config.json') as json_file:
    config = json.load(json_file)


def main():
    pygame.init()
    screen = pygame.display.set_mode([config["width"], config["length"]])
    screen.fill(config["board_background_color"])
    done = False
    while done == False:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                done = True
            if event.type == pygame.MOUSEBUTTONDOWN:
                to_draw = point()
                to_draw.draw(screen, event.dict['pos'], event.dict['button'], config["point_color"],
                             config["point_radius"])
    pygame.quit()


if __name__ == '__main__':
    main()
