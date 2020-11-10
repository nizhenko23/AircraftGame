import pygame, sys, time
from pygame.locals import *
import random
import math

# --- constants ---

#Colors
colorRed = pygame.Color(241,59,62)
colorPurple = pygame.Color(200,254,249)
colorBlue = pygame.Color(52, 207, 235)
colorGreen = pygame.Color(100,182,100)
colorWhite = pygame.Color(255,250,250)
colorBlack = pygame.Color(0,0,0)
colorOrange = pygame.Color(242,164,0)
colorBrown = pygame.Color(148,103,58)
colorBlue2 = pygame.Color(37, 45, 204)

#Dimensions
w = 800
h = 600

# --- classes ---

class Player():

    def __init__(self, x, y, R, color, k_left, k_right, k_up, k_down):

        self.x_start = x
        self.y_start = y
        self.R = R
        self.color = color
        self.x_wins = 0

        self.k_left = k_left
        self.k_right = k_right
        self.k_up = k_up
        self.k_down = k_down

        self.reset()

    def reset(self):
        '''set values on restart'''
        self.x = self.x_start
        self.y = self.y_start
        self.x_dir = 0
        self.y_dir = 0

    def draw(self, screen):
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.R)

    def move(self):
        self.x += self.x_dir
        self.y += self.y_dir

    def handle_events(self):
        keys = pygame.key.get_pressed()

        if keys[self.k_right] or keys[self.k_left]:
            self.x_dir += 0.1 if keys[self.k_right] else -0.1
        else:
            self.x_dir *= 0.98

        if keys[self.k_up] or keys[self.k_down]:
            self.y_dir += 0.1 if keys[self.k_down] else -0.1
        else:
            self.y_dir *= 0.98

class Bot():

    def __init__(self, x, y, R, color):

        self.x_start = x
        self.y_start = y
        self.R = R
        self.color = color
        self.x_wins = 0

        self.reset()

    def reset(self):
        self.x = self.x_start
        self.y = self.y_start
        self.x_dir = 0
        self.y_dir = 0

    def draw(self, screen):
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.R)

    def move(self):
        self.x += self.x_dir
        self.y += self.y_dir

    def handle_events(self):
        dx = random.randint(-1, 1)
        if dx == 0:
            self.x_dir *= 0.98
        else:
            self.x_dir += 0.1 if dx > 0 else -0.1

        dy = random.randint(-1, 1)
        if dy == 0:
            self.y_dir *= 0.98
        else:
            self.y_dir += 0.1 if dy > 0 else -0.1

class Score():

    def __init__(self, x, y, step):
        self.x = x
        self.y = y
        self.step = step
        self.circles = 3
        self.wins = 0

    def draw(self, screen):
        r1 = int(xR-5)
        r2 = int(xR-10)

        x = self.x
        y = self.y
        for i in range(self.circles):
            pygame.draw.circle(screen, colorOrange, (x, y), r1)
            pygame.draw.circle(screen, colorBlack, (x, y), r2)
            x += self.step

        x = self.x
        y = self.y
        for i in range(self.wins):
            pygame.draw.circle(screen, colorOrange, (x, y), r1)
            x += self.step

# --- functions ---

