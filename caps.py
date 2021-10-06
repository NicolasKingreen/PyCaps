import random

import pygame
from pygame.locals import *

Vector = pygame.math.Vector2

pygame.font.init()
FONT = pygame.font.SysFont(None, 16)
DRAW_DEBUG = False

CAPS_SPAWNED = 120


def draw_text(text, topleft=None, center=None):
    text_surface = FONT.render(text, True, (0, 0, 0))
    if topleft:
        text_rect = text_surface.get_rect(topleft=topleft)
    elif center:
        text_rect = text_surface.get_rect(center=center)
    else:
        text_rect = text_surface.get_rect()
    render_surface = pygame.display.get_surface()
    render_surface.blit(text_surface, text_rect)


def get_random_coordinates():
    x = random.randint(0, Window.WIDTH)
    y = random.randint(0, Window.HEIGHT)
    coordinates_vector = Vector(x, y)
    return coordinates_vector


def get_random_direction():
    x = random.random() * 2 - 1
    y = random.random() * 2 - 1
    direction_vector = Vector(x, y)
    direction_vector.normalize_ip()
    return direction_vector


def get_random_color():
    r = random.randint(0, 255)
    g = random.randint(0, 255)
    b = random.randint(0, 255)
    color = pygame.Color(r, g, b)
    return color


class Cap:

    ACCELERATION = -100

    def __init__(self):
        self.coordinates = get_random_coordinates()
        self.moving_direction = get_random_direction()
        self.speed = Cap.get_random_speed()
        self.acceleration = Cap.ACCELERATION
        self.color = get_random_color()
        self.radius = Cap.get_random_radius()

    def __str__(self):
        return f"Cap: \n" \
               f"->color={self.color}\n" \
               f"->radius={self.radius}\n" \
               f"->coordinates={self.coordinates}\n" \
               f"->moving_direction={self.moving_direction}\n" \
               f"->speed={self.speed}\n"

    def __repr__(self):
        x = int(self.coordinates.x)
        y = int(self.coordinates.y)
        dx = self.moving_direction.x
        dy = self.moving_direction.y
        return f"Cap({x}, {y})({dx:.2f}, {dy:.2f})"

    def update(self, frame_time_s):
        self.speed += self.acceleration * frame_time_s
        if self.speed < 0:
            self.speed = 0
            self.acceleration = 0
        elif self.speed > 0:
            self.acceleration = Cap.ACCELERATION
        self.coordinates += self.moving_direction * self.speed * frame_time_s
        # x borders
        if self.coordinates.x < self.radius:
            self.coordinates.x = self.radius
            self.moving_direction.x *= -1
        elif self.coordinates.x > Window.WIDTH - self.radius:
            self.coordinates.x = Window.WIDTH - self.radius
            self.moving_direction.x *= -1
        # y borders
        if self.coordinates.y < self.radius:
            self.coordinates.y = self.radius
            self.moving_direction.y *= -1
        elif self.coordinates.y > Window.HEIGHT - self.radius:
            self.coordinates.y = Window.HEIGHT - self.radius
            self.moving_direction.y *= -1

    def draw(self, surface):
        pygame.draw.circle(surface, self.color, self.coordinates, self.radius)
        if DRAW_DEBUG:
            pygame.draw.circle(surface, (255, 0, 0), self.coordinates, self.radius, 1)
            pygame.draw.line(surface, (255, 0, 0), self.coordinates, self.coordinates + self.moving_direction * self.speed / 4)

    def distance_to(self, other_cap):
        return self.coordinates.distance_to(other_cap.coordinates)

    def collides(self, other_cap):
        return self.distance_to(other_cap) < self.radius + other_cap.radius

    @staticmethod
    def get_random_radius():
        radius = random.randint(16, 32)
        return radius

    @staticmethod
    def get_random_speed():
        speed = random.randint(100, 300)
        return speed


class Window:

    WIDTH, HEIGHT = DIMENSIONS = (1280, 720)

    def __init__(self):
        self._surface = pygame.display.set_mode(Window.DIMENSIONS)
        pygame.display.set_caption("Caps Game")

    def get_surface(self):
        return self._surface


class CapsGame:

    MAX_FPS = 120

    def __init__(self):
        self.clock = pygame.time.Clock()
        self.window = Window()

        self.caps = []
        for _ in range(CAPS_SPAWNED):
            self.caps.append(Cap())

        self.is_running = False
        self.is_paused = False

    def run(self):
        global DRAW_DEBUG
        self.is_running = True
        while self.is_running:

            # logic
            frame_time_ms = self.clock.tick(CapsGame.MAX_FPS)
            frame_time_s = frame_time_ms / 1000.
            current_fps = self.clock.get_fps()

            self._handle_events()

            # states update
            if not self.is_paused:
                for cap in self.caps:
                    cap.update(frame_time_s)

            # caps collision
            # for cap1 in self.caps:
            #     for cap2 in self.caps:
            #         if cap1 is not cap2:
            #             if cap1.collides(cap2):
            #                 cap1.moving_direction *= -1
            #                 # cap1.moving_direction = cap1.moving_direction.cross(cap2.moving_direction)
            #                 # cap1.moving_direction.normalize_ip()

            # graphics
            self._draw_graphics()

    def get_current_fps(self):
        return int(self.clock.get_fps())

    def _handle_events(self):
        global DRAW_DEBUG
        for event in pygame.event.get():
            if event.type == QUIT:
                self.stop()
            elif event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    self.stop()
                elif event.key == K_SPACE:
                    self.is_paused = not self.is_paused
                elif event.key == K_d:
                    DRAW_DEBUG = not DRAW_DEBUG
            elif event.type == MOUSEBUTTONDOWN:
                if event.button == 1:
                    mouse_x, mouse_y = pygame.mouse.get_pos()
                    mouse_coordinates = Vector(mouse_x, mouse_y)
                    for cap in self.caps:
                        new_direction_vector = -(mouse_coordinates - cap.coordinates)
                        new_direction_vector.normalize_ip()
                        cap.moving_direction = new_direction_vector
                        cap.speed = 500
                elif event.button == 3:
                    mouse_x, mouse_y = pygame.mouse.get_pos()
                    mouse_coordinates = Vector(mouse_x, mouse_y)
                    for cap in self.caps:
                        new_direction_vector = mouse_coordinates - cap.coordinates
                        new_direction_vector.normalize_ip()
                        cap.moving_direction = new_direction_vector
                        cap.speed = 500

    def _draw_graphics(self):
        render_surface = self.window.get_surface()
        render_surface.fill(pygame.Color("white"))
        for cap in self.caps:
            cap.draw(render_surface)
        if DRAW_DEBUG:
            draw_text(str(self.caps), topleft=(10, 10))
            draw_text(str(self.get_current_fps()), topleft=(10, 26))
        if self.is_paused:
            draw_text("Game is paused", center=(Window.WIDTH // 2, Window.HEIGHT // 2))
        pygame.display.update()

    def stop(self):
        self.is_running = False


if __name__ == "__main__":
    CapsGame().run()
