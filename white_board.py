import pygame
import sys

pygame.init()

screen = pygame.display.set_mode((640, 480))
pygame.display.set_caption("First Pygame Application")

clock = pygame.time.Clock()
while True:
    clock.tick(50)

    # Process events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            sys.exit()

    # Clear the screen
    screen.fill((255, 255, 255))

    # Check input
    # Move objects ...
    # Draw objects ...

    # Update the screen
    pygame.display.flip()