def detect_collision(p1, p2):
    v12 = pygame.math.Vector2(p1.x-p2.x, p1.y-p2.y)
    distance = v12.length()
    hit_dist = 2*xR
    if distance <= hit_dist:
        # vector beteween center points
        nv = v12.normalize()
        # movement direction and combined relative movement
        d1 = pygame.math.Vector2(p1.x_dir, p1.y_dir)
        d2 = pygame.math.Vector2(p2.x_dir, p2.y_dir)
        dd = d1 - d2
        if dd.length() > 0:
            # normalized movement and normal distances
            ddn = dd.normalize()
            dir_dist  = ddn.dot(v12)
            norm_dist = pygame.math.Vector2(-ddn[0], ddn[1]).dot(v12)
            # minimum distance along the line of relative movement
            min_dist = math.sqrt(hit_dist*hit_dist - norm_dist*norm_dist)
            if dir_dist < min_dist:
                # update postions of the players so that the distance is 2*xR
                d1l, d2l = d1.length(), d2.length()
                d1n = d1/d1l if d1l > 0 else d1
                d2n = d2/d2l if d2l > 0 else d2
                p1.x -= d1n.x * d1l / (d1l+d2l)
                p1.y -= d1n.y * d1l / (d1l+d2l)
                p2.x -= d2n.x * d2l / (d1l+d2l)
                p2.y -= d2n.y * d2l / (d1l+d2l)
                # recalculate vector beteween center points
                v12 = pygame.math.Vector2(p1.x-p2.x, p1.y-p2.y)
                nv = v12.normalize()

            # reflect movement vectors
            rd1 = d1.reflect(nv)
            rd2 = d2.reflect(nv)
            len1, len2 = rd1.length(), rd2.length()
            if len1 > 0:
                rd1 = rd1 * len2 / len1
                p1.x_dir, p1.y_dir = rd1.x, rd1.y
            else:
                p1.x_dir, p1.y_dir = -p2.x_dir, -p2.y_dir
            if len2 > 0:
                rd2 = rd2 * len1 / len2
                p2.x_dir, p2.y_dir = rd2.x, rd2.y
            else:
                p2.x_dir, p2.y_dir = -p1.x_dir, -p1.y_dir

def detect_border(player):
    distance = ((centerX-player.x)**2 + (centerY-player.y)**2)**0.5
    return distance > (stageR+30)

def game():
    players = []
    scores = []

    p1 = Player(int(centerX-(stageR*0.8)), centerY, int(stageR//10), colorRed, K_a, K_d, K_w, K_s)
    players.append(p1)
    #p2 = Player(int(centerX+(stageR*0.8)), centerY, int(stageR//10), colorGreen, K_LEFT, K_RIGHT, K_UP, K_DOWN)
    #players.append(p2)

    b = Bot(int(centerX+(stageR*0.8)), centerY, int(stageR//10), colorGreen)
    players.append(b)
    b = Bot(centerX, int(centerY+(stageR*0.8)), int(stageR//10), colorOrange)
    players.append(b)
    b = Bot(centerX, int(centerY-(stageR*0.8)), int(stageR//10), colorWhite)
    players.append(b)
    b = Bot(centerX, centerY, int(stageR//10), colorBrown)
    players.append(b)

    s1 = Score(50, 30, 50)
    s2 = Score(750, 30, -50)
    scores.append(s1)
    scores.append(s2)

    while True:
        for event in pygame.event.get():
            #Game Exit
            if event.type== QUIT:
                pygame.quit()
                sys.exit()

        # ~~~ COLLISION DETECTION ~~~

        for p1 in players:
            for p2 in players:
                if p1 != p2:
                    detect_collision(p1, p2)

        # ~~~ Borders ~~~

        for i, p in enumerate(players):
            if detect_border(p):
                time.sleep(3)

                for x in players:
                    x.reset()

                if i == 0:
                    scores[1].wins += 1
                else:
                    scores[0].wins += 1

                print(scores[0].wins, scores[1].wins)

        for s in scores:
            if s.wins >= 3:
                #game_end()
                return

        # ~~~ MOVEMENT ~~~

        for p in players:
            p.handle_events()

        for p in players:
            p.move()

        # --- draws --- (without events and moves)
        screen.fill(colorBlack)
        # stage
        pygame.draw.circle(screen, colorBlue, (centerX,centerY), stageR)
        # players
        for p in players:
            p.draw(screen)
        # scores
        for s in scores:
            s.draw(screen)
        # update
        pygame.display.update()
        fpsClock.tick(60)

# --- main ---

pygame.init()
screen = pygame.display.set_mode((w,h))
screen_rect = screen.get_rect()
centerX = screen_rect.centerx
centerY = screen_rect.centery
pygame.display.set_caption('Ice Fighters')
fpsClock = pygame.time.Clock()

stageR = 250
xR = int((stageR//10))

game()