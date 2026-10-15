"""Neon Grid Runner — a neon-style arcade game built with Pygame."""
from __future__ import annotations
import math
import random
import pygame
from dataclasses import dataclass

SCREEN_WIDTH, SCREEN_HEIGHT = 900, 600
FPS = 60
PLAYER_SIZE = 22
PLAYER_SPEED = 270.0  # pixels per second
DASH_SPEED = 650.0
DASH_DURATION = 0.13
DASH_COOLDOWN = 1.0
ROUND_DURATION = 60.0
BG = (8, 11, 24)
GRID = (19, 27, 48)
WHITE = (235, 244, 255)
MUTED = (130, 150, 180)
RED = (255, 55, 105)
CYAN = (50, 230, 255)
GOLD = (255, 207, 92)

@dataclass
class Target:
    x: float
    y: float
    radius: int = 10
    pulse: float = 0.0

    def position(self) -> tuple[float, float]:
        return self.x, self.y


def clamp(value: float, low: float, high: float) -> float:
    return max(low, min(value, high))


def move_point(x: float, y: float, dx: float, dy: float, speed: float, dt: float,
               width: int = SCREEN_WIDTH, height: int = SCREEN_HEIGHT,
               size: int = PLAYER_SIZE) -> tuple[float, float]:
    """Move using elapsed seconds and wrap around screen edges."""
    x += dx * speed * dt
    y += dy * speed * dt
    if x + size < 0:
        x = float(width)
    elif x > width:
        x = float(-size)
    if y + size < 0:
        y = float(height)
    elif y > height:
        y = float(-size)
    return x, y


def distance(a: tuple[float, float], b: tuple[float, float]) -> float:
    return math.hypot(a[0] - b[0], a[1] - b[1])


def target_is_collected(player_rect: pygame.Rect, target: Target) -> bool:
    """Check circle-rectangle collision between target and player."""
    closest_x = clamp(target.x, player_rect.left, player_rect.right)
    closest_y = clamp(target.y, player_rect.top, player_rect.bottom)
    return distance((closest_x, closest_y), target.position()) <= target.radius


def random_target(rng: random.Random | None = None, width: int = SCREEN_WIDTH,
                  height: int = SCREEN_HEIGHT, margin: int = 55) -> Target:
    rng = rng or random
    return Target(float(rng.randint(margin, width - margin)),
                  float(rng.randint(margin + 50, height - margin)))


