import pygame

pygame.init()

debug_mode = True

screen = pygame.display.set_mode((600,336))

font = pygame.font.Font('Bernard-MT-Condensed-Regular.ttf', 15)

Character = pygame.image.load('Main-character.png')
Character = pygame.transform.scale(Character, (Character.get_width()*.5, Character.get_height()*.5))

Background = pygame.image.load('Background.png')
Background = pygame.transform.scale(Background, (Background.get_width()*8, Background.get_height()*4))

#Visible time in game
countdown_Time = 0 #Starting time
start_time = pygame.time.get_ticks()





platforms =[
pygame.Rect(0,300,600,36),
  pygame.Rect(200, 220, 120, 20),
  pygame.Rect(400, 160, 100, 20)]

clock = pygame.time.Clock()

running = True
on_ground = False
x = 0
y = 240
vy = 0
gravity = 0.3

while running:
    past_second = (pygame.time.get_ticks() + start_time) / 1000
    current_time = min(7000, countdown_Time + int(past_second))
    if current_time == 7000:
        running = False
    #Single key presses
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False


#Continuous movement press/press and hold
    keys = pygame.key.get_pressed()
    if keys[pygame.K_UP] and (on_ground == True):
        vy = -8
    if keys[pygame.K_DOWN]:
        y = y+1
    if keys[pygame.K_LEFT]:
        x = x-1
    if keys[pygame.K_RIGHT]:
        x = x+1

    on_ground = False

    vy = gravity + vy
    y = vy + y

    screen.fill((0,0,0))

#Spawn location
    Character_rect = Character.get_rect(topleft=(x,y))
# Collision dectecting
    for platform in platforms:
        if Character_rect.colliderect(platform):
            if vy > 0:
                y = platform.top - Character_rect.height
                vy = 0
                on_ground = True
            if vy < 0:
                y = platform.bottom
                vy = 0
            if x <  platform.left:
                x = platform.left - Character_rect.width
            if x >  platform.right:
                x = platform.right
    screen.blit(Background, (0,0))
    screen.blit(Character, (x, y))


#Ability to see the hitboxes
    if debug_mode == True:
        pygame.draw.rect(screen, (0, 255, 0), Character_rect, 2)
        for platform in platforms:
            pygame.draw.rect(screen, (0, 255, 0), platform, 2)


    clock.tick(60)



    time_text = f"Time: {current_time}"
    Clock_screen = font.render(time_text, True, (0, 0, 0))
    screen.blit(Clock_screen, (519, 20))

    pygame.display.flip()


pygame.quit()
