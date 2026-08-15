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

    FULL_HEALTH_IMAGES = (
        "boss/boss.png",
        "boss/boss_2.png",
    )

    HALF_HEALTH_IMAGES = (
        "boss/boss_half_health.png",
        "boss/boss_half_health_2.png",
    )

    NEAR_DEATH_IMAGES = (
        "boss/boss_near_death.png",
        "boss/boss_near_death_2.png",
    )

    DEATH_IMAGES = (
        "boss/boss_death.png",
        "boss/boss_death_2.png",
    )

    def __init__(
        self,
        position: tuple[float, float],
        arena_left: float,
        arena_right: float,
    ) -> None:
        self.full_health_frames = self._load_frames(
            self.FULL_HEALTH_IMAGES
        )

        self.half_health_frames = self._load_frames(
            self.HALF_HEALTH_IMAGES
        )

        self.near_death_frames = self._load_frames(
            self.NEAR_DEATH_IMAGES
        )

        self.death_frames = self._load_frames(
            self.DEATH_IMAGES
        )

        self.frames = self.full_health_frames
        self.health = BossTuning.MAX_HEALTH
        self.should_remove = False

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

        self.velocity_y = 0.0
        self.is_on_ground = True
        self.ground_y = float(position[1])

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
        self.is_on_platform = False

        self.hit_flash_timer = 0.0
        self.stagger_timer = 0.0
        self.knockback_velocity_x = 0.0

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
        platforms: list,
    ) -> None:
        # Update visual hit feedback timer.
        self.hit_flash_timer = max(
            0.0,
            self.hit_flash_timer - delta_time,
        )

        # ---------------------------------------------------------
        # STAGGER / SWORD HIT REACTION
        # ---------------------------------------------------------

        if self.stagger_timer > 0.0:
            self.stagger_timer = max(
                0.0,
                self.stagger_timer - delta_time,
            )

            # Briefly push the boss backward instead of allowing
            # its AI state to move normally.
            self.feet_x += (
                self.knockback_velocity_x
                * delta_time
            )

            # Gradually reduce knockback momentum.
            self.knockback_velocity_x *= 0.82

            self.clamp_to_arena()

        else:
            # Normal boss AI runs only when not staggered.
            self.state.update(
                delta_time,
                player,
            )

            # Make sure any old knockback has fully ended.
            self.knockback_velocity_x = 0.0

        # ---------------------------------------------------------
        # VERTICAL PHYSICS
        # ---------------------------------------------------------

        self._apply_vertical_physics(
            delta_time,
            platforms,
        )

        # ---------------------------------------------------------
        # ANIMATION
        # ---------------------------------------------------------

        self._update_animation(
            delta_time
        )

        # ---------------------------------------------------------
        # COLLISION RECT
        # ---------------------------------------------------------

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
        if self.is_defeated:
            self.animation_elapsed += delta_time

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

            if self.facing_right:
                self.image = pygame.transform.flip(
                    frame,
                    True,
                    False,
                )
            else:
                self.image = frame

            return

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
        forward_offset = (
            BossTuning.HITBOX_FORWARD_OFFSET
            * self.direction
        )

        self.collision_rect.midbottom = (
            round(
                self.feet_x
                + forward_offset
            ),
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
        # Match Freddy's damage feedback: briefly blink the sprite
        # on and off instead of applying a color tint.
        if self.hit_flash_timer > 0.0:
            flash_phase = int(
                self.hit_flash_timer * 12
            )

            if flash_phase % 2 == 0:
                return

        render_x, render_y = (
            self.get_interpolated_feet_position(
                alpha
            )
        )

        vertical_offset = (
            BossTuning.IMAGE_VERTICAL_OFFSET
        )

        if self.is_on_platform:
            vertical_offset += (
                BossTuning.PLATFORM_IMAGE_VERTICAL_OFFSET
            )

        rect = self.image.get_rect(
            midbottom=(
                round(
                    render_x
                    - camera_x
                ),
                round(
                    render_y
                    + vertical_offset
                ),
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
        forward_offset = (
            BossTuning.HITBOX_FORWARD_OFFSET
            * self.direction
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
                + forward_offset
            ),
            round(render_y),
        )

        pygame.draw.rect(
            screen,
            BossTuning.DEBUG_COLOR,
            debug_rect,
            width=2,
        )

    @property
    def is_defeated(self) -> bool:
        return self.health <= 0


    def take_damage(
        self,
        amount: int,
        knockback_direction: int = 0,
        knockback_speed: float = 0.0,
    ) -> bool:
        if amount <= 0 or self.is_defeated:
            return False

        self.health = max(
            0,
            self.health - amount,
        )

        self._update_health_visuals()

        if self.health <= 0:
            from game.boss_ai.death_state import DeathState

            self.change_state(
                DeathState(self)
            )

        return True

    def _update_health_visuals(self) -> None:
        if self.health <= 0:
            return

        health_ratio = (
            self.health / BossTuning.MAX_HEALTH
        )

        if health_ratio <= 0.33:
            self.frames = self.near_death_frames

        elif health_ratio <= 0.66:
            self.frames = self.half_health_frames

        else:
            self.frames = self.full_health_frames

        self.current_frame %= len(self.frames)  

    def _apply_vertical_physics(
        self,
        delta_time: float,
        platforms: list,
    ) -> None:
        previous_bottom = self.collision_rect.bottom

        self.velocity_y += (
            BossTuning.GRAVITY
            * delta_time
        )

        self.velocity_y = min(
            self.velocity_y,
            BossTuning.MAX_FALL_SPEED,
        )

        self.feet_y += (
            self.velocity_y
            * delta_time
        )

        self._synchronize_collision_rect()

        self.is_on_ground = False
        self.is_on_platform = False

        if self.velocity_y >= 0:
            for platform in platforms:
                crossed_top = (
                    previous_bottom <= platform.rect.top
                    and self.collision_rect.bottom
                    >= platform.rect.top
                )

                overlaps_x = (
                    self.collision_rect.right
                    > platform.rect.left
                    and self.collision_rect.left
                    < platform.rect.right
                )

                if crossed_top and overlaps_x:
                    self.feet_y = float(
                        platform.rect.top
                    )

                    self.velocity_y = 0.0
                    self.is_on_ground = True
                    self.is_on_platform = True

                    self._synchronize_collision_rect()
                    return

        if self.collision_rect.bottom >= self.ground_y:
            self.feet_y = self.ground_y

            self.velocity_y = 0.0
            self.is_on_ground = True
            self.is_on_platform = False

            self._synchronize_collision_rect()

    def _load_frames(
        self,
        filenames: tuple[str, ...],
    ) -> list[pygame.Surface]:
        frames = []

        for filename in filenames:
            image = assets.load_image(
                filename,
                alpha=True,
            )

            width = round(
                image.get_width()
                * BossTuning.SPRITE_SCALE
            )

            height = round(
                image.get_height()
                * BossTuning.SPRITE_SCALE
            )

            image = pygame.transform.scale(
                image,
                (width, height),
            )

            frames.append(image)

        return frames

    def receive_sword_hit(
        self,
        amount: int,
        direction: int,
    ) -> bool:
        if not self.take_damage(amount):
            return False

        self.hit_flash_timer = (
            BossTuning.SWORD_HIT_FLASH_DURATION
        )

        self.stagger_timer = (
            BossTuning.SWORD_HIT_STAGGER_DURATION
        )

        self.knockback_velocity_x = (
            direction
            * BossTuning.SWORD_HIT_KNOCKBACK_SPEED
        )

        return True


    def receive_fireball_hit(
        self,
        amount: int,
    ) -> bool:
        if not self.take_damage(amount):
            return False

        self.hit_flash_timer = (
            BossTuning.FIREBALL_HIT_FLASH_DURATION
        )

        return True