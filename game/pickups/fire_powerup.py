from __future__ import annotations

import math

import pygame

from game.assets import assets


class FirePowerUp:
    """
    Collectible that grants Freddy his fire-powered form.

    Position and collision live in world space.
    """

    IMAGE_PATH = "fireball.png"

    SIZE = 34

    BOB_HEIGHT = 6.0
    BOB_SPEED = 4.0

    ROTATION_SPEED = 300.0

    def __init__(
        self,
        position: tuple[float, float],
    ) -> None:
        image = assets.load_image(
            self.IMAGE_PATH,
            alpha=True,
        )

        self.base_image = pygame.transform.scale(
            image,
            (self.SIZE, self.SIZE),
        )

        self.center_x = float(position[0])
        self.base_center_y = float(position[1])

        self.center_y = self.base_center_y
        self.previous_center_y = self.center_y

        self.elapsed = 0.0
        self.collected = False

        self.collision_rect = pygame.Rect(
            0,
            0,
            30,
            30,
        )

        self._synchronize_collision_rect()

    def begin_physics_step(self) -> None:
        self.previous_center_y = self.center_y

    def update(self, delta_time: float) -> None:
        if self.collected:
            return

        self.elapsed += delta_time

        self.center_y = (
            self.base_center_y
            + math.sin(
                self.elapsed * self.BOB_SPEED
            )
            * self.BOB_HEIGHT
        )

        self._synchronize_collision_rect()

    def _synchronize_collision_rect(self) -> None:
        self.collision_rect.center = (
            round(self.center_x),
            round(self.center_y),
        )

    def collect(self) -> None:
        self.collected = True

    def render(
        self,
        screen: pygame.Surface,
        camera_x: float,
        alpha: float,
    ) -> None:
        if self.collected:
            return

        render_y = (
            self.previous_center_y
            + (
                self.center_y
                - self.previous_center_y
            )
            * alpha
        )

        angle = (
            -self.elapsed
            * self.ROTATION_SPEED
        ) % 360.0

        image = pygame.transform.rotate(
            self.base_image,
            angle,
        )

        rect = image.get_rect(
            center=(
                round(
                    self.center_x
                    - camera_x
                ),
                round(render_y),
            )
        )

        screen.blit(
            image,
            rect,
        )

    def render_debug(
        self,
        screen: pygame.Surface,
        camera_x: float,
    ) -> None:
        if self.collected:
            return

        debug_rect = self.collision_rect.move(
            -round(camera_x),
            0,
        )

        pygame.draw.rect(
            screen,
            (255, 140, 0),
            debug_rect,
            width=2,
        )