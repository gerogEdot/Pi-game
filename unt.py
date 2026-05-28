import pygame
import random

pygame.init()
debug_mode = False  # Set to True to see collision boxes
SCREEN_W, SCREEN_H = 600, 336
screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
pygame.display.set_caption("CHASE - A Parkour Platformer")
font = pygame.font.Font('Bernard-MT-Condensed-Regular.ttf', 15)
large_font = pygame.font.Font('Bernard-MT-Condensed-Regular.ttf', 30)

# Load Character
Character = pygame.image.load('Main-character.png')
Character = pygame.transform.scale(Character, (int(Character.get_width()*.7), int(Character.get_height()*.7)))
Platform_img = pygame.image.load('platform_1_.png')  # FIXED: Corrected filename

# Load Monster & Death Screen
Monster = pygame.image.load('monster.png')  # FIXED: Corrected filename (lowercase)
Monster = pygame.transform.scale(Monster, (int(Monster.get_width()*0.7), SCREEN_H))
Permadeath = pygame.image.load('Deathscreen.png')
Permadeath = pygame.transform.scale(Permadeath, (int(Permadeath.get_width()*2), int(Permadeath.get_height()*2)))

# Load Start Screen
Start_Screen = pygame.image.load('Start_screen.png')
Start_Screen = pygame.transform.scale(Start_Screen, (SCREEN_W, SCREEN_H))

# Load Background Layers
bg_layers_raw = [
    pygame.image.load('Background.png'),
    pygame.image.load('Background2.png'),
    pygame.image.load('Background3.png'),
    pygame.image.load('Background4.png'),  # FIXED: Use Background4 instead of duplicate
]
bg_layers = [pygame.transform.scale(img, (SCREEN_W, SCREEN_H)) for img in bg_layers_raw]

# Load and resize Powerups -
powerups = [
    pygame.image.load('powerup1.png'),
    pygame.image.load('powerup2.png'),
    pygame.image.load('powerup3.png'),
    pygame.image.load('powerup4.png')
]
powerupimages = [pygame.transform.scale(img, (24, 24)) for img in powerups]

NUM_ZONES = 4
ZONE_WIDTH = SCREEN_W
TOTAL_WORLD_WIDTH = ZONE_WIDTH * NUM_ZONES

# Floor spans the full world
floor = pygame.Rect(0, 300, TOTAL_WORLD_WIDTH, 36)

# Generate platforms
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

# Powerup World Spawning
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

# Game States
GAME_STATE_START = 0
GAME_STATE_PLAYING = 1
GAME_STATE_PAUSED = 2
GAME_STATE_OVER = 3

# Game Variables
clock = pygame.time.Clock()
game_state = GAME_STATE_START
countdown_Time = 0
start_time = 0
pause_start_time = 0
time_offset = 0
camera_x = 0

# Player Status
x = 150
y = 240
vy = 0
gravity = 0.3
on_ground = False
speed_multiplier = 1.0
speed_boost_time = 0
lives = 0
game_over = False
death_time = 0

# Monster AI Tracking
monster_world_x = -100.0
monster_base_speed = 1.9

def reset_game():
    """Reset game variables for a new run"""
    global x, y, vy, on_ground, speed_multiplier, speed_boost_time, lives
    global monster_world_x, camera_x, start_time, countdown_Time, time_offset
    global platforms, spawned_powerups

    # Reset player
    x = 150
    y = 240
    vy = 0
    on_ground = False
    speed_multiplier = 1.0
    speed_boost_time = 0
    lives = 0
    camera_x = 0

    # Reset game timer
    start_time = pygame.time.get_ticks()
    countdown_Time = 0
    time_offset = 0

    # Reset monster
    monster_world_x = -100.0

    # Regenerate platforms and powerups
    platforms = generate_platforms(TOTAL_WORLD_WIDTH)
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

