import pygame
import random
import sys
import os
import math

pygame.init()
pygame.mixer.init()

# -----------------------------
# Screen
# -----------------------------
WIDTH, HEIGHT = 900, 350
FPS = 60

# -----------------------------
# Colors
# -----------------------------
RED = (209, 25, 13)
BLACK = (51, 51, 51)
WHITE = (255, 255, 255)
GRAY = (200, 200, 200)
SKY = (124, 199, 242)
NIGHT = (40, 40, 70)
YELLOW = (255, 220, 0)

# -----------------------------
# Ground
# -----------------------------
GROUND_Y = HEIGHT - 5

# -----------------------------
# Player Physics
# -----------------------------
GRAVITY = 0.7
JUMP_STRENGTH = -17

# -----------------------------
# Assets
# -----------------------------
SPRITE_PATH = os.path.join("assets", "hawk.png")

OBSTACLES = [
    os.path.join("assets", "building.png"),
    os.path.join("assets", "building2.png")
]

# -----------------------------
# Sounds
# -----------------------------
ding_sound = None
jump_sound = None
high_sound = None
explode_sound = None

try:
    ding_sound = pygame.mixer.Sound("ding.wav")
except:
    pass

try:
    jump_sound = pygame.mixer.Sound("jump.wav")
except:
    pass

try:
    high_sound = pygame.mixer.Sound("highscore.wav")
except:
    pass

try:
    explode_sound = pygame.mixer.Sound("explosion.wav")
except:
    pass


# =========================================================
# Background Buildings (fixed sizes)
# =========================================================
city_buildings = []

for i in range(18):
    bw = random.randint(35, 65)
    bh = random.randint(60, 170)
    bx = i * 70
    city_buildings.append([bx, bw, bh])


# =========================================================
# Player Class
# =========================================================
class Player:
    W, H = 80, 90

    def __init__(self):
        self.x = 100
        self.normal_h = self.H
        self.y = GROUND_Y - self.H
        self.vel_y = 0
        self.grounded = True
        self.sprite = None
        self.ducking = False

        if os.path.exists(SPRITE_PATH):
            img = pygame.image.load(SPRITE_PATH).convert_alpha()
            self.sprite = pygame.transform.scale(img, (self.W, self.H))

    def jump(self):
        if self.grounded and not self.ducking:
            self.vel_y = JUMP_STRENGTH
            self.grounded = False

            # note jump sound
            if jump_sound:
                jump_sound.play()

    def duck(self, state):
        self.ducking = state

        if self.grounded:
            if state:
                self.H = 55
            else:
                self.H = self.normal_h

            self.y = GROUND_Y - self.H

    def update(self):
        self.vel_y += GRAVITY
        self.y += self.vel_y

        if self.y >= GROUND_Y - self.H:
            self.y = GROUND_Y - self.H
            self.vel_y = 0
            self.grounded = True

    def draw(self, screen):
        if self.sprite:
            img = pygame.transform.scale(self.sprite, (self.W, self.H))
            screen.blit(img, (self.x, int(self.y)))
        else:
            pygame.draw.rect(screen, RED, (self.x, int(self.y), self.W, self.H))

    def get_rect(self):
        return pygame.Rect(self.x + 10, int(self.y) + 10, self.W - 20, self.H - 20)


# =========================================================
# Obstacles
# =========================================================
class Obstacle:
    def __init__(self):
        self.type = random.choice(["ground", "ground", "ground", "flying"])

        if self.type == "ground":
            self.IMG_W = random.choice([70, 100, 120])
            self.IMG_H = random.choice([80, 120, 140])
            self.x = WIDTH + random.randint(250, 500)
            self.y = GROUND_Y - self.IMG_H
            self.sprite = None

            path = random.choice(OBSTACLES)

            if os.path.exists(path):
                img = pygame.image.load(path).convert_alpha()
                self.sprite = pygame.transform.scale(img, (self.IMG_W, self.IMG_H))

        else:
            self.IMG_W = 65
            self.IMG_H = 40
            self.x = WIDTH + random.randint(250, 500)
            self.y = random.choice([160, 190, 220])

    def update(self, speed):
        self.x -= speed

    def draw(self, screen):
        if self.type == "ground":
            if self.sprite:
                screen.blit(self.sprite, (self.x, self.y))
            else:
                pygame.draw.rect(screen, BLACK, (self.x, self.y, self.IMG_W, self.IMG_H))
        else:
            pygame.draw.ellipse(screen, RED, (self.x, self.y, self.IMG_W, self.IMG_H))

    def get_rect(self):
        return pygame.Rect(self.x + 5, self.y + 5, self.IMG_W - 10, self.IMG_H - 10)

    def off_screen(self):
        return self.x + self.IMG_W < 0


# =========================================================
# Speed
# =========================================================
class SpeedIncrease:
    def __init__(self, start_speed=6, max_speed=20, increase_rate=0.002):
        self.speed = start_speed
        self.max_speed = max_speed
        self.increase_rate = increase_rate

    def update(self):
        if self.speed < self.max_speed:
            self.speed += self.increase_rate

        return self.speed


# =========================================================
# Collision
# =========================================================
class Collisions:
    def __init__(self):
        self.game_over = False

    def check_collision(self, player, obstacle):
        if player.get_rect().colliderect(obstacle.get_rect()):
            self.game_over = True

        return self.game_over


