from __future__ import annotations

import pygame

from states.base_state import BaseState


class OptionsState(BaseState):
    def __init__(
        self,
        screen: pygame.Surface,
        state_manager,
    ) -> None:
        super().__init__(screen, state_manager)

        self.background_color = (60, 45, 70)
        self.font = pygame.font.Font(None, 48)

        self.previous_state_name = "menu"

    def enter(self) -> None:
        current_name = self.state_manager.current_state_name

        if current_name != "options" and current_name is not None:
            self.previous_state_name = current_name

    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.state_manager.change_state("menu")

    def update(self, delta_time: float) -> None:
        pass

    def render(self, screen: pygame.Surface) -> None:
        screen.fill(self.background_color)

        title_surface = self.font.render(
            "Options Placeholder",
            True,
            (255, 255, 255),
        )

        instructions_surface = pygame.font.Font(None, 30).render(
            "Press Escape to return to the menu",
            True,
            (225, 225, 225),
        )

        title_rect = title_surface.get_rect(
            center=screen.get_rect().center
        )

        instructions_rect = instructions_surface.get_rect(
            center=(screen.get_width() // 2, 380)
        )

        screen.blit(title_surface, title_rect)
        screen.blit(instructions_surface, instructions_rect)