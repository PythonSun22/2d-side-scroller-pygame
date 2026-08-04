from __future__ import annotations

import pygame


class Platform:
    """
    Simple static platform.

    The platform owns only its collision rectangle and presentation.
    """

    def __init__(
        self,
        rect: pygame.Rect,
        *,
        color: tuple[int, int, int] = (110, 80, 45),
    ) -> None:
        self.rect = rect
        self.color = color

    def render(
        self,
        screen: pygame.Surface,
        camera_x: float,
    ) -> None:
        screen_rect = self.rect.move(
            -round(camera_x),
            0,
        )

        pygame.draw.rect(
            screen,
            self.color,
            screen_rect,
        )

    def render_debug(
        self,
        screen: pygame.Surface,
        camera_x: float,
    ) -> None:
        screen_rect = self.rect.move(
            -round(camera_x),
            0,
        )

        pygame.draw.rect(
            screen,
            (255, 220, 0),
            screen_rect,
            width=2,
        )