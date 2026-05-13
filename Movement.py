import pygame
import random

pygame.init()

debug_mode = True

SCREEN_W, SCREEN_H = 600, 336
screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))

font = pygame.font.Font('Bernard-MT-Condensed-Regular.ttf', 15)

Character = pygame.image.load('Main-character.png')
Character = pygame.transform.scale(Character, (Character.get_width()*.7, Character.get_height()*.7))

bg_layers_raw = [
    pygame.image.load('Background.png'),
    pygame.image.load('Background2.png'),
    pygame.image.load('Background3.png'),
    pygame.image.load('Background3.png'),
]
bg_layers = [pygame.transform.scale(img, (SCREEN_W, SCREEN_H)) for img in bg_layers_raw]

powerups = [
    pygame.image.load('powerup(1).png'),
    pygame.image.load('powerup(2).png'),
    pygame.image.load('powerup(3).png'),
    pygame.image.load('powerup(4).png')
]

NUM_ZONES = 4
ZONE_WIDTH = SCREEN_W                        # 600px per zone
TOTAL_WORLD_WIDTH = ZONE_WIDTH * NUM_ZONES   # 2400px total

camera_x = 0
scroll_speed = 2

# Floor spans the full world
floor = pygame.Rect(0, 300, TOTAL_WORLD_WIDTH, 36)

# Generate non-overlapping platforms
def generate_platforms(world_width, num_platforms=20):
    plats = []
    GAP = 80                          # large gap so platforms are well spaced
    MIN_X = 200                       # clear start area
    PLAT_W_MIN, PLAT_W_MAX = 80, 140
    PLAT_H = 20
    Y_MIN = SCREEN_H // 2             # never higher than screen midpoint (168px)
    Y_MAX = 275                       # never lower than just above the floor

    attempts = 0
    while len(plats) < num_platforms and attempts < 10000:
        attempts += 1
        w = random.randint(PLAT_W_MIN, PLAT_W_MAX)
        x = random.randint(MIN_X, world_width - w - 50)
        y = random.randint(Y_MIN, Y_MAX)
        candidate = pygame.Rect(x, y, w, PLAT_H)
        # Inflate by GAP on all sides to enforce spacing between platforms
        padded = candidate.inflate(GAP * 1.2, GAP * 1.2)
        if not any(padded.colliderect(p) for p in plats):
            plats.append(candidate)

    return plats

platforms = generate_platforms(TOTAL_WORLD_WIDTH)

backclock = [pygame.Rect(517, 20, 50, 20)]
clock = pygame.time.Clock()

countdown_Time = 0
start_time = pygame.time.get_ticks()

running = True
on_ground = False
x = 0
y = 240
vy = 0
gravity = 0.3

while running:
    past_second = (pygame.time.get_ticks() - start_time) / 1000
    current_time = min(7000, countdown_Time + int(past_second))
    if current_time == 7000:
        running = False

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    keys = pygame.key.get_pressed()
    if keys[pygame.K_UP] and on_ground:
        vy = -8
    if keys[pygame.K_RIGHT]:
        x += 0.5
        camera_x += scroll_speed

    # Clamp camera so it doesn't scroll past the end of the world
    camera_x = min(camera_x, TOTAL_WORLD_WIDTH - SCREEN_W)

    on_ground = False
    vy += gravity
    y += vy

    screen.fill((0, 0, 0))

    # Draw exactly 4 backgrounds, one per zone
    zone_index = int(camera_x // ZONE_WIDTH)
    zone_offset = camera_x % ZONE_WIDTH

    # Current zone bg slides out to the left
    screen.blit(bg_layers[zone_index], (-zone_offset, 0))

    # Next zone bg slides in from the right (if there is one)
    if zone_index + 1 < NUM_ZONES:
        screen.blit(bg_layers[zone_index + 1], (ZONE_WIDTH - zone_offset, 0))

    Character_rect = Character.get_rect(topleft=(x, y))

    # Floor collision
    screen_floor = pygame.Rect(floor.x - camera_x, floor.y, floor.width, floor.height)
    if Character_rect.colliderect(screen_floor):
        if vy > 0:
            y = screen_floor.top - Character_rect.height
            vy = 0
            on_ground = True

    # Platform collision
    for platform in platforms:
        screen_platform = pygame.Rect(platform.x - camera_x, platform.y, platform.width, platform.height)
        if Character_rect.colliderect(screen_platform):
            if vy > 0:
                y = screen_platform.top - Character_rect.height
                vy = 0
                on_ground = True
            if vy < 0:
                y = screen_platform.bottom
                vy = 0
            if x < screen_platform.left:
                x = screen_platform.left - Character_rect.width
            if x > screen_platform.right:
                x = screen_platform.right

    screen.blit(Character, (x, y))

    if debug_mode:
        pygame.draw.rect(screen, (115, 255, 115), Character_rect, 2)
        pygame.draw.rect(screen, (0, 255, 0), screen_floor, 2)
        for platform in platforms:
            screen_platform = pygame.Rect(platform.x - camera_x, platform.y, platform.width, platform.height)
            pygame.draw.rect(screen, (0, 255, 0), screen_platform, 2)

    for cb in backclock:
        screen_cb = pygame.Rect(cb.x - camera_x, cb.y, cb.width, cb.height)
        pygame.draw.rect(screen, (0, 255, 0), screen_cb, 2)

    clock.tick(60)

    time_text = f"Time: {current_time}"
    Clock_screen = font.render(time_text, True, (0, 0, 0))
    screen.blit(Clock_screen, (519, 20))

    pygame.display.flip()

pygame.quit()
