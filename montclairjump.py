import pygame
import random
import sys
import os


pygame.init()


# Screen
WIDTH, HEIGHT = 900, 350
FPS = 60


# Colors
RED = (209, 25, 13)
BLACK = ( 51, 51, 51)
WHITE = (255, 255, 255)
GRAY = (200, 200, 200)
SKY = (124, 199, 242) # light blue sky color


# Ground
GROUND_Y = HEIGHT + -5


# Player
GRAVITY = 0.8
JUMP_STRENGTH = -15


# Hawk Image
SPRITE_PATH = os.path.join("assets", "hawk.png")

# Building Image
OBSTACLES = [os.path.join("assets", "building.png"), os.path.join("assets", "building2.png")]
BUILDING_PATH = random.choice(OBSTACLES)


# Player Class ( jumping and stuff )
class Player:
    W, H = 80, 90  # player hitbox

    def __init__(self):
        self.x = 100
        self.y = GROUND_Y - self.H
        self.vel_y = 0 # y velocity
        self.grounded = True
        self.sprite = None

        if os.path.exists(SPRITE_PATH):
            img = pygame.image.load(SPRITE_PATH).convert_alpha()
            self.sprite = pygame.transform.scale(img, (self.W, self.H))

    def jump(self):
        # player jumps only if they are on the ground
        if self.grounded:
            self.vel_y = JUMP_STRENGTH
            self.grounded = False

    # gravity
    def update(self):
        self.vel_y += GRAVITY
        self.y += self.vel_y
        if self.y >= GROUND_Y - self.H:   # stopping gravity when at ground
            self.y = GROUND_Y - self.H
            self.vel_y = 0
            self.grounded = True

    def draw(self, screen):
        if self.sprite:
            screen.blit(self.sprite, (self.x, int(self.y)))
        else:
            pygame.draw.rect(screen, RED, (self.x, int(self.y), self.W, self.H))

    def get_rect(self):
        return pygame.Rect(self.x + 10, int(self.y) + 10, self.W - 20, self.H - 20)


class Obstacle:  # obstacle class
    IMG_W, IMG_H = 120, 140  # building size

    def __init__(self):
        self.x = WIDTH + random.randint(200, 500)
        self.y = HEIGHT - self.IMG_H + 35  # pinned to bottom 
        self.sprite = None
        BUILDING_PATH = random.choice(OBSTACLES)
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

    def get_rect(self): #I changed this to make the hitbox for the obstacles smaller
        return pygame.Rect(
            self.x + 30,        #move in from left
            self.y + 20,        #move down
            self.IMG_W - 50,    #reduce width
            self.IMG_H - 60     #reduce height
        )

    def off_screen(self):
        return self.x + self.IMG_W < 0
    

class SpeedIncrease: # increase speed class
    def __init__(self, start_speed=6, max_speed=20, increase_rate=0.002):
        self.speed = start_speed # current speed
        self.max_speed = max_speed # speed cap
        self.increase_rate = increase_rate #rate of increase

    def update(self): #increase speed each frame
        if self.speed < self.max_speed:
            self.speed += self.increase_rate
        return self.speed
    

class Collisions: #collisions end the game
    def __init__(self):
        self.game_over = False #check for collision

    def check_collision(self, player, obstacle):
        #get hitboxes
        player_rect = player.get_rect()
        obstacle_rect = obstacle.get_rect()

        if player_rect.colliderect(obstacle_rect):
            self.game_over = True

        return self.game_over
    

class ScoreSystem:
    def __init__(self):
        self.score = 0
        self.last_update = pygame.time.get_ticks()

    def update(self):
        current_time = pygame.time.get_ticks()

        if current_time - self.last_update >= 100: #10 points per second
            self.score +=1
            self.last_update = current_time

    def draw(self, screen):
        score_text = f"{self.score:05d}" #format so score is always 5 digits
        font = pygame.font.SysFont(None, 36)
        text_surface = font.render(score_text, True, BLACK)
        screen.blit(text_surface, (WIDTH - 120, 20))


class GameState:
    START = 0
    PLAYING = 1
    GAME_OVER = 2

    def __init__(self):
        self.state = GameState.START

        self.title_font = pygame.font.SysFont(None, 64)
        self.small_font = pygame.font.SysFont(None, 32)

    def draw_start(self, screen):
        screen.fill(SKY)

        title = self.title_font.render("Montclair Jump", True, BLACK)
        prompt = self.small_font.render("Press SPACE to start", True, BLACK)

        screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 120))
        screen.blit(prompt, (WIDTH // 2 - prompt.get_width() // 2, 200))

    def draw_game_over(self, screen, score):
        screen.fill(SKY)

        title = self.title_font.render("Game Over", True, BLACK)
        score_text = self.small_font.render(f"Score: {score:05d}", True, BLACK)
        prompt = self.small_font.render("Press SPACE to restart", True, BLACK)

        screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 100))
        screen.blit(score_text, (WIDTH // 2 - score_text.get_width() // 2, 170))
        screen.blit(prompt, (WIDTH // 2 - prompt.get_width() // 2, 230))


#main game loop
def main():
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Montclair Jump")
    clock  = pygame.time.Clock()

    player = Player()
    obstacle = Obstacle()
    speed = 6

    speed_increase = SpeedIncrease(start_speed=speed) #manage speed increase

    collision_check = Collisions()

    score_system = ScoreSystem()

    game_state = GameState()

    while True:
        clock.tick(FPS)

        for event in pygame.event.get(): # keypress events
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit() # quit
            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_SPACE, pygame.K_UP): # jump on space or up arrow
                    #Game start
                    if game_state.state == GameState.START:
                        game_state.state = GameState.PLAYING
                    #Game over and restart
                    elif game_state.state == GameState.GAME_OVER:
                        player = Player()
                        obstacle = Obstacle()
                        speed = 6
                        speed_increase = SpeedIncrease(start_speed=speed)
                        collision_check = Collisions()
                        score_system = ScoreSystem()

                        game_state.state = GameState.PLAYING

                    elif game_state.state == GameState.PLAYING:
                        player.jump()

        if game_state.state == GameState.PLAYING:
            speed = speed_increase.update()

            player.update()
            obstacle.update(speed)
            score_system.update()

            if collision_check.check_collision(player, obstacle):
                game_state.state = GameState.GAME_OVER
            
            if obstacle.off_screen(): # for now, one obstacle spawns, then when it hits the wall it respawns, will add more later
                obstacle = Obstacle()

        # Draw
        if game_state.state == GameState.START:
            game_state.draw_start(screen)

        elif game_state.state == GameState.PLAYING:
            screen.fill(SKY)
            pygame.draw.line(screen, BLACK, (0, GROUND_Y), (WIDTH, GROUND_Y), 2)
            pygame.draw.rect(screen, SKY, (0, GROUND_Y, WIDTH, HEIGHT - GROUND_Y))

            obstacle.draw(screen)
            player.draw(screen)
            score_system.draw(screen)

            pygame.draw.rect(screen, RED, player.get_rect(), 2)          # These are for debugging to see the hitboxes of the 
            pygame.draw.rect(screen, BLACK, obstacle.get_rect(), 2)      # obstacles and the player

        elif game_state.state == GameState.GAME_OVER:
            game_state.draw_game_over(screen, score_system.score)

        pygame.display.flip()
        


if __name__ == "__main__":
    main()