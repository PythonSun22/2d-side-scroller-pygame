from __future__ import annotations

import pygame

from game.assets import assets
from game.mob_tuning import MobTuning


class Mob:
    """
    Basic animated ground mob.

    Physics remains in world coordinates. Rendering uses interpolated
    positions and a stable foot anchor.
    """

    WALK_IMAGES = (
        "mob/mob_walk_death_1.png",
        "mob/mob_walk_death_2.png",
    )

    DEATH_IMAGE = "mob/mob_walk_death_3.png"

    def __init__(
        self,
        position: tuple[float, float],
        patrol_left: float,
        patrol_right: float,
    ) -> None:
        if patrol_right <= patrol_left:
            raise ValueError(
                "patrol_right must be greater than patrol_left."
            )

        self.walk_frames = [
            assets.load_image(filename, alpha=True)
            for filename in self.WALK_IMAGES
        ]

        self.death_image = assets.load_image(
            self.DEATH_IMAGE,
            alpha=True,
        )

        self.current_frame = 0
        self.image = self.walk_frames[self.current_frame]

        self.feet_x = float(position[0])
        self.feet_y = float(position[1])

        self.previous_feet_x = self.feet_x
        self.previous_feet_y = self.feet_y

        self.patrol_left = float(patrol_left)
        self.patrol_right = float(patrol_right)

        self.direction = 1
        self.facing_right = True

        self.animation_elapsed = 0.0

        self.collision_rect = pygame.Rect(
            0,
            0,
            MobTuning.HITBOX_WIDTH,
            MobTuning.HITBOX_HEIGHT,
        )

        self._synchronize_collision_rect()

    def begin_physics_step(self) -> None:
        self.previous_feet_x = self.feet_x
        self.previous_feet_y = self.feet_y

    def update(self, delta_time: float) -> None:
        self._update_patrol(delta_time)
        self._update_animation(delta_time)
        self._synchronize_collision_rect()

    def _update_patrol(self, delta_time: float) -> None:
        self.feet_x += (
            self.direction
            * MobTuning.PATROL_SPEED
            * delta_time
        )

        if self.feet_x >= self.patrol_right:
            self.feet_x = self.patrol_right
            self.direction = -1
            self.facing_right = False

        elif self.feet_x <= self.patrol_left:
            self.feet_x = self.patrol_left
            self.direction = 1
            self.facing_right = True

    def _update_animation(self, delta_time: float) -> None:
        self.animation_elapsed += delta_time

        while (
            self.animation_elapsed
            >= MobTuning.ANIMATION_INTERVAL
        ):
            self.animation_elapsed -= (
                MobTuning.ANIMATION_INTERVAL
            )

            self.current_frame = (
                self.current_frame + 1
            ) % len(self.walk_frames)

        frame = self.walk_frames[self.current_frame]

        if self.facing_right:
            self.image = pygame.transform.flip(
                frame,
                True,
                False,
            )
        else:
            self.image = frame

    def _synchronize_collision_rect(self) -> None:
        self.collision_rect.midbottom = (
            round(self.feet_x),
            round(
                self.feet_y
                - MobTuning.HITBOX_VERTICAL_OFFSET
            ),
        )

    def get_interpolated_feet_position(
        self,
        alpha: float,
    ) -> tuple[float, float]:
        render_x = (
            self.previous_feet_x
            + (self.feet_x - self.previous_feet_x) * alpha
        )

        render_y = (
            self.previous_feet_y
            + (self.feet_y - self.previous_feet_y) * alpha
        )

        return render_x, render_y

    def render(
        self,
        screen: pygame.Surface,
        camera_x: float,
        alpha: float,
    ) -> None:
        render_x, render_y = (
            self.get_interpolated_feet_position(alpha)
        )

        render_rect = self.image.get_rect(
            midbottom=(
                round(render_x - camera_x),
                round(
                    render_y
                    + MobTuning.IMAGE_VERTICAL_OFFSET
                ),
            )
        )

        screen.blit(
            self.image,
            render_rect,
        )

    def render_debug_hitbox(
        self,
        screen: pygame.Surface,
        camera_x: float,
        alpha: float,
    ) -> None:
        render_x, render_y = (
            self.get_interpolated_feet_position(alpha)
        )

        debug_rect = pygame.Rect(
            0,
            0,
            MobTuning.HITBOX_WIDTH,
            MobTuning.HITBOX_HEIGHT,
        )

        debug_rect.midbottom = (
            round(render_x - camera_x),
            round(
                render_y
                - MobTuning.HITBOX_VERTICAL_OFFSET
            ),
        )

        pygame.draw.rect(
            screen,
            MobTuning.DEBUG_COLOR,
            debug_rect,
            width=2,
        )