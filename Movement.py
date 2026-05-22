import pygame
import random

pygame.init()
debug_mode = True
SCREEN_W, SCREEN_H = 600, 336
screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
font = pygame.font.Font('Bernard-MT-Condensed-Regular.ttf', 15)

# Load Character,
Character = pygame.image.load('Main-character.png')
Character = pygame.transform.scale(Character, (int(Character.get_width()*.7), int(Character.get_height()*.7)))

# Load Monster & Death Screen
Monster = pygame.image.load('Monster.png')
Monster = pygame.transform.scale(Monster, (int(Monster.get_width()*0.7), SCREEN_H))
Permadeath = pygame.image.load('Deathscreen.png')
Permadeath = pygame.transform.scale(Permadeath, (int(Permadeath.get_width()*2), int(Permadeath.get_height()*2)))

# Load Background Layers
bg_layers_raw = [
    pygame.image.load('Background.png'),
    pygame.image.load('Background2.png'),
    pygame.image.load('Background3.png'),
    pygame.image.load('Background3.png'),
]
bg_layers = [pygame.transform.scale(img, (SCREEN_W, SCREEN_H)) for img in bg_layers_raw]

# Load and resize Powerups
powerups = [
    pygame.image.load('powerup(1).png'),
    pygame.image.load('powerup(2).png'),
    pygame.image.load('powerup(3).png'),
    pygame.image.load('powerup(4).png')
]
powerupimages = [pygame.transform.scale(img, (24, 24)) for img in powerups]

NUM_ZONES = 4
ZONE_WIDTH = SCREEN_W
TOTAL_WORLD_WIDTH = ZONE_WIDTH * NUM_ZONES
camera_x = 0
scroll_speed = 2

# Floor spans the full world
floor = pygame.Rect(0, 300, TOTAL_WORLD_WIDTH, 36)

#Generate platforms
def generate_platforms(world_width, num_platforms=20):
    plats = []
    GAP = 80
    MIN_X = 200
    PLAT_W_MIN, PLAT_W_MAX = 80, 140
    PLAT_H = 20
    Y_MIN = SCREEN_H // 2
    Y_MAX = 275
    attempts = 0
    while len(plats) < num_platforms and attempts < 10000:
        attempts += 1
        w = random.randint(PLAT_W_MIN, PLAT_W_MAX)
        x = random.randint(MIN_X, world_width - w - 50)
        y = random.randint(Y_MIN, Y_MAX)
        candidate = pygame.Rect(x, y, w, PLAT_H)
        padded = candidate.inflate(GAP * 1.2, GAP * 1.2)
        if not any(padded.colliderect(p) for p in plats):
            plats.append(candidate)
    return plats

platforms = generate_platforms(TOTAL_WORLD_WIDTH)

