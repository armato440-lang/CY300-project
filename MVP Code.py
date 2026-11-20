import pygame
import random
import math
import os

# ---------------------------------------------------------
# GAME SETTINGS
# ---------------------------------------------------------

SCREEN_WIDTH = 900
SCREEN_HEIGHT = 600

PLAYER_SIZE = 30
PLAYER_SPEED = 5

BULLET_SPEED = 10
ZOMBIE_SIZE = 30

STARTING_HEALTH = 3
MAX_HEALTH = 3

BULLET_SIZE = 5


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ASSET_DIR = os.path.join(BASE_DIR, "assets")

#---------------------------------------------------
# IMAGE LOADING
#---------------------------------------------------

def load_image(filename, size):
    """Load an image, scale it to size, and return it.
    Returns None if the file can't be loaded."""

    path = os.path.join(ASSET_DIR, filename)

    try:
        image = pygame.image.load(path).convert_alpha()
        return pygame.transform.smoothscale(image, size)
    except (pygame.error, FileNotFoundError):
        print("Could not load " + path + ", using shapes instead.")
        return None


def load_all_images():
    """Load every image the game uses."""

    images = {
        "player": load_image("player.png", (PLAYER_SIZE * 2, PLAYER_SIZE * 2)),
        "zombie": load_image("zombie.png", (ZOMBIE_SIZE * 2, ZOMBIE_SIZE * 2)),
        "health": load_image("health.png", (30, 30)),
    }

    return images
# ---------------------------------------------------------
# PLAYER
# ---------------------------------------------------------

def create_player():
    """Create the player's starting position."""
    
    player = {
        "x": SCREEN_WIDTH // 2,
        "y": SCREEN_HEIGHT // 2,
        "health": STARTING_HEALTH
    }

    return player


def move_player(player):
    """Move the player using WASD."""

    keys = pygame.key.get_pressed()

    if keys[pygame.K_w]:
        player["y"] -= PLAYER_SPEED

    if keys[pygame.K_s]:
        player["y"] += PLAYER_SPEED

    if keys[pygame.K_a]:
        player["x"] -= PLAYER_SPEED

    if keys[pygame.K_d]:
        player["x"] += PLAYER_SPEED

    # Keep player inside the screen
    player["x"] = max(PLAYER_SIZE, min(SCREEN_WIDTH - PLAYER_SIZE, player["x"]))
    player["y"] = max(PLAYER_SIZE, min(SCREEN_HEIGHT - PLAYER_SIZE, player["y"]))


# ---------------------------------------------------------
# SHOOTING
# ---------------------------------------------------------

def shoot(player, mouse_x, mouse_y):
    """Create a bullet traveling toward the mouse."""

    dx = mouse_x - player["x"]
    dy = mouse_y - player["y"]

    distance = math.sqrt(dx ** 2 + dy ** 2)

    if distance == 0:
        return None

    # Convert direction into a unit vector
    dx = dx / distance
    dy = dy / distance

    bullet = {
        "x": player["x"],
        "y": player["y"],
        "dx": dx,
        "dy": dy
    }

    return bullet


def move_bullets(bullets):
    """Move all bullets."""

    for bullet in bullets:
        bullet["x"] += bullet["dx"] * BULLET_SPEED
        bullet["y"] += bullet["dy"] * BULLET_SPEED


def remove_old_bullets(bullets):
    """Remove bullets that leave the screen."""

    for bullet in bullets[:]:

        if (
            bullet["x"] < 0
            or bullet["x"] > SCREEN_WIDTH
            or bullet["y"] < 0
            or bullet["y"] > SCREEN_HEIGHT
        ):
            bullets.remove(bullet)


# ---------------------------------------------------------
# ZOMBIES
# ---------------------------------------------------------

def spawn_zombie(level):
    """Create a zombie at a random edge of the screen."""

    side = random.randint(1, 4)

    if side == 1:
        x = 0
        y = random.randint(0, SCREEN_HEIGHT)

    elif side == 2:
        x = SCREEN_WIDTH
        y = random.randint(0, SCREEN_HEIGHT)

    elif side == 3:
        x = random.randint(0, SCREEN_WIDTH)
        y = 0

    else:
        x = random.randint(0, SCREEN_WIDTH)
        y = SCREEN_HEIGHT

    zombie = {
        "x": x,
        "y": y,
        "speed": 1.5 + (level * 0.3)
    }

    return zombie