class NeonGridRunner:
    def __init__(self) -> None:
        pygame.init()
        pygame.display.set_caption("NEON GRID RUNNER")
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("consolas", 20)
        self.small_font = pygame.font.SysFont("consolas", 15)
        self.title_font = pygame.font.SysFont("consolas", 42, bold=True)
        self.big_font = pygame.font.SysFont("consolas", 30, bold=True)
        self.background = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        self._build_background()
        self.reset()

    def _build_background(self) -> None:
        self.background.fill(BG)
        for x in range(0, SCREEN_WIDTH, 40):
            pygame.draw.line(self.background, GRID, (x, 0), (x, SCREEN_HEIGHT), 1)
        for y in range(0, SCREEN_HEIGHT, 40):
            pygame.draw.line(self.background, GRID, (0, y), (SCREEN_WIDTH, y), 1)
        pygame.draw.line(self.background, (26, 42, 65), (SCREEN_WIDTH // 2, 0),
                         (SCREEN_WIDTH // 2, SCREEN_HEIGHT), 1)
        pygame.draw.line(self.background, (26, 42, 65), (0, SCREEN_HEIGHT // 2),
                         (SCREEN_WIDTH, SCREEN_HEIGHT // 2), 1)

    def reset(self) -> None:
        self.player = pygame.Vector2(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2)
        self.score = 0
        self.elapsed = 0.0
        self.time_left = ROUND_DURATION
        self.target = random_target()
        self.trails: list[tuple[float, float, float]] = []
        self.particles: list[dict[str, float | int]] = []
        self.dash_timer = 0.0
        self.dash_cooldown = 0.0
        self.paused = False
        self.game_over = False

    def _spawn_burst(self, x: float, y: float) -> None:
        for _ in range(18):
            angle, speed = random.uniform(0, math.tau), random.uniform(50, 220)
            self.particles.append({"x": x, "y": y, "vx": math.cos(angle) * speed,
                "vy": math.sin(angle) * speed, "life": random.uniform(.25, .65),
                "max_life": .65, "size": random.randint(2, 4)})

    def _update_particles(self, dt: float) -> None:
        for p in self.particles[:]:
            p["x"] = float(p["x"]) + float(p["vx"]) * dt
            p["y"] = float(p["y"]) + float(p["vy"]) * dt
            p["life"] = float(p["life"]) - dt
            if float(p["life"]) <= 0:
                self.particles.remove(p)

    def _handle_events(self) -> bool:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return False
                if event.key == pygame.K_p and not self.game_over:
                    self.paused = not self.paused
                elif event.key == pygame.K_r and self.game_over:
                    self.reset()
                elif event.key == pygame.K_SPACE and not self.paused and not self.game_over:
                    if self.dash_cooldown <= 0:
                        self.dash_timer = DASH_DURATION
                        self.dash_cooldown = DASH_COOLDOWN
        return True

    def _update(self, dt: float) -> None:
        if self.paused or self.game_over:
            return
        self.elapsed += dt
        self.time_left = max(0.0, ROUND_DURATION - self.elapsed)
        self.dash_timer = max(0.0, self.dash_timer - dt)
        self.dash_cooldown = max(0.0, self.dash_cooldown - dt)
        self.target.pulse += dt * 5
        keys = pygame.key.get_pressed()
        direction = pygame.Vector2(
            float(keys[pygame.K_RIGHT] or keys[pygame.K_d]) - float(keys[pygame.K_LEFT] or keys[pygame.K_a]),
            float(keys[pygame.K_DOWN] or keys[pygame.K_s]) - float(keys[pygame.K_UP] or keys[pygame.K_w]))
        if direction.length_squared() > 0:
            direction = direction.normalize()
        speed = DASH_SPEED if self.dash_timer > 0 else PLAYER_SPEED
        self.player.x, self.player.y = move_point(self.player.x, self.player.y,
            direction.x, direction.y, speed, dt)
        self.trails.append((self.player.x + PLAYER_SIZE / 2, self.player.y + PLAYER_SIZE / 2, .45))
        self.trails = [(x, y, life - dt) for x, y, life in self.trails if life - dt > 0]
        self._update_particles(dt)
        rect = pygame.Rect(round(self.player.x), round(self.player.y), PLAYER_SIZE, PLAYER_SIZE)
        if target_is_collected(rect, self.target):
            self.score += 1
            self._spawn_burst(self.target.x, self.target.y)
            self.target = random_target()
        if self.time_left <= 0:
            self.game_over = True

    def _glow_circle(self, color: tuple[int, int, int], center: tuple[int, int], radius: int) -> None:
        x, y = center
        for extra, alpha in ((12, 18), (8, 25), (4, 40)):
            size = (radius + extra) * 2
            glow = pygame.Surface((size, size), pygame.SRCALPHA)
            pygame.draw.circle(glow, (*color, alpha), (size // 2, size // 2), radius + extra)
            self.screen.blit(glow, (x - size // 2, y - size // 2))
        pygame.draw.circle(self.screen, color, center, radius)

    def _text(self, text: str, font: pygame.font.Font, color: tuple[int, int, int],
              position: tuple[int, int], anchor: str = "topleft") -> None:
        image = font.render(text, True, color)
        rect = image.get_rect()
        setattr(rect, anchor, position)
        self.screen.blit(image, rect)

    def _draw_hud(self) -> None:
        panel = pygame.Surface((SCREEN_WIDTH, 76), pygame.SRCALPHA)
        panel.fill((4, 7, 18, 220))
        self.screen.blit(panel, (0, 0))
        self._text("NEON GRID RUNNER", self.font, WHITE, (24, 16))
        self._text("COLLECT THE CYAN CORES", self.small_font, MUTED, (25, 43))
        self._text(f"SCORE  {self.score:02d}", self.big_font, CYAN,
                   (SCREEN_WIDTH // 2, 35), "midtop")
        self._text(f"{self.time_left:04.1f}s", self.big_font,
                   RED if self.time_left <= 10 else WHITE, (SCREEN_WIDTH - 24, 16), "topright")
        bx, by, bw, bh = SCREEN_WIDTH - 194, 52, 170, 7
        pygame.draw.rect(self.screen, (35, 45, 65), (bx, by, bw, bh), border_radius=4)
        ready = 1.0 - self.dash_cooldown / DASH_COOLDOWN
        pygame.draw.rect(self.screen, CYAN, (bx, by, int(bw * clamp(ready, 0, 1)), bh), border_radius=4)
        self._text("DASH", self.small_font, MUTED, (bx - 48, by - 5))
        self._text("MOVE  WASD / ARROWS", self.small_font, MUTED, (24, SCREEN_HEIGHT - 28))
        self._text("SPACE DASH   P PAUSE   ESC QUIT", self.small_font, MUTED,
                   (SCREEN_WIDTH - 24, SCREEN_HEIGHT - 28), "topright")

    def _draw_overlay(self, title: str, subtitle: str) -> None:
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((3, 5, 15, 190))
        self.screen.blit(overlay, (0, 0))
        self._text(title, self.title_font, WHITE, (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 30), "midbottom")
        self._text(subtitle, self.font, CYAN, (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 8), "midtop")

    def _draw(self) -> None:
        self.screen.blit(self.background, (0, 0))
        for x, y, life in self.trails:
            radius = max(2, int(5 * life / .45))
            dot = pygame.Surface((radius * 2 + 2, radius * 2 + 2), pygame.SRCALPHA)
            pygame.draw.circle(dot, (*RED, int(150 * life / .45)), (radius + 1, radius + 1), radius)
            self.screen.blit(dot, (int(x - radius - 1), int(y - radius - 1)))
        r = self.target.radius + int(2 * (1 + math.sin(self.target.pulse)))
        self._glow_circle(CYAN, (int(self.target.x), int(self.target.y)), r)
        diamond = [(self.target.x, self.target.y - 17), (self.target.x + 17, self.target.y),
                   (self.target.x, self.target.y + 17), (self.target.x - 17, self.target.y)]
        pygame.draw.polygon(self.screen, (150, 250, 255), diamond, width=2)
        center = (int(self.player.x + PLAYER_SIZE / 2), int(self.player.y + PLAYER_SIZE / 2))
        self._glow_circle(RED, center, 13)
        player_rect = pygame.Rect(round(self.player.x), round(self.player.y), PLAYER_SIZE, PLAYER_SIZE)
        pygame.draw.rect(self.screen, (255, 95, 130), player_rect, border_radius=5)
        pygame.draw.rect(self.screen, WHITE, player_rect, width=2, border_radius=5)
        pygame.draw.circle(self.screen, WHITE, center, 3)
        for p in self.particles:
            life = max(0.0, float(p["life"]))
            size = int(p["size"])
            surf = pygame.Surface((size * 2 + 2, size * 2 + 2), pygame.SRCALPHA)
            pygame.draw.circle(surf, (*GOLD, int(255 * life / float(p["max_life"]))),
                               (size + 1, size + 1), size)
            self.screen.blit(surf, (int(float(p["x"]) - size), int(float(p["y"]) - size)))
        self._draw_hud()
        if self.paused:
            self._draw_overlay("PAUSED", "Press P to continue")
        elif self.game_over:
            self._draw_overlay("TIME'S UP!", f"Final score: {self.score}   |   Press R to restart")
        pygame.display.flip()

    def run(self) -> None:
        running = True
        while running:
            dt = min(self.clock.tick(FPS) / 1000.0, .05)
            running = self._handle_events()
            self._update(dt)
            self._draw()
        pygame.quit()


def main() -> None:
    NeonGridRunner().run()

if __name__ == "__main__":
    main()
