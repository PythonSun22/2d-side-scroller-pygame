from __future__ import annotations

import pygame

from game.assets import assets
from game.boss_ai.boss_state import BossState
from game.boss_ai.dormant_state import DormantState
from game.boss_tuning import BossTuning


class Boss:
    """
    Main FreddyWorld boss.

    This initial vertical slice supports:
    Dormant -> Stalk -> Charge -> Recovery.
    """

    WALK_IMAGES = (
        "boss/boss.png",
        "boss/boss_2.png",
    )

    def __init__(
        self,
        position: tuple[float, float],
        arena_left: float,
        arena_right: float,
    ) -> None:
        self.frames = [
            assets.load_image(
                filename,
                alpha=True,
            )
            for filename in self.WALK_IMAGES
        ]

        self.current_frame = 0
        self.image = self.frames[0]

        self.animation_elapsed = 0.0

        self.feet_x = float(
            position[0]
        )

        self.feet_y = float(
            position[1]
        )

        self.previous_feet_x = self.feet_x
        self.previous_feet_y = self.feet_y

        self.arena_left = float(
            arena_left
        )

        self.arena_right = float(
            arena_right
        )

        self.direction = -1
        self.facing_right = False

        self.is_moving = False
        self.is_active = False

        self.collision_rect = pygame.Rect(
            0,
            0,
            BossTuning.HITBOX_WIDTH,
            BossTuning.HITBOX_HEIGHT,
        )

        self._state: BossState | None = None

        self._synchronize_collision_rect()

        self.change_state(
            DormantState(self)
        )

    @property
    def state(self) -> BossState:
        if self._state is None:
            raise RuntimeError(
                "Boss has no active state."
            )

        return self._state

    @property
    def state_name(self) -> str:
        return type(self.state).__name__

    def change_state(
        self,
        new_state: BossState,
    ) -> None:
        if self._state is not None:
            self._state.exit()

        self._state = new_state
        self._state.enter()

    def activate(self) -> None:
        if self.is_active:
            return

        self.is_active = True

        from game.boss_ai.stalk_state import (
            StalkState,
        )

        self.change_state(
            StalkState(self)
        )

    def begin_physics_step(self) -> None:
        self.previous_feet_x = self.feet_x
        self.previous_feet_y = self.feet_y

    def update(
        self,
        delta_time: float,
        player,
    ) -> None:
        self.state.update(
            delta_time,
            player,
        )

        self._update_animation(
            delta_time
        )

        self._synchronize_collision_rect()

    def set_direction(
        self,
        direction: int,
    ) -> None:
        if direction == 0:
            return

        self.direction = (
            1 if direction > 0 else -1
        )

        self.facing_right = (
            self.direction > 0
        )

    def face_world_x(
        self,
        target_x: float,
    ) -> None:
        if target_x > self.feet_x:
            self.set_direction(1)

        elif target_x < self.feet_x:
            self.set_direction(-1)

    def clamp_to_arena(self) -> bool:
        """
        Keep the boss inside the arena.

        Returns True if a boundary was reached.
        """
        half_width = (
            BossTuning.HITBOX_WIDTH
            / 2
        )

        minimum_x = (
            self.arena_left
            + half_width
        )

        maximum_x = (
            self.arena_right
            - half_width
        )

        if self.feet_x < minimum_x:
            self.feet_x = minimum_x
            return True

        if self.feet_x > maximum_x:
            self.feet_x = maximum_x
            return True

        return False

    def _update_animation(
        self,
        delta_time: float,
    ) -> None:
        if not self.is_moving:
            self.current_frame = 0
            self.animation_elapsed = 0.0

        else:
            self.animation_elapsed += (
                delta_time
            )

            while (
                self.animation_elapsed
                >= BossTuning.ANIMATION_INTERVAL
            ):
                self.animation_elapsed -= (
                    BossTuning.ANIMATION_INTERVAL
                )

                self.current_frame = (
                    self.current_frame + 1
                ) % len(self.frames)

        frame = self.frames[
            self.current_frame
        ]

        # If the source art faces the wrong direction,
        # reverse this condition exactly as we did with Mob.
        if self.facing_right:
            self.image = pygame.transform.flip(
                frame,
                True,
                False,
            )
        else:
            self.image = frame

    def _synchronize_collision_rect(
        self,
    ) -> None:
        self.collision_rect.midbottom = (
            round(self.feet_x),
            round(self.feet_y),
        )

    def get_interpolated_feet_position(
        self,
        alpha: float,
    ) -> tuple[float, float]:
        render_x = (
            self.previous_feet_x
            + (
                self.feet_x
                - self.previous_feet_x
            )
            * alpha
        )

        render_y = (
            self.previous_feet_y
            + (
                self.feet_y
                - self.previous_feet_y
            )
            * alpha
        )

        return render_x, render_y

    def render(
        self,
        screen: pygame.Surface,
        camera_x: float,
        alpha: float,
    ) -> None:
        render_x, render_y = (
            self.get_interpolated_feet_position(
                alpha
            )
        )

        rect = self.image.get_rect(
            midbottom=(
                round(
                    render_x
                    - camera_x
                ),
                round(render_y),
            )
        )

        screen.blit(
            self.image,
            rect,
        )

    def render_debug_hitbox(
        self,
        screen: pygame.Surface,
        camera_x: float,
        alpha: float,
    ) -> None:
        render_x, render_y = (
            self.get_interpolated_feet_position(
                alpha
            )
        )

        debug_rect = pygame.Rect(
            0,
            0,
            BossTuning.HITBOX_WIDTH,
            BossTuning.HITBOX_HEIGHT,
        )

        debug_rect.midbottom = (
            round(
                render_x
                - camera_x
            ),
            round(render_y),
        )

        pygame.draw.rect(
            screen,
            BossTuning.DEBUG_COLOR,
            debug_rect,
            width=2,
        )