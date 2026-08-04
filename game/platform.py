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

    def render(self, screen: pygame.Surface) -> None:
        pygame.draw.rect(
            screen,
            self.color,
            self.rect,
        )

    def render_debug(self, screen: pygame.Surface) -> None:
        pygame.draw.rect(
            screen,
            (255, 220, 0),
            self.rect,
            width=2,
        )