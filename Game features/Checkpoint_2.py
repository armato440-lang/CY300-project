"""
ZOMBIE APOCALYPSE - CHECKPOINT 2
Updated version of the original MVP.

Controls:
    W / A / S / D : Move
    Left mouse     : Shoot toward cursor
    M              : Toggle sound on/off
    R              : Restart after game over
    Q              : Quit after game over

Assets are loaded once at startup from the assets folder.
"""

import os
import random
import math
import pygame

# ---------------------------------------------------------
# GAME SETTINGS
# ---------------------------------------------------------

SCREEN_WIDTH = 900
SCREEN_HEIGHT = 600
FPS = 60

PLAYER_SIZE = 30
PLAYER_SPEED = 5
ZOMBIE_SIZE = 30
BULLET_SPEED = 10
BULLET_SIZE = 5

STARTING_HEALTH = 3
MAX_HEALTH = 3

MUSIC_VOLUME = 0.30
SOUND_VOLUME = 0.55
ANIMATION_DELAY = 130  # milliseconds between walking frames

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
IMAGE_DIR = os.path.join(BASE_DIR, "assets", "images")
SOUND_DIR = os.path.join(BASE_DIR, "assets", "sounds")
MUSIC_DIR = os.path.join(BASE_DIR, "assets", "music")

# ---------------------------------------------------------
# ASSET LOADING
# ---------------------------------------------------------

def load_image(filename, size):
    """Load and scale an image. Return None if it cannot be loaded."""
    path = os.path.join(IMAGE_DIR, filename)

    try:
        image = pygame.image.load(path).convert_alpha()
        return pygame.transform.smoothscale(image, size)
    except (pygame.error, FileNotFoundError) as error:
        print("Image could not be loaded:", path, "-", error)
        return None


def load_sound(filename, volume=SOUND_VOLUME):
    """Load one sound effect. Return None if it cannot be loaded."""
    path = os.path.join(SOUND_DIR, filename)

    try:
        sound = pygame.mixer.Sound(path)
        sound.set_volume(volume)
        return sound
    except (pygame.error, FileNotFoundError) as error:
        print("Sound could not be loaded:", path, "-", error)
        return None


def play_background_music():

    music_path = os.path.join(MUSIC_DIR, "background.mp3")

    try:
        pygame.mixer.music.load(music_path)
        pygame.mixer.music.set_volume(0.25)

        # -1 makes the music loop continuously
        pygame.mixer.music.play(-1)

        print("Background music is playing!")

    except pygame.error as error:
        print("Music loading error:", error)


def load_all_assets():
    """Load every image and sound once when the game starts."""
    images = {
        "player_idle": load_image("player_idle.png", (64, 64)),
        "player_walk1": load_image("player_walk1.png", (64, 64)),
        "player_walk2": load_image("player_walk2.png", (64, 64)),
        "player_hurt": load_image("player_hurt.png", (64, 64)),
        "zombie_idle": load_image("zombie_idle.png", (64, 64)),
        "zombie_walk1": load_image("zombie_walk1.png", (64, 64)),
        "zombie_walk2": load_image("zombie_walk2.png", (64, 64)),
        "zombie_hurt": load_image("zombie_hurt.png", (64, 64)),
    }

    sounds = {
        "shoot": load_sound("shoot.ogg", 0.35),
        "zombie_hit": load_sound("zombie_hit.ogg", 0.55),
        "player_hurt": load_sound("player_hurt.ogg", 0.65),
        "ready": load_sound("ready.ogg", 0.65),
        "fight": load_sound("fight.ogg", 0.65),
        "game_over": load_sound("game_over.ogg", 0.70),
    }

    return images, sounds


def play_sound(sounds, sound_name, muted):
    """Play a sound only when sound is available and not muted."""
    sound = sounds.get(sound_name)
    if sound is not None and not muted:
        sound.play()


# ---------------------------------------------------------
# PLAYER
# ---------------------------------------------------------

def create_player():
    return {
        "x": SCREEN_WIDTH // 2,
        "y": SCREEN_HEIGHT // 2,
        "health": STARTING_HEALTH,
        "moving": False,
        "last_direction": 1,
        "animation_frame": 0,
        "animation_timer": 0,
    }


