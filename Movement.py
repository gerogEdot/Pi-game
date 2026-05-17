import pygame
import sys

pygame.init()

debug_mode = False

screen = pygame.display.set_mode((600, 336))
pygame.display.set_caption("Unknown PIgame")

font = pygame.font.Font('Bernard-MT-Condensed-Regular.ttf', 15)

# ── Character ─────────────────────────────────────────────────────────────────
Character = pygame.image.load('Main-character.png')
Character = pygame.transform.scale(Character, (
    Character.get_width()  * 1.5,
    Character.get_height() * 1.5
))
CHAR_W = Character.get_width()
CHAR_H = Character.get_height()

# ── Background areas ──────────────────────────────────────────────────────────
# Each background is scaled to fill the 600x336 screen exactly.
def load_bg(path):
    img = pygame.image.load(path)
    return pygame.transform.scale(img, (600, 336))

backgrounds = [
    load_bg('Background.png'),    # Area 1
    load_bg('Background_2.png'),  # Area 2
    load_bg('Background_3.png'),  # Area 3
    load_bg('Background_4.png'),  # Area 4
]

area_names = [
    "Area 1 - City Ruins",
    "Area 2 - Rocky Cliffs",
    "Area 3 - Mountain Pass",
    "Area 4 - Sky Peaks",
]

# ── Platform tile ─────────────────────────────────────────────────────────────
plat_tile = pygame.image.load('pixil-frame-0__4_.png')
plat_tile = pygame.transform.scale(plat_tile, (85, 20))

def make_plat_surf(w):
    s = pygame.Surface((w, 20))
    for bx in range(0, w, 85):
        s.blit(plat_tile, (bx, 0))
    return s

# ── Platforms (world coordinates, area = 600px wide each) ─────────────────────
PLATFORMS_RAW = [
    # Area 1  (world x 0-599)
    (0,   300, 600, 36),
    (200, 220, 120, 20),
    (400, 160, 100, 20),
    (517,  80,  50, 20),

    # Area 2  (world x 600-1199)
    (600, 300, 600, 36),
    (700, 240, 100, 20),
    (850, 190, 120, 20),
    (1050, 140, 80, 20),
    (1130,  80, 50, 20),

    # Area 3  (world x 1200-1799)
    (1200, 300, 600, 36),
    (1250, 240, 110, 20),
    (1420, 185, 100, 20),
    (1580, 130,  90, 20),
    (1700,  75,  60, 20),

    # Area 4  (world x 1800-2399)
    (1800, 300, 600, 36),
    (1870, 250, 100, 20),
    (2050, 200, 110, 20),
    (2200, 145,  85, 20),
    (2330,  75,  50, 20),
]

platforms   = []
plat_surfs  = {}
for row in PLATFORMS_RAW:
    wx, wy, ww, wh = row
    r = pygame.Rect(wx, wy, ww, wh)
    platforms.append(r)
    plat_surfs[id(r)] = make_plat_surf(ww)

WORLD_W = 2400

# ── Area / fade state ─────────────────────────────────────────────────────────
current_area  = 0
prev_area     = 0
fading        = False
fade_alpha    = 255
FADE_SPEED    = 5
fade_surf     = pygame.Surface((600, 336))

banner_timer  = 0
BANNER_FRAMES = 120

# ── Camera ────────────────────────────────────────────────────────────────────
cam_x = 0.0

# ── Player (world coords) — matches original variable names ───────────────────
x  = 80.0
y  = 240.0
vy = 0.0
gravity = 0.3

# ── Timer — fixed from original (subtract not add) ────────────────────────────
countdown_Time = 0
start_time     = pygame.time.get_ticks()

clock     = pygame.time.Clock()
on_ground = False
running   = True

