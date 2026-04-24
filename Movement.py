import pygame

pygame.init()

debug_mode = True

screen = pygame.display.set_mode((600,336))

Character = pygame.image.load('Main-character.png')
Character = pygame.transform.scale(Character, (Character.get_width()*.2, Character.get_height()*.2))

#backg = pygame.image.load('background.png')
Background = pygame.transform.scale(backg, (backg.get_width()*2, backg.get_height()*2))


platforms = [
    pygame.Rect(0,300,600,36),
    pygame.Rect(200, 220, 120, 20),
    pygame.Rect(400, 160, 100, 20)
]

clock = pygame.time.Clock()

while running:
    screen.fill((0,0,0))
    screen.blit(Background,(0,0))

    player_rect = pygame.Rect(x , y, 30,30)

    barier1_rect = pygame.Rect( 300 , 45, 30,30)
    barier2_rect = pygame.Rect(250 , 450, 60,50)
    barier3_rect = pygame.Rect(600 , 50, 60,40)

    pygame.draw.rect(screen, (255, 0, 0),barier1_rect, 2)
    pygame.draw.rect(screen, (255, 0, 0),barier2_rect, 2)
    pygame.draw.rect(screen, (255, 0, 0),barier3_rect, 2)

    pygame.draw.rect(screen, (0,255,0),player_rect, 2)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    keys = pygame.key.get_pressed()
    if keys[pygame.K_UP]:
        y = y-2
    if keys[pygame.K_DOWN]:
        y = y + 2
    if keys[pygame.K_LEFT]:
        x = x - 2
    if keys[pygame.K_RIGHT]:
        x = x + 2

        if player_rect.colliderect(barier1_rect):
            y = barier1_rect.top - player_rect.height

    clock.tick(60)

    pygame.display.flip()