def move_player(player, dt):
    """Move player with WASD and keep the player inside the screen."""
    keys = pygame.key.get_pressed()
    old_x = player["x"]
    old_y = player["y"]

    if keys[pygame.K_w]:
        player["y"] -= PLAYER_SPEED
    if keys[pygame.K_s]:
        player["y"] += PLAYER_SPEED
    if keys[pygame.K_a]:
        player["x"] -= PLAYER_SPEED
        player["last_direction"] = -1
    if keys[pygame.K_d]:
        player["x"] += PLAYER_SPEED
        player["last_direction"] = 1

    player["x"] = max(PLAYER_SIZE, min(SCREEN_WIDTH - PLAYER_SIZE, player["x"]))
    player["y"] = max(PLAYER_SIZE, min(SCREEN_HEIGHT - PLAYER_SIZE, player["y"]))

    player["moving"] = (player["x"] != old_x or player["y"] != old_y)

    if player["moving"]:
        player["animation_timer"] += dt
        if player["animation_timer"] >= ANIMATION_DELAY:
            player["animation_frame"] = 1 - player["animation_frame"]
            player["animation_timer"] = 0
    else:
        player["animation_frame"] = 0
        player["animation_timer"] = 0


# ---------------------------------------------------------
# SHOOTING
# ---------------------------------------------------------

def shoot(player, mouse_x, mouse_y):
    """Create a bullet traveling from player toward the mouse cursor."""
    dx = mouse_x - player["x"]
    dy = mouse_y - player["y"]
    distance = math.sqrt(dx ** 2 + dy ** 2)

    if distance == 0:
        return None

    return {
        "x": player["x"],
        "y": player["y"],
        "dx": dx / distance,
        "dy": dy / distance,
    }


def move_bullets(bullets):
    for bullet in bullets:
        bullet["x"] += bullet["dx"] * BULLET_SPEED
        bullet["y"] += bullet["dy"] * BULLET_SPEED


def remove_old_bullets(bullets):
    for bullet in bullets[:]:
        if (bullet["x"] < 0 or bullet["x"] > SCREEN_WIDTH
                or bullet["y"] < 0 or bullet["y"] > SCREEN_HEIGHT):
            bullets.remove(bullet)


# ---------------------------------------------------------
# ZOMBIES
# ---------------------------------------------------------

def spawn_zombie(level):
    """Create a zombie at a random edge of the screen."""
    side = random.randint(1, 4)

    if side == 1:
        x, y = 0, random.randint(0, SCREEN_HEIGHT)
    elif side == 2:
        x, y = SCREEN_WIDTH, random.randint(0, SCREEN_HEIGHT)
    elif side == 3:
        x, y = random.randint(0, SCREEN_WIDTH), 0
    else:
        x, y = random.randint(0, SCREEN_WIDTH), SCREEN_HEIGHT

    return {
        "x": x,
        "y": y,
        "speed": 1.5 + (level * 0.3),
        "animation_frame": 0,
        "animation_timer": 0,
        "last_direction": 1,
    }


def move_zombies(zombies, player, dt):
    """Move zombies toward player and animate their walking."""
    for zombie in zombies:
        dx = player["x"] - zombie["x"]
        dy = player["y"] - zombie["y"]
        distance = math.sqrt(dx ** 2 + dy ** 2)

        if distance != 0:
            zombie["last_direction"] = 1 if dx >= 0 else -1
            zombie["x"] += (dx / distance) * zombie["speed"]
            zombie["y"] += (dy / distance) * zombie["speed"]

        zombie["animation_timer"] += dt
        if zombie["animation_timer"] >= ANIMATION_DELAY:
            zombie["animation_frame"] = 1 - zombie["animation_frame"]
            zombie["animation_timer"] = 0


# ---------------------------------------------------------
# COLLISIONS
# ---------------------------------------------------------

def check_bullet_hits(bullets, zombies, sounds, muted):
    """Remove zombies hit by bullets and return the score increase."""
    score_increase = 0
    hit_distance = ZOMBIE_SIZE + BULLET_SIZE

    for bullet in bullets[:]:
        for zombie in zombies[:]:
            distance = math.sqrt(
                (bullet["x"] - zombie["x"]) ** 2
                + (bullet["y"] - zombie["y"]) ** 2
            )

            if distance < hit_distance:
                if bullet in bullets:
                    bullets.remove(bullet)
                if zombie in zombies:
                    zombies.remove(zombie)
                score_increase += 1
                play_sound(sounds, "zombie_hit", muted)
                break

    return score_increase


def check_zombie_attacks(player, zombies, sounds, muted):
    """Damage player when a zombie reaches them."""
    for zombie in zombies[:]:
        distance = math.sqrt(
            (player["x"] - zombie["x"]) ** 2
            + (player["y"] - zombie["y"]) ** 2
        )

        if distance < PLAYER_SIZE + ZOMBIE_SIZE - 20:
            player["health"] -= 1
            zombies.remove(zombie)
            play_sound(sounds, "player_hurt", muted)


