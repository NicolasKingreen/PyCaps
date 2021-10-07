import random

import pygame
from pygame.locals import *

Vector = pygame.math.Vector2

pygame.font.init()
FONT = pygame.font.SysFont(None, 16)
DRAW_DEBUG = False

CAPS_SPAWNED = 4


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
    MAX_SPEED = 750

    def __init__(self):
        self.coordinates = get_random_coordinates()
        self.moving_direction = get_random_direction()
        self.speed = Cap.get_random_speed()
        self.acceleration = Cap.ACCELERATION
        self.color = get_random_color()
        self.radius = Cap.get_random_radius()
        self.mass = self.radius / 8

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
        return f"Cap({x}, {y})"

    def update(self, frame_time_s):
        self.speed += self.acceleration * frame_time_s
        if self.speed < 0:
            self.speed = 0
            self.acceleration = 0
        elif self.speed > 0:
            self.acceleration = Cap.ACCELERATION
        if self.speed > Cap.MAX_SPEED:
            self.speed = Cap.MAX_SPEED
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

    def draw(self, surface, frame_time_s):
        pygame.draw.circle(surface, self.color, self.coordinates, self.radius)
        if DRAW_DEBUG:
            text_surf = FONT.render(f"Circle({self.mass})", True, (255, 0, 0))
            text_rect = text_surf.get_rect(center=(self.coordinates.x, self.coordinates.y - self.radius - 10))
            pygame.draw.circle(surface, (255, 0, 0), self.coordinates, self.radius, 1)
            pygame.draw.line(surface, (255, 0, 0), self.coordinates, self.coordinates + self.moving_direction * self.speed * frame_time_s)
            surface.blit(text_surf, text_rect)

    def distance_to(self, other_cap):
        return self.coordinates.distance_to(other_cap.coordinates)

    def collides(self, other_cap):
        return self.distance_to(other_cap) < self.radius + other_cap.radius

    @staticmethod
    def get_random_radius():
        radius = random.randint(16, 128)
        return radius

    @staticmethod
    def get_random_speed():
        speed = random.randint(300, 500)
        return speed


class Window:

    # WIDTH, HEIGHT = DIMENSIONS = (640, 360)
    WIDTH, HEIGHT = DIMENSIONS = (1280, 720)
    # WIDTH, HEIGHT = DIMENSIONS = (1920, 1080)

    def __init__(self):
        self.full_screen = False
        self._surface = pygame.display.set_mode(Window.DIMENSIONS)
        pygame.display.set_caption("Caps Game")

    def get_surface(self):
        return self._surface

    def toggle_fullscreen(self):
        pygame.display.toggle_fullscreen()


class CapsGame:

    MAX_FPS = 60

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
                for cap1 in self.caps:
                    for cap2 in self.caps:
                        if cap1 is not cap2:
                            if cap1.collides(cap2):

                                # TODO: process still caps

                                # cap2.coordinates = cap1.coordinates.

                                # mass_ratio = cap1.mass / cap2.mass
                                #
                                # new_vel_x1 = (cap1.moving_direction.x * cap1.speed * (cap1.mass - cap2.mass) + (2 * cap2.mass * cap2.moving_direction.x * cap2.speed))/(cap1.mass + cap2.mass)
                                # new_vel_x1 /= mass_ratio
                                # new_vel_y1 = (cap1.moving_direction.y * cap1.speed * (cap1.mass - cap2.mass) + (2 * cap2.mass * cap2.moving_direction.y * cap2.speed))/(cap1.mass + cap2.mass)
                                # new_vel_y1 /= mass_ratio
                                # new_vel_x2 = (cap2.moving_direction.x * cap1.speed * (cap2.mass - cap1.mass) + (2 * cap1.mass * cap1.moving_direction.x * cap1.speed))/(cap1.mass + cap2.mass)
                                # new_vel_x2 *= mass_ratio
                                # new_vel_y2 = (cap2.moving_direction.y * cap1.speed * (cap2.mass - cap1.mass) + (2 * cap1.mass * cap1.moving_direction.y * cap1.speed))/(cap1.mass + cap2.mass)
                                # new_vel_y2 *= mass_ratio
                                # velocity_vector1 = Vector(new_vel_x1, new_vel_y1)
                                # velocity_vector2 = Vector(new_vel_x2, new_vel_y2)
                                # new_speed1 = velocity_vector1.magnitude()
                                # new_speed2 = velocity_vector2.magnitude()
                                # if velocity_vector1:
                                #     velocity_vector1.normalize_ip()
                                # if velocity_vector2:
                                #     velocity_vector2.normalize_ip()
                                # cap1.moving_direction = velocity_vector1
                                # cap2.moving_direction = velocity_vector2
                                # cap1.speed = new_speed1
                                # cap2.speed = new_speed2
                                # cap1.coordinates += cap1.moving_direction * cap1.speed * frame_time_s
                                # cap2.coordinates += cap2.moving_direction * cap2.speed * frame_time_s

                                cap1_old_md = cap1.moving_direction
                                cap2_old_md = cap2.moving_direction

                                cap1.moving_direction.reflect_ip(cap2_old_md)
                                cap1.coordinates += cap1.moving_direction * cap1.speed * frame_time_s * 2
                                # cap1.moving_direction.reflect_ip(cap1_old_md)

                                cap1.color = get_random_color()

            # graphics
            self._draw_graphics(frame_time_s)

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
                elif event.key == K_f:
                    self.window.toggle_fullscreen()
                elif event.key == K_a:
                    self.caps.append(Cap())
            elif event.type == MOUSEBUTTONDOWN:
                if event.button == 1:
                    mouse_x, mouse_y = pygame.mouse.get_pos()
                    mouse_coordinates = Vector(mouse_x, mouse_y)
                    for cap in self.caps:
                        new_direction_vector = -(mouse_coordinates - cap.coordinates)
                        new_direction_vector.normalize_ip()
                        cap.moving_direction = new_direction_vector
                        cap.speed += min(1., 50/mouse_coordinates.distance_to(cap.coordinates)) * 250
                elif event.button == 3:
                    mouse_x, mouse_y = pygame.mouse.get_pos()
                    mouse_coordinates = Vector(mouse_x, mouse_y)
                    for cap in self.caps:
                        new_direction_vector = mouse_coordinates - cap.coordinates
                        new_direction_vector.normalize_ip()
                        cap.moving_direction = new_direction_vector
                        cap.speed += min(1., 50/mouse_coordinates.distance_to(cap.coordinates)) * 250

    def _draw_graphics(self, frame_time_s):
        render_surface = self.window.get_surface()
        render_surface.fill(pygame.Color("white"))
        for cap in self.caps:
            cap.draw(render_surface, frame_time_s)
        if DRAW_DEBUG:
            draw_text(str(self.caps), topleft=(10, 10))
            draw_text(f"{self.get_current_fps()} FPS", topleft=(10, 26))
        if self.is_paused:
            draw_text("Game is paused", center=(Window.WIDTH // 2, Window.HEIGHT // 2))
        pygame.display.update()

    def stop(self):
        self.is_running = False


if __name__ == "__main__":
    CapsGame().run()
