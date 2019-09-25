import pygame
import pygame.draw
from figures import point

def main():
    pygame.init()
    xx, yy = 400, 400
    size = [xx, yy]
    screen = pygame.display.set_mode(size)
    screen.fill((255, 255, 255))
    done = False
    while done == False:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                done = True
            if event.type == pygame.MOUSEBUTTONDOWN:
                to_draw = point()
                to_draw.draw(screen, event.dict['pos'], event.dict['button'])
    pygame.quit()

if __name__ == '__main__':
    main()