# ---------------------------------------------------------
# POWER-UPS
# ---------------------------------------------------------

def spawn_health_package():
    return {
        "x": random.randint(50, SCREEN_WIDTH - 50),
        "y": random.randint(50, SCREEN_HEIGHT - 50),
    }


def check_powerup_collection(player, powerups):
    """Restore one health point when a health package is collected."""
    for powerup in powerups[:]:
        distance = math.sqrt(
            (player["x"] - powerup["x"]) ** 2
            + (player["y"] - powerup["y"]) ** 2
        )

        if distance < 30 and player["health"] < MAX_HEALTH:
            player["health"] += 1
            powerups.remove(powerup)


# ---------------------------------------------------------
# LEVEL SYSTEM
# ---------------------------------------------------------

def update_level(score):
    return (score // 10) + 1


# ---------------------------------------------------------
# DRAWING
# ---------------------------------------------------------

def draw_background(screen):
    """Draw a simple dark ground with subtle grid lines."""
    screen.fill((35, 42, 38))

    grid_color = (43, 51, 45)
    for x in range(0, SCREEN_WIDTH, 50):
        pygame.draw.line(screen, grid_color, (x, 0), (x, SCREEN_HEIGHT), 1)
    for y in range(0, SCREEN_HEIGHT, 50):
        pygame.draw.line(screen, grid_color, (0, y), (SCREEN_WIDTH, y), 1)


def get_player_image(player, images, mouse_x):
    if player["moving"]:
        key = "player_walk1" if player["animation_frame"] == 0 else "player_walk2"
    else:
        key = "player_idle"

    image = images.get(key) or images.get("player_idle")
    if image is not None and mouse_x < player["x"]:
        image = pygame.transform.flip(image, True, False)
    return image


def get_zombie_image(zombie, images):
    key = "zombie_walk1" if zombie["animation_frame"] == 0 else "zombie_walk2"
    image = images.get(key) or images.get("zombie_idle")

    if image is not None and zombie["last_direction"] < 0:
        image = pygame.transform.flip(image, True, False)
    return image


def draw_game(screen, player, bullets, zombies, powerups,
              score, level, images):
    draw_background(screen)
    mouse_x, _ = pygame.mouse.get_pos()

    # Player sprite
    player_image = get_player_image(player, images, mouse_x)
    if player_image is not None:
        rect = player_image.get_rect(center=(int(player["x"]), int(player["y"])))
        screen.blit(player_image, rect)
    else:
        pygame.draw.circle(screen, (50, 150, 255),
                           (int(player["x"]), int(player["y"])), PLAYER_SIZE)

    # Bullets
    for bullet in bullets:
        pygame.draw.circle(screen, (255, 230, 70),
                           (int(bullet["x"]), int(bullet["y"])), BULLET_SIZE)

    # Zombie sprites
    for zombie in zombies:
        zombie_image = get_zombie_image(zombie, images)
        if zombie_image is not None:
            rect = zombie_image.get_rect(
                center=(int(zombie["x"]), int(zombie["y"]))
            )
            screen.blit(zombie_image, rect)
        else:
            pygame.draw.circle(screen, (50, 200, 50),
                               (int(zombie["x"]), int(zombie["y"])), ZOMBIE_SIZE)

    # Health packages (drawn as a medical cross)
    for powerup in powerups:
        x, y = int(powerup["x"]), int(powerup["y"])
        pygame.draw.rect(screen, (220, 45, 45), (x - 11, y - 4, 22, 8))
        pygame.draw.rect(screen, (220, 45, 45), (x - 4, y - 11, 8, 22))

    # HUD
    font = pygame.font.Font(None, 30)
    hud = [
        ("Score: " + str(score), (20, 18)),
        ("Level: " + str(level), (20, 48)),
        ("Health: " + str(player["health"]), (20, 78)),
        ("M: Sound " + ("OFF" if pygame.mixer.get_init() is None else "ON"),
         (SCREEN_WIDTH - 150, 18)),
    ]
    for message, position in hud[:3]:
        screen.blit(font.render(message, True, (255, 255, 255)), position)

    # Sound state is displayed separately by main so the label is accurate.
    small = pygame.font.Font(None, 24)
    screen.blit(small.render("WASD: Move | Mouse: Shoot | M: Mute",
                             True, (220, 220, 220)), (20, SCREEN_HEIGHT - 30))


# ---------------------------------------------------------
# GAME OVER
# ---------------------------------------------------------

def draw_game_over(screen, score):
    screen.fill((20, 20, 20))
    font = pygame.font.Font(None, 64)
    small_font = pygame.font.Font(None, 34)

    title = font.render("GAME OVER", True, (255, 65, 65))
    final_score = small_font.render(
        "Final Score: " + str(score), True, (255, 255, 255)
    )
    instructions = small_font.render(
        "Press R to Restart or Q to Quit", True, (255, 255, 255)
    )

    screen.blit(title, title.get_rect(center=(SCREEN_WIDTH // 2, 210)))
    screen.blit(final_score, final_score.get_rect(center=(SCREEN_WIDTH // 2, 290)))
    screen.blit(instructions, instructions.get_rect(center=(SCREEN_WIDTH // 2, 360)))


# ---------------------------------------------------------
# MAIN GAME
# ---------------------------------------------------------

def main():
    pygame.init()

    # Audio initialization can fail on computers without an audio device.
    audio_available = True
    try:
        pygame.mixer.init()
    except pygame.error as error:
        print("Audio is unavailable:", error)
        audio_available = False

    if audio_available:
        play_background_music()

    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Zombie Apocalypse - Checkpoint 2")
    clock = pygame.time.Clock()

    # Load images and sounds once, not every frame.
    if audio_available:
        images, sounds = load_all_assets()
    else:
        # Images still load even when audio is unavailable.
        images = {
            "player_idle": load_image("player_idle.png", (64, 64)),
            "player_walk1": load_image("player_walk1.png", (64, 64)),
            "player_walk2": load_image("player_walk2.png", (64, 64)),
            "player_hurt": load_image("player_hurt.png", (64, 64)),
            "zombie_idle": load_image("zombie_idle.png", (64, 64)),
            "zombie_walk1": load_image("zombie_walk1.png", (64, 64)),
            "zombie_walk2": load_image("zombie_walk2.png", (64, 64)),
            "zombie_hurt": load_image("zombie_hurt.png", (64, 64)),
        }
        sounds = {}

    muted = False
    player = create_player()
    bullets = []
    zombies = []
    powerups = []

    score = 0
    level = 1
    running = True
    game_active = True
    game_over_sound_played = False

    zombie_timer = 0
    powerup_timer = 0

    # Opening voice announcement.
    play_sound(sounds, "ready", muted)
    play_sound(sounds, "fight", muted)

    while running:
        dt = clock.tick(FPS)

        # -------------------------------------------------
        # EVENTS
        # -------------------------------------------------
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_m:
                    muted = not muted
                    if muted:
                        pygame.mixer.stop()
                    else:
                        play_sound(sounds, "fight", muted)

                if not game_active and event.key == pygame.K_r:
                    player = create_player()
                    bullets = []
                    zombies = []
                    powerups = []
                    score = 0
                    level = 1
                    zombie_timer = 0
                    powerup_timer = 0
                    game_active = True
                    game_over_sound_played = False
                    play_sound(sounds, "ready", muted)
                    play_sound(sounds, "fight", muted)

                elif not game_active and event.key == pygame.K_q:
                    running = False

            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1 and game_active:
                    mouse_x, mouse_y = pygame.mouse.get_pos()
                    bullet = shoot(player, mouse_x, mouse_y)
                    if bullet is not None:
                        bullets.append(bullet)
                        play_sound(sounds, "shoot", muted)

        # -------------------------------------------------
        # ACTIVE GAME
        # -------------------------------------------------
        if game_active:
            move_player(player, dt)

            zombie_timer += 1
            spawn_rate = max(15, 60 - (level * 5))
            if zombie_timer >= spawn_rate:
                zombies.append(spawn_zombie(level))
                zombie_timer = 0

            powerup_timer += 1
            if powerup_timer >= 600:
                powerups.append(spawn_health_package())
                powerup_timer = 0

            move_bullets(bullets)
            remove_old_bullets(bullets)
            move_zombies(zombies, player, dt)

            score += check_bullet_hits(bullets, zombies, sounds, muted)
            check_zombie_attacks(player, zombies, sounds, muted)
            check_powerup_collection(player, powerups)

            level = update_level(score)

            if player["health"] <= 0:
                game_active = False

            draw_game(screen, player, bullets, zombies, powerups,
                      score, level, images)

            # Accurate sound status display.
            status_font = pygame.font.Font(None, 24)
            status = "Sound: OFF (M)" if muted else "Sound: ON (M)"
            status_surface = status_font.render(status, True, (255, 230, 120))
            screen.blit(status_surface, (SCREEN_WIDTH - 140, 45))

        # -------------------------------------------------
        # GAME OVER
        # -------------------------------------------------
        else:
            draw_game_over(screen, score)

            if not game_over_sound_played:
                play_sound(sounds, "game_over", muted)
                game_over_sound_played = True

        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    main()
