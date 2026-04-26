import pygame
import random
import sys
import os


pygame.init()


# Screen
WIDTH, HEIGHT = 900, 350
FPS = 60


# Colors
RED   = (209, 25, 13)
BLACK = ( 51, 51, 51)
WHITE = (255, 255, 255)
GRAY  = (200, 200, 200)
SKY   = (124, 199, 242) # light blue sky color


# Ground
GROUND_Y = HEIGHT + -5


# Player
GRAVITY = 0.8
JUMP_STRENGTH = -15


# Hawk Image
SPRITE_PATH = os.path.join("assets", "hawk.png")

# Building Image
BUILDING_PATH = os.path.join("assets", "building.png")


# Player Class ( jumping and stuff )
class Player:
    W, H = 80, 90  # player hitbox

    def __init__(self):
        self.x        = 100
        self.y        = GROUND_Y - self.H
        self.vel_y    = 0                  # y velocity
        self.grounded = True
        self.sprite   = None

        if os.path.exists(SPRITE_PATH):
            img = pygame.image.load(SPRITE_PATH).convert_alpha()
            self.sprite = pygame.transform.scale(img, (self.W, self.H))

    def jump(self):
        # player jumps only if they are on the ground
        if self.grounded:
            self.vel_y    = JUMP_STRENGTH
            self.grounded = False

    # gravity
    def update(self):
        self.vel_y += GRAVITY
        self.y     += self.vel_y
        if self.y >= GROUND_Y - self.H:   # stopping gravity when at ground
            self.y        = GROUND_Y - self.H
            self.vel_y    = 0
            self.grounded = True

    def draw(self, screen):
        if self.sprite:
            screen.blit(self.sprite, (self.x, int(self.y)))
        else:
            pygame.draw.rect(screen, RED, (self.x, int(self.y), self.W, self.H))

    def get_rect(self):
        return pygame.Rect(self.x + 10, int(self.y) + 10, self.W - 20, self.H - 20)


class Obstacle:  # obstacle class
    IMG_W, IMG_H = 70, 140  # building size

    def __init__(self):
        self.x = WIDTH + random.randint(200, 500)
        self.y = HEIGHT - self.IMG_H + 35  # pinned to bottom 
        self.sprite = None

        if os.path.exists(BUILDING_PATH):
            img = pygame.image.load(BUILDING_PATH).convert_alpha()
            self.sprite = pygame.transform.scale(img, (self.IMG_W, self.IMG_H))

    def update(self, speed):
        self.x -= speed

    def draw(self, screen):
        if self.sprite:
            screen.blit(self.sprite, (self.x, self.y))
        else:
            pygame.draw.rect(screen, BLACK, (self.x, self.y, self.IMG_W, self.IMG_H))

    def get_rect(self):
        return pygame.Rect(self.x + 5, self.y, self.IMG_W - 10, GROUND_Y - self.y)

    def off_screen(self):
        return self.x + self.IMG_W < 0


#main game loop
def main():
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Montclair Jump")
    clock  = pygame.time.Clock()

    player   = Player()
    obstacle = Obstacle()
    speed    = 6

    while True:
        clock.tick(FPS)

        for event in pygame.event.get(): # keypress events
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit() # quit
            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_SPACE, pygame.K_UP): # jump on space or up arrow
                    player.jump()

        player.update()
        obstacle.update(speed)

        if obstacle.off_screen(): # for now, one obstacle spawns, then when it hits the wall it respawns, will add more later
            obstacle = Obstacle()

        # Draw
        screen.fill(SKY)
        pygame.draw.line(screen, BLACK, (0, GROUND_Y), (WIDTH, GROUND_Y), 2)
        pygame.draw.rect(screen, SKY, (0, GROUND_Y, WIDTH, HEIGHT - GROUND_Y))
        obstacle.draw(screen)
        player.draw(screen)
        pygame.display.flip()
        


if __name__ == "__main__":
    main()