# =========================================================
# Score
# =========================================================
class ScoreSystem:
    def __init__(self):
        self.score = 0
        self.high_score = 0
        self.last_update = pygame.time.get_ticks()
        self.last_ding = 0
        self.stars = 0

    def update(self):
        current_time = pygame.time.get_ticks()

        if current_time - self.last_update >= 100:
            self.score += 1
            self.last_update = current_time

            if self.score % 100 == 0 and self.score != self.last_ding:
                self.last_ding = self.score

                if ding_sound:
                    ding_sound.play()

            self.stars = self.score // 1000

        # note high score sound
        if self.score > self.high_score:
            self.high_score = self.score

            if high_sound and self.score % 25 == 0:
                high_sound.play()

    def draw(self, screen):
        font = pygame.font.SysFont(None, 32)

        txt = font.render(f"{self.score:05d}", True, BLACK)
        hi = font.render(f"HI {self.high_score:05d}", True, BLACK)

        screen.blit(txt, (WIDTH - 130, 20))
        screen.blit(hi, (WIDTH - 270, 20))

        for i in range(self.stars):
            pygame.draw.circle(screen, YELLOW, (25 + i * 22, 25), 8)


# =========================================================
# Game State
# =========================================================
class GameState:
    START = 0
    PLAYING = 1
    GAME_OVER = 2

    def __init__(self):
        self.state = self.START
        self.title_font = pygame.font.SysFont(None, 64)
        self.small_font = pygame.font.SysFont(None, 32)

    def draw_start(self, screen):
        screen.fill(SKY)

        title = self.title_font.render("Montclair Jump", True, BLACK)
        prompt = self.small_font.render("Press SPACE to start", True, BLACK)

        screen.blit(title, (WIDTH//2 - title.get_width()//2, 120))
        screen.blit(prompt, (WIDTH//2 - prompt.get_width()//2, 200))

    def draw_game_over(self, screen, score, high):
        screen.fill(SKY)

        title = self.title_font.render("Game Over", True, BLACK)
        txt = self.small_font.render(f"Score: {score:05d}", True, BLACK)
        hi = self.small_font.render(f"High: {high:05d}", True, BLACK)
        prompt = self.small_font.render("Press SPACE to restart", True, BLACK)

        screen.blit(title, (WIDTH//2 - title.get_width()//2, 90))
        screen.blit(txt, (WIDTH//2 - txt.get_width()//2, 150))
        screen.blit(hi, (WIDTH//2 - hi.get_width()//2, 185))
        screen.blit(prompt, (WIDTH//2 - prompt.get_width()//2, 235))


# =========================================================
# Background
# =========================================================
def draw_city(screen, score):

    if score < 300:
        sky = SKY
    elif score < 700:
        sky = (200, 170, 120)
    else:
        sky = NIGHT

    screen.fill(sky)

    scroll_speed = 1 + (score // 250)

    for b in city_buildings:
        b[0] -= scroll_speed

        if b[0] + b[1] < 0:
            b[0] = WIDTH + random.randint(20, 120)

        x = b[0]
        w = b[1]
        h = b[2]
        y = GROUND_Y - h

        pygame.draw.rect(screen, GRAY, (x, y, w, h))


# =========================================================
# Main
# =========================================================
def main():
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Montclair Jump")
    clock = pygame.time.Clock()

    player = Player()
    obstacle = Obstacle()
    speed = 6

    speed_increase = SpeedIncrease(start_speed=speed)
    collision_check = Collisions()
    score_system = ScoreSystem()
    game_state = GameState()

    while True:
        clock.tick(FPS)

        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:

                if event.key == pygame.K_s:
                    player.duck(True)

                if event.key in (pygame.K_SPACE, pygame.K_UP):

                    if game_state.state == GameState.START:
                        game_state.state = GameState.PLAYING

                    elif game_state.state == GameState.GAME_OVER:
                        hi = score_system.high_score

                        player = Player()
                        obstacle = Obstacle()
                        speed = 6
                        speed_increase = SpeedIncrease(start_speed=speed)
                        collision_check = Collisions()
                        score_system = ScoreSystem()
                        score_system.high_score = hi

                        game_state.state = GameState.PLAYING

                    elif game_state.state == GameState.PLAYING:
                        player.jump()

            if event.type == pygame.KEYUP:
                if event.key == pygame.K_s:
                    player.duck(False)

        if game_state.state == GameState.PLAYING:

            speed = speed_increase.update()

            player.update()
            obstacle.update(speed)
            score_system.update()

            if collision_check.check_collision(player, obstacle):

                # note explosion sound
                if explode_sound:
                    explode_sound.play()

                game_state.state = GameState.GAME_OVER

            if obstacle.off_screen():
                obstacle = Obstacle()

        if game_state.state == GameState.START:
            game_state.draw_start(screen)

        elif game_state.state == GameState.PLAYING:
            draw_city(screen, score_system.score)

            pygame.draw.line(screen, BLACK, (0, GROUND_Y), (WIDTH, GROUND_Y), 2)

            obstacle.draw(screen)
            player.draw(screen)
            score_system.draw(screen)

        elif game_state.state == GameState.GAME_OVER:
            game_state.draw_game_over(
                screen,
                score_system.score,
                score_system.high_score
            )

        pygame.display.flip()


if __name__ == "__main__":
    main()