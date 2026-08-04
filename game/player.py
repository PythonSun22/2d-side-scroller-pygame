from __future__ import annotations

import pygame

from game.assets import assets
from game.player_tuning import PlayerTuning
from game.platform import Platform

class Player:
    """
    Freddy's movement, animation, rendering anchor, and collision box.

    Every animation frame is anchored at the same foot position, preventing
    differently sized PNG frames from visibly shifting.

    The collision box moves slightly toward Freddy's facing direction.
    """

    WALK_IMAGES = (
        "greenFreddy01.png",
        "greenFreddy02.png",
        "greenFreddy03.png",
        "greenFreddy04.png",
        "greenFreddy05.png",
    )

    def __init__(
        self,
        position: tuple[int, int],
        screen_width: int,
        ground_y: int,
    ) -> None:
        self.frames = [
            assets.load_image(filename, alpha=True)
            for filename in self.WALK_IMAGES
        ]

        self.current_frame = 0
        self.image = self.frames[self.current_frame]

        self.screen_width = screen_width
        self.ground_y = ground_y

        self.facing_right = True
        self.is_moving = False
        self.animation_elapsed = 0.0
        self.velocity_y = 0.0
        self.is_on_ground = True
        self.jump_requested = False 

        # The supplied position is the top-left position of the first frame.
        initial_rect = self.image.get_rect(topleft=position)

        # This point becomes the stable anchor for every animation frame.
        self.feet_x = float(initial_rect.centerx)
        self.feet_y = initial_rect.bottom

        self.image_rect = self.image.get_rect(
            midbottom=(round(self.feet_x), self.feet_y)
        )

        self.collision_rect = pygame.Rect(
            0,
            0,
            PlayerTuning.HITBOX_WIDTH,
            PlayerTuning.HITBOX_HEIGHT,
        )

        self._synchronize_rectangles()

    def update(self, delta_time: float, platforms: list) -> None:
        keys = pygame.key.get_pressed()

        direction = 0

        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            direction -= 1

        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            direction += 1

        self.is_moving = direction != 0

        if direction < 0:
            self.facing_right = False
        elif direction > 0:
            self.facing_right = True

        self._handle_jump()
        self._move_horizontally(direction, delta_time)
        self._apply_vertical_physics(delta_time, platforms)
        self._update_animation(delta_time)
        self._synchronize_rectangles()
        self._keep_inside_screen()

    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type != pygame.KEYDOWN:
            return

        if event.key in (pygame.K_SPACE, pygame.K_UP, pygame.K_w):
            self.jump_requested = True

    def _handle_jump(self) -> None:
        if self.jump_requested and self.is_on_ground:
            self.velocity_y = -PlayerTuning.JUMP_SPEED
            self.is_on_ground = False

        self.jump_requested = False

    def _apply_vertical_physics(
        self,
        delta_time: float,
        platforms: list,
    ) -> None:
        previous_hitbox_bottom = self.collision_rect.bottom

        self.velocity_y += (
            PlayerTuning.GRAVITY
            * delta_time
        )

        self.velocity_y = min(
            self.velocity_y,
            PlayerTuning.MAX_FALL_SPEED,
        )

        self.feet_y += (
            self.velocity_y
            * delta_time
        )

        self._synchronize_rectangles()

        self.is_on_ground = False

        # Only land while falling.
        if self.velocity_y >= 0:
            for platform in platforms:
                crossed_platform_top = (
                    previous_hitbox_bottom <= platform.rect.top
                    and self.collision_rect.bottom >= platform.rect.top
                )

                overlaps_horizontally = (
                    self.collision_rect.right > platform.rect.left
                    and self.collision_rect.left < platform.rect.right
                )

                if crossed_platform_top and overlaps_horizontally:
                    self.feet_y = (
                        platform.rect.top
                        + PlayerTuning.HITBOX_VERTICAL_OFFSET
                    )

                    self.velocity_y = 0.0
                    self.is_on_ground = True

                    self._synchronize_rectangles()
                    break

        # Ground remains the final fallback.
        if (
            not self.is_on_ground
            and self.collision_rect.bottom >= self.ground_y
        ):
            self.feet_y = (
                self.ground_y
                + PlayerTuning.HITBOX_VERTICAL_OFFSET
            )

            self.velocity_y = 0.0
            self.is_on_ground = True

            self._synchronize_rectangles()

    def _move_horizontally(
        self,
        direction: int,
        delta_time: float,
    ) -> None:
        self.feet_x += (
            direction
            * PlayerTuning.MOVEMENT_SPEED
            * delta_time
        )

    def _update_animation(self, delta_time: float) -> None:
        if not self.is_moving or not self.is_on_ground:
            self.current_frame = 0
            self.animation_elapsed = 0.0
            self._refresh_image()
            return

        self.animation_elapsed += delta_time

        while (
            self.animation_elapsed
            >= PlayerTuning.ANIMATION_INTERVAL
        ):
            self.animation_elapsed -= (
                PlayerTuning.ANIMATION_INTERVAL
            )

            self.current_frame += 1

            if self.current_frame >= len(self.frames):
                self.current_frame = 1

        self._refresh_image()

    def _refresh_image(self) -> None:
        frame = self.frames[self.current_frame]

        if self.facing_right:
            self.image = frame
        else:
            self.image = pygame.transform.flip(
                frame,
                True,
                False,
            )

    def _synchronize_rectangles(self) -> None:
        image_offset_x = 0

        if self.current_frame == 0:
            image_offset_x = (
                PlayerTuning.IDLE_IMAGE_OFFSET_X
                if self.facing_right
                else -PlayerTuning.IDLE_IMAGE_OFFSET_X
            )

        self.image_rect = self.image.get_rect(
            midbottom=(
                round(self.feet_x + image_offset_x),
                self.feet_y,
            )
        )

        facing_offset = (
            PlayerTuning.HITBOX_FACING_OFFSET
            if self.facing_right
            else -PlayerTuning.HITBOX_FACING_OFFSET
        )
        
        self.collision_rect.midbottom = (
            round(self.feet_x + facing_offset),
            self.feet_y - PlayerTuning.HITBOX_VERTICAL_OFFSET,
        )

    def _keep_inside_screen(self) -> None:
        """
        Keep the facing-dependent hitbox inside the screen.

        Adjusting feet_x keeps the image and hitbox synchronized.
        """
        correction = 0

        if self.collision_rect.left < 0:
            correction = -self.collision_rect.left

        elif self.collision_rect.right > self.screen_width:
            correction = (
                self.screen_width
                - self.collision_rect.right
            )

        if correction != 0:
            self.feet_x += correction
            self._synchronize_rectangles()

    def render(self, screen: pygame.Surface) -> None:
        screen.blit(
            self.image,
            self.image_rect,
        )

    def render_debug_hitbox(
        self,
        screen: pygame.Surface,
    ) -> None:
        pygame.draw.rect(
            screen,
            (0, 255, 0),
            self.collision_rect,
            width=2,
        )