#Powerup World Spawning
spawned_powerups = []
for platform in platforms:
    if random.random() < 0.30:
        p_w, p_h = 24, 24
        p_x = platform.x + (platform.width // 2) - (p_w // 2)
        p_y = platform.y - p_h
        spawned_powerups.append({
            'rect': pygame.Rect(p_x, p_y, p_w, p_h),
            'type': random.randint(0, 3),
            'active': True
        })

# Game Variables
backclock = [pygame.Rect(517, 20, 50, 20)]
clock = pygame.time.Clock()
countdown_Time = 0
start_time = pygame.time.get_ticks()
time_offset = 0  # Used to apply adjustments like cutting the timer in half

# Player Status
x = 150
y = 240
vy = 0
gravity = 0.3
on_ground = False
speed_multiplier = 1.0
lives = 0  # Starts with 0 extra lives. Can be increased via powerup(3)
game_over = False
death_time = 0

#Monster AI Tracking Setup
monster_world_x = -100.0
monster_base_speed = 2

running = True
while running:
    current_ticks = pygame.time.get_ticks()

    if game_over:
        screen.blit(Permadeath, (220, 60))
        pygame.display.flip()
        if current_ticks - death_time > 7000:
            running = False
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        continue

    # Calculate current game time while factoring in modifications
    raw_elapsed = (current_ticks - start_time) / 1000
    current_time = min(7000, max(0, countdown_Time + int(raw_elapsed) + time_offset))
    if current_time == 7000:
        running = False

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    keys = pygame.key.get_pressed()
    if keys[pygame.K_UP] and on_ground:
        vy = -8
    if keys[pygame.K_RIGHT]:
        x += (0.5 * speed_multiplier)
        camera_x += scroll_speed
        camera_x = min(camera_x, TOTAL_WORLD_WIDTH - SCREEN_W)

    on_ground = False
    vy += gravity
    y += vy

    # Monster Movement AI
    player_world_x = x + camera_x
    if monster_world_x < player_world_x:
        monster_world_x += monster_base_speed

    # Draw Scrolling Background
    zone_index = int(camera_x // ZONE_WIDTH)
    zone_offset = camera_x % ZONE_WIDTH
    screen.blit(bg_layers[zone_index], (-zone_offset, 0))
    if zone_index + 1 < NUM_ZONES:
        screen.blit(bg_layers[zone_index + 1], (ZONE_WIDTH - zone_offset, 0))

    Character_rect = Character.get_rect(topleft=(x, y))

    # Translate Monster World Position to Screen Space
    monster_screen_x = monster_world_x - camera_x
    monster_rect = Monster.get_rect(topleft=(monster_screen_x, 0))

    # Monster Collision Check
    if Character_rect.colliderect(monster_rect):
        if lives > 0:
            lives -= 1
            # Push monster back in world space to buy player room
            monster_world_x = max(-100.0, monster_world_x - 300)
            print(f"Used extra life! Remaining: {lives}")
        else:
            game_over = True
            death_time = pygame.time.get_ticks()
            continue

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

    # --- Render & Check Powerup Collisions ---
    for p in spawned_powerups:
        if p['active']:
            screen_p_rect = pygame.Rect(p['rect'].x - camera_x, p['rect'].y, p['rect'].width, p['rect'].height)

            if -24 < screen_p_rect.x < SCREEN_W:
                screen.blit(powerupimages[p['type']], screen_p_rect)

            if Character_rect.colliderect(screen_p_rect):
                p['active'] = False
                if p['type'] == 0:    # powerup(1): Speed boost
                    speed_multiplier = 4.0
                elif p['type'] == 1:  # powerup(2): Reset gravity jump bonus
                    vy = -10
                elif p['type'] == 2:  # powerup(3): Extra Life
                    lives += 1
                elif p['type'] == 3:  # powerup(4): Half Time
                    half_val = current_time // 2
                    # Adjust time offset so current_time becomes equal to half_val
                    time_offset -= (current_time - half_val)

    screen.blit(Character, (x, y))

    # Draw monster
    if -monster_rect.width < monster_screen_x < SCREEN_W:
        screen.blit(Monster, (monster_screen_x, monster_rect.y))

    if debug_mode:
        pygame.draw.rect(screen, (115, 255, 115), Character_rect, 2)
        pygame.draw.rect(screen, (255, 0, 0), monster_rect, 2)
        pygame.draw.rect(screen, (0, 255, 0), screen_floor, 2)
        for platform in platforms:
            screen_platform = pygame.Rect(platform.x - camera_x, platform.y, platform.width, platform.height)
            pygame.draw.rect(screen, (0, 255, 0), screen_platform, 2)

    clock.tick(60)

    # Update text display to include lives remaining
    time_text = f"Time: {current_time} | Lives: {lives}"
    Clock_screen = font.render(time_text, True, (0, 0, 0))
    screen.blit(Clock_screen, (450, 20))  # Left shifted to keep text on-screen
    pygame.display.flip()

pygame.quit()