def move_zombies(zombies, player):
    """Move every zombie toward the player."""

    for zombie in zombies:

        dx = player["x"] - zombie["x"]
        dy = player["y"] - zombie["y"]

        distance = math.sqrt(dx ** 2 + dy ** 2)

        if distance != 0:
            dx = dx / distance
            dy = dy / distance

            zombie["x"] += dx * zombie["speed"]
            zombie["y"] += dy * zombie["speed"]


# ---------------------------------------------------------
# COLLISIONS
# ---------------------------------------------------------

def check_bullet_hits(bullets, zombies):
    """Check whether bullets hit zombies."""

    score_increase = 0
    hit_distance = ZOMBIE_SIZE + BULLET_SIZE

    for bullet in bullets[:]:

        for zombie in zombies[:]:

            distance = math.sqrt(
                (bullet["x"] - zombie["x"]) ** 2
                + (bullet["y"] - zombie["y"]) ** 2
            )

            if distance < 25:

                if bullet in bullets:
                    bullets.remove(bullet)

                zombies.remove(zombie)

                score_increase += 1

                break

    return score_increase


def check_zombie_attacks(player, zombies):
    """Check whether zombies hit the player."""

    for zombie in zombies[:]:

        distance = math.sqrt(
            (player["x"] - zombie["x"]) ** 2
            + (player["y"] - zombie["y"]) ** 2
        )

        if distance < 30:

            player["health"] -= 1

            zombies.remove(zombie)


# ---------------------------------------------------------
# POWER-UPS
# ---------------------------------------------------------

def spawn_health_package():
    """Create a health package at a random location."""

    powerup = {
        "x": random.randint(50, SCREEN_WIDTH - 50),
        "y": random.randint(50, SCREEN_HEIGHT - 50)
    }

    return powerup


def check_powerup_collection(player, powerups):
    """Restore one health when player collects a package."""

    for powerup in powerups[:]:

        distance = math.sqrt(
            (player["x"] - powerup["x"]) ** 2
            + (player["y"] - powerup["y"]) ** 2
        )

        if distance < 30:

            if player["health"] < MAX_HEALTH:
                player["health"] += 1
                powerups.remove(powerup)


# ---------------------------------------------------------
# LEVEL SYSTEM
# ---------------------------------------------------------