running = True
while running:
    current_ticks = pygame.time.get_ticks()

    # ==================== START SCREEN ====================
    if game_state == GAME_STATE_START:
        screen.blit(Start_Screen, (0, 0))

        instruction_text = font.render("Press C to start", True, (255, 255, 255))
        screen.blit(instruction_text, (SCREEN_W // 2 - 70, SCREEN_H - 50))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_c:
                    reset_game()
                    game_state = GAME_STATE_PLAYING

        pygame.display.flip()
        clock.tick(60)
        continue

    # ==================== GAME OVER SCREEN ====================
    if game_state == GAME_STATE_OVER:
        screen.blit(Permadeath, (220, 60))

        restart_text = font.render("Press C to return to menu", True, (255, 255, 255))
        screen.blit(restart_text, (SCREEN_W // 2 - 120, SCREEN_H - 40))

        pygame.display.flip()
        if current_ticks - death_time > 3000:  # Auto-return after 3 seconds
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_c:
                        game_state = GAME_STATE_START
        else:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
        clock.tick(60)
        continue

    # ==================== PAUSE SCREEN ====================
    if game_state == GAME_STATE_PAUSED:
        pause_text = large_font.render("PAUSED", True, (255, 255, 255))
        resume_text = font.render("Press C to Resume", True, (255, 255, 255))
        screen.blit(pause_text, (SCREEN_W // 2 - 80, SCREEN_H // 2 - 40))
        screen.blit(resume_text, (SCREEN_W // 2 - 90, SCREEN_H // 2 + 20))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_c:
                    start_time += (current_ticks - pause_start_time)  # Don't count pause time
                    game_state = GAME_STATE_PLAYING

        pygame.display.flip()
        clock.tick(60)
        continue

    #  MAIN GAME LOOP
    if game_state == GAME_STATE_PLAYING:
        # Calculate current game time while factoring in modifications
        raw_elapsed = (current_ticks - start_time) / 1000
        current_time = min(7000, max(0, countdown_Time + int(raw_elapsed) + time_offset))

        # Check win condition
        if current_time >= 7000:
            game_state = GAME_STATE_OVER
            death_time = pygame.time.get_ticks()
            # Don't continue, loop will handle GAME_OVER state next iteration

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_c:  # Pause with C
                    game_state = GAME_STATE_PAUSED
                    pause_start_time = current_ticks

        keys = pygame.key.get_pressed()

        # FIXED: Proper movement controls matching README (W/A/D or Arrow Keys)
        if (keys[pygame.K_w] or keys[pygame.K_UP] or keys[pygame.K_SPACE]) and on_ground:
            vy = -8

        # Right movement
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            x += 5

        # Left movement - ADDED
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            x -= 5

        # Apply speed boost multiplier to movement
        if speed_multiplier > 1.0:
            if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
                x += (5 * (speed_multiplier - 1.0))
            if keys[pygame.K_a] or keys[pygame.K_LEFT]:
                x -= (5 * (speed_multiplier - 1.0))

            # Decay speed boost over time (5 seconds = 300 frames at 60fps)
            speed_boost_time -= 1
            if speed_boost_time <= 0:
                speed_multiplier = 1.0

        on_ground = False
        vy += gravity
        y += vy

        # FIXED: Camera follows player properly
        # Keep player at roughly 1/4 from the left side of screen
        camera_x = max(0, x - SCREEN_W // 4)
        camera_x = min(camera_x, TOTAL_WORLD_WIDTH - SCREEN_W)

        # Monster Movement AI
        player_world_x = x
        if monster_world_x < player_world_x:
            monster_world_x += monster_base_speed

        # Draw Scrolling Background
        zone_index = int(camera_x // ZONE_WIDTH)
        zone_offset = camera_x % ZONE_WIDTH

        if zone_index < NUM_ZONES:
            screen.blit(bg_layers[zone_index], (-zone_offset, 0))
        if zone_index + 1 < NUM_ZONES:
            screen.blit(bg_layers[zone_index + 1], (ZONE_WIDTH - zone_offset, 0))

        # FIXED: Adjust character position for camera
        Character_rect = Character.get_rect(topleft=(x - camera_x, y))

        # Draw platforms
        for platform in platforms:
            screen_platform = pygame.Rect(platform.x - camera_x, platform.y, platform.width, platform.height)
            if -platform.width < screen_platform.x < SCREEN_W:  # Only draw visible platforms
                scaled_platform = pygame.transform.scale(Platform_img, (platform.width, platform.height))
                screen.blit(scaled_platform, screen_platform)

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
                game_state = GAME_STATE_OVER
                death_time = pygame.time.get_ticks()
                print("Game Over! You were caught!")

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
                if x < screen_platform.left + camera_x:
                    x = screen_platform.left + camera_x - Character_rect.width
                if x > screen_platform.right + camera_x:
                    x = screen_platform.right + camera_x

        # --- Render & Check Powerup Collisions ---
        for p in spawned_powerups:
            if p['active']:
                screen_p_rect = pygame.Rect(p['rect'].x - camera_x, p['rect'].y, p['rect'].width, p['rect'].height)

                if -24 < screen_p_rect.x < SCREEN_W:
                    screen.blit(powerupimages[p['type']], screen_p_rect)

                if Character_rect.colliderect(screen_p_rect):
                    p['active'] = False
                    if p['type'] == 0:    # powerup_1_: Speed boost (5 second duration)
                        speed_multiplier = 2.0
                        speed_boost_time = 300  # 5 seconds at 60fps
                        print("⚡ Speed boost activated! (5 seconds)")
                    elif p['type'] == 1:  # powerup_2_: Jump boost
                        vy = -10
                        print("⬆️  Jump boost activated!")
                    elif p['type'] == 2:  # powerup_3_: Extra Life
                        lives += 1
                        print(f"❤️  Extra life! Total lives: {lives}")
                    elif p['type'] == 3:  # powerup_4_: Half Time
                        half_val = current_time // 2
                        # Adjust time offset so current_time becomes equal to half_val
                        time_offset -= (current_time - half_val)
                        print(f"⏱️  Time halved! New time: {current_time // 2}s")

        screen.blit(Character, (x - camera_x, y))

        # Draw monster
        if -monster_rect.width < monster_screen_x < SCREEN_W:
            screen.blit(Monster, (monster_screen_x, monster_rect.y))

        # Debug mode - draw collision boxes
        if debug_mode:
            pygame.draw.rect(screen, (115, 255, 115), Character_rect, 2)  # Player
            pygame.draw.rect(screen, (255, 0, 0), monster_rect, 2)        # Monster
            pygame.draw.rect(screen, (0, 255, 0), screen_floor, 2)        # Floor
            for platform in platforms:
                screen_platform = pygame.Rect(platform.x - camera_x, platform.y, platform.width, platform.height)
                pygame.draw.rect(screen, (0, 255, 0), screen_platform, 2)

        # Draw UI
        time_text = f"Time: {current_time}s | Lives: {lives}"
        if speed_multiplier > 1.0:
            time_text += " | ⚡ SPEED BOOST!"

        ui_text = font.render(time_text, True, (0, 0, 0))
        screen.blit(ui_text, (10, 10))

        pause_hint = font.render("Press C to Pause", True, (100, 100, 100))
        screen.blit(pause_hint, (SCREEN_W - 150, 10))

        clock.tick(60)
        pygame.display.flip()

pygame.quit()