def area_for_x(wx):
    return min(len(backgrounds) - 1, int(wx // 600))

# ─────────────────────────────────────────────────────────────────────────────
while running:

    # Timer (fixed: subtract start_time)
    past_second  = (pygame.time.get_ticks() - start_time) / 1000
    current_time = min(7000, countdown_Time + int(past_second))
    if current_time == 7000:
        running = False

    # Events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_F1:
                debug_mode = not debug_mode
            if event.key == pygame.K_ESCAPE:
                running = False

    # Input — same keys as original + WASD
    keys = pygame.key.get_pressed()
    if (keys[pygame.K_UP] or keys[pygame.K_w] or keys[pygame.K_SPACE]) and on_ground:
        vy = -8
    if keys[pygame.K_LEFT]  or keys[pygame.K_a]:
        x -= 3
    if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
        x += 3

    x = max(0, min(x, WORLD_W - CHAR_W))

    # Physics
    on_ground = False
    vy += gravity
    y  += vy

    # Collision (fixed overlap-based resolution from original)
    Character_rect = pygame.Rect(int(x), int(y), CHAR_W, CHAR_H)

    for platform in platforms:
        if Character_rect.colliderect(platform):
            ov_x = min(Character_rect.right  - platform.left,
                       platform.right - Character_rect.left)
            ov_y = min(Character_rect.bottom - platform.top,
                       platform.bottom - Character_rect.top)
            if ov_y <= ov_x:
                if vy >= 0 and Character_rect.centery < platform.centery:
                    y         = float(platform.top - CHAR_H)
                    vy        = 0
                    on_ground = True
                elif vy < 0:
                    y  = float(platform.bottom)
                    vy = 0
            else:
                if x + CHAR_W / 2 < platform.centerx:
                    x = float(platform.left - CHAR_W)
                else:
                    x = float(platform.right)

    if y > 400:
        y = 240.0; vy = 0.0

    # Camera smooth follow
    cam_x += (x - 600 // 3 - cam_x) * 0.15
    cam_x  = max(0, min(cam_x, WORLD_W - 600))

    # ── Area transition ────────────────────────────────────────────────────────
    new_area = area_for_x(x)
    if new_area != current_area:
        prev_area    = current_area
        current_area = new_area
        fading       = True
        fade_alpha   = 0
        banner_timer = BANNER_FRAMES

    if fading:
        fade_alpha = min(255, fade_alpha + FADE_SPEED)
        if fade_alpha >= 255:
            fading = False

    if banner_timer > 0:
        banner_timer -= 1

    # ════════════════════════════════════════════════════════════════════════
    # DRAW
    # ════════════════════════════════════════════════════════════════════════
    ci = int(cam_x)

    # 1. Old background (shown beneath during crossfade)
    screen.blit(backgrounds[prev_area], (0, 0))

    # 2. New background fades in
    if fading:
        fade_surf.blit(backgrounds[current_area], (0, 0))
        fade_surf.set_alpha(fade_alpha)
        screen.blit(fade_surf, (0, 0))
    else:
        screen.blit(backgrounds[current_area], (0, 0))

    # 3. Platforms
    for plat in platforms:
        sx = plat.x - ci
        if -200 < sx < 800:
            screen.blit(plat_surfs[id(plat)], (sx, plat.y))

    # 4. Character
    screen_x = int(x) - ci
    screen.blit(Character, (screen_x, int(y)))

    # 5. Debug hitboxes (toggle with F1)
    if debug_mode:
        pygame.draw.rect(screen, (115, 255, 115),
                         pygame.Rect(screen_x, int(y), CHAR_W, CHAR_H), 2)
        for plat in platforms:
            sx = plat.x - ci
            if -200 < sx < 800:
                pygame.draw.rect(screen, (0, 255, 0),
                                 pygame.Rect(sx, plat.y, plat.width, plat.height), 2)

    # 6. Area name banner
    if banner_timer > 0:
        alpha    = min(255, banner_timer * 5)
        name_txt = font.render(area_names[current_area], True, (255, 240, 180))
        shadow   = font.render(area_names[current_area], True, (0, 0, 0))
        name_txt.set_alpha(alpha)
        shadow.set_alpha(alpha)
        bx = 300 - name_txt.get_width() // 2
        screen.blit(shadow,   (bx + 1, 31))
        screen.blit(name_txt, (bx,     30))

    # 7. Timer HUD — same position as original (519, 20)
    time_text    = f"Time: {current_time}"
    Clock_screen = font.render(time_text, True, (255, 255, 255))
    shadow_t     = font.render(time_text, True, (0, 0, 0))
    screen.blit(shadow_t,    (520, 21))
    screen.blit(Clock_screen,(519, 20))

    # 8. Controls hint at bottom
    hint = font.render("F1=debug  |  WASD / Arrows  |  Space=jump", True, (200, 200, 200))
    screen.blit(hint, (8, 320))

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()
