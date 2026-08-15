from __future__ import annotations

import pygame


class Camera:
    """
    Horizontal camera for Freddy World.

    Game objects remain in world coordinates. The camera converts those
    coordinates into screen coordinates during rendering.
    """

    def __init__(
        self,
        screen_width: int,
        world_width: int,
    ) -> None:
        self.screen_width = screen_width
        self.world_width = max(world_width, screen_width)

        self.x = 0.0
        self.previous_x = self.x

        # Freddy may move freely within this region before the camera follows.
        self.left_dead_zone = int(screen_width * 0.35)
        self.right_dead_zone = int(screen_width * 0.60)

        self.locked_x: float | None = None

    @property
    def max_x(self) -> float:
        return float(
            max(0, self.world_width - self.screen_width)
        )

    def begin_physics_step(self) -> None:
        """
        Preserve the camera position before the next fixed update.
        """
        self.previous_x = self.x

    def get_interpolated_x(
        self,
        alpha: float,
    ) -> float:
        """
        Return a visual camera position between the previous and current
        physics states.
        """
        return (
            self.previous_x
            + (self.x - self.previous_x) * alpha
        )
        
    def update(self, target_rect: pygame.Rect) -> None:
        """
        Follow the target only when it leaves the horizontal dead zone.
        """
        target_screen_x = target_rect.centerx - self.x

        if self.locked_x is not None:
            self.x = self.locked_x
            return

        if target_screen_x > self.right_dead_zone:
            self.x = (
                target_rect.centerx
                - self.right_dead_zone
            )

        elif target_screen_x < self.left_dead_zone:
            self.x = (
                target_rect.centerx
                - self.left_dead_zone
            )

        self.x = max(
            0.0,
            min(self.x, self.max_x),
        )

    def world_to_screen_x(self, world_x: float) -> int:
        return round(world_x - self.x)

    def apply_rect(self, world_rect: pygame.Rect) -> pygame.Rect:
        return world_rect.move(
            -round(self.x),
            0,
        )

    def lock_to(self, x: float) -> None:
        self.locked_x = max(
            0.0,
            min(float(x), self.max_x),
        )

        # Prevent interpolation from visibly sliding in from the old camera
        # position on the first locked frame.
        self.x = self.locked_x
        self.previous_x = self.x


    def unlock(self) -> None:
        self.locked_x = None