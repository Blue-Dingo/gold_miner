#########################################################
# ## import

import pygame
import os
import math
from pygame import Surface, surface
#########################################################
# ## funcs & class

class Claw(pygame.sprite.Sprite):
    def __init__(self, image, position) -> None:
        super().__init__()
        self.image = image
        self.rect = image.get_rect(center=position)
        self.origin = position # 집게의 원점 좌표 저장
        self.image0 = image # 회전되기 전의 이미지 저장
        self.offset_x0 = 50
        self.offset = pygame.math.Vector2(self.offset_x0, 0)
        self.set_init()

    def draw(self, screen):
        pygame.draw.circle(screen, RED, self.origin, 2)
        screen.blit(self.image, self.rect)

    def draw_wire(self, screen):
        pygame.draw.line(screen, BLACK, self.origin, self.rect.center, 5)

    def rotate(self):
        self.image = pygame.transform.rotate(self.image0, -self.angle)

    def set_init(self):
        self.angle = 10
        self.direction = CLOCKWISE
        self.offset.x = self.offset_x0
        self.winding = False
        self.to_x = 0

    def update(self):
        self.offset.x += self.to_x
        rotated_offset = self.offset.rotate(self.angle)
        self.rect = self.image.get_rect(center=self.origin + rotated_offset)

class GemStone(pygame.sprite.Sprite):
    def __init__(self, image, position, speed, score) -> None:
        super().__init__()
        self.image = image
        self.rect = image.get_rect(center=position)
        self.speed = speed
        self.score = score

def group_add(typeIndex, position):
    gemstone_group.add(GemStone(gemstone_images[typeIndex], position, gemstone_speeds[typeIndex], gemstone_score[typeIndex]))

def setup_gemstone():
    group_add(1, (300,500))
    group_add(1, (800,400))
    group_add(0, (200,380))
    group_add(0, (500,200))
    group_add(0, (600,300))
    group_add(2, (700,250))
    group_add(3, (900,600))
    # gemstone_group.add(GemStone(gemstone_images[0], (200,380), gemstone_speeds[0], gemstone_score[0]))
    # gemstone_group.add(GemStone(gemstone_images[1], (300,500), gemstone_speeds[1], gemstone_score[1]))
    # gemstone_group.add(GemStone(gemstone_images[2], (300,380), gemstone_speeds[2], gemstone_score[2]))
    # gemstone_group.add(GemStone(gemstone_images[3], (900,420), gemstone_speeds[3], gemstone_score[3]))

def check_collide():
    global caught_gemstone
    for gemstone in gemstone_group:
        # if claw.rect.colliderect(gemstone.rect):
        if pygame.sprite.collide_mask(claw, gemstone):
            caught_gemstone = gemstone
            claw.to_x = -gemstone.speed
            claw.winding = True
            break

def drag_gemstone():
    rad = math.radians(claw.angle)
    r = caught_gemstone.rect.size[0]/2
    x, y = r*math.cos(rad), r*math.sin(rad)
    x_claw, y_claw = claw.rect.center[0], claw.rect.center[1]
    caught_gemstone.rect = caught_gemstone.image.get_rect(center=(x_claw+x,y_claw+y))

def drop_gemstone():
    global caught_gemstone, curr_score

    curr_score += caught_gemstone.score     
    gemstone_group.remove(caught_gemstone)
    caught_gemstone = None


#########################################################
# ## pygame 초기화

pygame.init()

screen_w, screen_h = 1280, 720
screen = pygame.display.set_mode((screen_w,screen_h))
pygame.display.set_caption("Gold Miner")

clock = pygame.time.Clock()

#########################################################
# ## 변수들

RED = (255,0,0)
BLACK = (0,0,0)

# 집게 방향
CLOCKWISE = 1
COUNTER_CLOCKWISE = -1
STOP = 0

current_path = os.path.dirname(__file__)

# 점수 시간
game_font = pygame.font.SysFont("arialrounded", 20)
game_font_big = pygame.font.SysFont("arialrounded", 50)
game_font_big.set_bold(True)
start_time = pygame.time.get_ticks()
total_time = 30
goal_score = 1000
curr_score = 0

# 배경
background = pygame.image.load(os.path.join(current_path, "background.png"))

# 보석변수
gemstone_images = [
        pygame.image.load(os.path.join(current_path, "small_gold.png")).convert_alpha(),
        pygame.image.load(os.path.join(current_path, "big_gold.png")).convert_alpha(),
        pygame.image.load(os.path.join(current_path, "stone.png")).convert_alpha(),
        pygame.image.load(os.path.join(current_path, "diamond.png")).convert_alpha()]
gemstone_speeds = [5,2,2,7]
gemstone_score = [100,500,10,800]

gemstone_group = pygame.sprite.Group()
setup_gemstone()
caught_gemstone = None


# 집게 변수
claw_image = pygame.image.load(os.path.join(current_path, "claw.png"))
claw = Claw(claw_image, (screen_w/2, 100))

angle_speed = 2.5
launch_speed = 10
return_speed = 20

#########################################################
# ## game loop

running = True
while running:
    clock.tick(30)
    elapsed = pygame.time.get_ticks() - start_time
    time_left = total_time-elapsed//1000

    if time_left <=0: 
        running = False
        result = "Game Over"
    
    if curr_score >= goal_score :
        running = False
        result = "Mission Complete"

    goal_score_text = game_font.render(f"Goal Score : {goal_score:,}", True, BLACK)
    curr_score_text = game_font.render(f"Current Score : {curr_score:,}", True, BLACK)
    timer_text = game_font.render(f"Timer : {time_left}", True, BLACK)


    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        
        if event.type == pygame.MOUSEBUTTONDOWN:
            claw.direction = STOP

    if claw.direction == CLOCKWISE:
        claw.angle += angle_speed
    elif claw.direction == COUNTER_CLOCKWISE:
        claw.angle -= angle_speed
    else:
        if not claw.winding:
            claw.to_x = launch_speed
            # 충돌처리
            if not caught_gemstone:
                check_collide()

        # 경계처리
        claw_x = claw.rect.center[0]
        claw_y = claw.rect.center[1]
        if not(0<claw_x<screen_w) or claw_y>screen_h :
            claw.to_x = -return_speed
            claw.winding = True

        # 되감기중
        if claw.winding:
            # 끌고오기
            if caught_gemstone:
                drag_gemstone()
            # 원점체크
            if claw.offset.x <= claw.offset_x0:
                claw.set_init()
                # 채광성공
                if caught_gemstone:
                    drop_gemstone()
               
    # 집게 회전
    if claw.direction != STOP:
        if claw.angle <= 10 :
            claw.angle = 10
            claw.direction = CLOCKWISE
        elif claw.angle >= 170 :
            claw.angle = 170
            claw.direction = COUNTER_CLOCKWISE
        claw.rotate()
    
    claw.update() # claw.rect 업데이트

    screen.blit(background, background.get_rect())
    gemstone_group.draw(screen)
    claw.draw(screen)
    claw.draw_wire(screen)

    screen.blit(timer_text, timer_text.get_rect(right=screen_w-20,top=20))
    screen.blit(goal_score_text, (20,20))
    screen.blit(curr_score_text, (20,60))

    pygame.display.update()

result_text = game_font_big.render(result, True, BLACK)
screen.blit(result_text, result_text.get_rect(center=screen.get_rect().center))
pygame.display.update()
pygame.time.delay(2000)
pygame.quit()