def update_level(score):
    """Increase the level as the player's score increases."""

    level = (score // 10) + 1

    return level


# ---------------------------------------------------------
# DRAWING
# ---------------------------------------------------------

def draw_game(screen, player, bullets, zombies, powerups, score, level):
    """Draw everything on the screen."""

    screen.fill((30, 30, 30))

    # Draw player
    pygame.draw.circle(
        screen,
        (50, 150, 255),
        (int(player["x"]), int(player["y"])),
        PLAYER_SIZE
    )

    # Draw bullets
    for bullet in bullets:

        pygame.draw.circle(
            screen,
            (255, 255, 0),
            (int(bullet["x"]), int(bullet["y"])),
            5
        )

    # Draw zombies
    for zombie in zombies:

        pygame.draw.circle(
            screen,
            (50, 200, 50),
            (int(zombie["x"]), int(zombie["y"])),
            ZOMBIE_SIZE
        )

    # Draw health packages
    for powerup in powerups:

        pygame.draw.rect(
            screen,
            (255, 50, 50),
            (
                int(powerup["x"] - 10),
                int(powerup["y"] - 10),
                20,
                20
            )
        )

    # Text
    font = pygame.font.Font(None, 30)

    score_text = font.render(
        "Score: " + str(score),
        True,
        (255, 255, 255)
    )

    level_text = font.render(
        "Level: " + str(level),
        True,
        (255, 255, 255)
    )

    health_text = font.render(
        "Health: " + str(player["health"]),
        True,
        (255, 255, 255)
    )

    screen.blit(score_text, (20, 20))
    screen.blit(level_text, (20, 50))
    screen.blit(health_text, (20, 80))


# ---------------------------------------------------------
# GAME OVER
# ---------------------------------------------------------

def game_over(screen, score):
    """Display the game-over screen."""

    font = pygame.font.Font(None, 60)
    small_font = pygame.font.Font(None, 35)

    screen.fill((20, 20, 20))

    text = font.render(
        "GAME OVER",
        True,
        (255, 50, 50)
    )

    score_text = small_font.render(
        "Final Score: " + str(score),
        True,
        (255, 255, 255)
    )

    restart_text = small_font.render(
        "Press R to Restart or Q to Quit",
        True,
        (255, 255, 255)
    )

    screen.blit(
        text,
        (
            SCREEN_WIDTH // 2 - text.get_width() // 2,
            200
        )
    )

    screen.blit(
        score_text,
        (
            SCREEN_WIDTH // 2 - score_text.get_width() // 2,
            280
        )
    )

    screen.blit(
        restart_text,
        (
            SCREEN_WIDTH // 2 - restart_text.get_width() // 2,
            350
        )
    )

    pygame.display.flip()


# ---------------------------------------------------------
# MAIN GAME
# ---------------------------------------------------------

def main():

    pygame.init()

    screen = pygame.display.set_mode(
        (SCREEN_WIDTH, SCREEN_HEIGHT)
    )

    pygame.display.set_caption("Zombie Decision Game")

    clock = pygame.time.Clock()

    player = create_player()

    bullets = []
    zombies = []
    powerups = []

    score = 0
    level = 1

    running = True
    game_active = True

    zombie_timer = 0
    powerup_timer = 0

    while running:
        #----------------------------------------------
        # IMPLEMENT IMAGES
        #-----------------------------------------------
        screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Zombie Apocolypse!!")

images = load_all_images()   # add this line

        # -------------------------------------------------
        # EVENTS
        # -------------------------------------------------

        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.MOUSEBUTTONDOWN:

                if event.button == 1 and game_active:

                    mouse_x, mouse_y = pygame.mouse.get_pos()

                    bullet = shoot(
                        player,
                        mouse_x,
                        mouse_y
                    )

                    if bullet is not None:
                        bullets.append(bullet)

        # -------------------------------------------------
        # ACTIVE GAME
        # -------------------------------------------------

        if game_active:

            move_player(player)

            # Create zombies
            zombie_timer += 1

            spawn_rate = max(15, 60 - (level * 5))

            if zombie_timer >= spawn_rate:

                zombies.append(
                    spawn_zombie(level)
                )

                zombie_timer = 0

            # Create health packages
            powerup_timer += 1

            if powerup_timer >= 600:

                powerups.append(
                    spawn_health_package()
                )

                powerup_timer = 0

            # Update objects
            move_bullets(bullets)
            remove_old_bullets(bullets)

            move_zombies(zombies, player)

            # Check collisions
            score += check_bullet_hits(
                bullets,
                zombies
            )

            check_zombie_attacks(
                player,
                zombies
            )

            check_powerup_collection(
                player,
                powerups
            )

            # Update difficulty
            level = update_level(score)

            # Check death
            if player["health"] <= 0:

                game_active = False

            # Draw game
            draw_game(
                screen,
                player,
                bullets,
                zombies,
                powerups,
                score,
                level
            )

            pygame.display.flip()

        # -------------------------------------------------
        # GAME OVER
        # -------------------------------------------------

        else:

            game_over(screen, score)

            keys = pygame.key.get_pressed()

            if keys[pygame.K_r]:

                player = create_player()

                bullets = []
                zombies = []
                powerups = []

                score = 0
                level = 1

                zombie_timer = 0
                powerup_timer = 0

                game_active = True

            if keys[pygame.K_q]:

                running = False

        clock.tick(60)

    pygame.quit()


# ---------------------------------------------------------
# RUN PROGRAM
# ---------------------------------------------------------

if __name__ == "__main__":
    main()
   

