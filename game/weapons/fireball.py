from __future__ import annotations

from enum import Enum, auto

import pygame

from game.assets import assets


class FireballState(Enum):
    ACTIVE = auto()
    EXPLODING = auto()
    FINISHED = auto()


class Fireball:
    """
    Freddy's powered fireball projectile.

    Uses fixed-step world-space physics and preserves the original
    bouncing/explosion behavior.
    """

    SIZE = 16

    SPEED = 300.0

    GRAVITY = 1800.0
    BOUNCE_SPEED = 420.0
    MAX_FALL_SPEED = 600.0

    ROTATION_INTERVAL = 0.10
    EXPLOSION_FRAME_DURATION = 0.08

    DAMAGE = 1
    KNOCKBACK_SPEED = 180.0

    def __init__(
        self,
        position: tuple[float, float],
        direction: int,
        ground_y: float,
    ) -> None:
        self.x = float(position[0])
        self.y = float(position[1])

        self.previous_x = self.x
        self.previous_y = self.y

        self.direction = 1 if direction >= 0 else -1

        self.velocity_x = (
            self.direction
            * self.SPEED
        )

        self.velocity_y = 0.0
        self.ground_y = float(ground_y)

        self.state = FireballState.ACTIVE

        self.animation_elapsed = 0.0
        self.current_frame = 0

        base_fire = assets.load_image(
            "fireball.png",
            alpha=True,
        )

        base_fire = pygame.transform.scale(
            base_fire,
            (self.SIZE, self.SIZE),
        )

        self.fire_frames = [
            base_fire,
            pygame.transform.rotate(base_fire, -90),
            pygame.transform.rotate(base_fire, -180),
            pygame.transform.rotate(base_fire, -270),
        ]

        self.explosion_frames = [
            assets.load_image(
                "firework0.png",
                alpha=True,
            ),
            assets.load_image(
                "firework1.png",
                alpha=True,
            ),
            assets.load_image(
                "firework2.png",
                alpha=True,
            ),
        ]

        self.collision_rect = pygame.Rect(
            0,
            0,
            self.SIZE,
            self.SIZE,
        )

        self._sync_collision_rect()

    @property
    def is_finished(self) -> bool:
        return self.state == FireballState.FINISHED

    @property
    def is_active(self) -> bool:
        return self.state == FireballState.ACTIVE

    def begin_physics_step(self) -> None:
        self.previous_x = self.x
        self.previous_y = self.y

    def update(self, delta_time: float) -> None:
        if self.state == FireballState.ACTIVE:
            self._update_active(delta_time)

        elif self.state == FireballState.EXPLODING:
            self._update_explosion(delta_time)

        self._sync_collision_rect()

    def _update_active(
        self,
        delta_time: float,
    ) -> None:
        self.x += (
            self.velocity_x
            * delta_time
        )

        self.velocity_y += (
            self.GRAVITY
            * delta_time
        )

        self.velocity_y = min(
            self.velocity_y,
            self.MAX_FALL_SPEED,
        )

        self.y += (
            self.velocity_y
            * delta_time
        )

        # Preserve the original bouncing-fireball behavior.
        if self.y + self.SIZE / 2 >= self.ground_y:
            self.y = (
                self.ground_y
                - self.SIZE / 2
            )

            self.velocity_y = -self.BOUNCE_SPEED

        self.animation_elapsed += delta_time

        while (
            self.animation_elapsed
            >= self.ROTATION_INTERVAL
        ):
            self.animation_elapsed -= (
                self.ROTATION_INTERVAL
            )

            self.current_frame = (
                self.current_frame + 1
            ) % len(self.fire_frames)

    def start_explosion(self) -> None:
        if self.state != FireballState.ACTIVE:
            return

        self.state = FireballState.EXPLODING

        self.velocity_x = 0.0
        self.velocity_y = 0.0

        self.current_frame = 0
        self.animation_elapsed = 0.0

    def _update_explosion(
        self,
        delta_time: float,
    ) -> None:
        self.animation_elapsed += delta_time

        while (
            self.animation_elapsed
            >= self.EXPLOSION_FRAME_DURATION
        ):
            self.animation_elapsed -= (
                self.EXPLOSION_FRAME_DURATION
            )

            self.current_frame += 1

            if self.current_frame >= len(
                self.explosion_frames
            ):
                self.state = FireballState.FINISHED
                return

    def _sync_collision_rect(self) -> None:
        self.collision_rect.center = (
            round(self.x),
            round(self.y),
        )

    def render(
        self,
        screen: pygame.Surface,
        camera_x: float,
        alpha: float,
    ) -> None:
        if self.state == FireballState.FINISHED:
            return

        render_x = (
            self.previous_x
            + (self.x - self.previous_x)
            * alpha
        )

        render_y = (
            self.previous_y
            + (self.y - self.previous_y)
            * alpha
        )

        if self.state == FireballState.ACTIVE:
            image = self.fire_frames[
                self.current_frame
            ]

        else:
            frame_index = min(
                self.current_frame,
                len(self.explosion_frames) - 1,
            )

            image = self.explosion_frames[
                frame_index
            ]

        rect = image.get_rect(
            center=(
                round(render_x - camera_x),
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
        if not self.is_active:
            return

        debug_rect = self.collision_rect.move(
            -round(camera_x),
            0,
        )

        pygame.draw.rect(
            screen,
            (255, 110, 0),
            debug_rect,
            width=2,
        )