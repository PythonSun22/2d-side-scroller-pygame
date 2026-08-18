from __future__ import annotations

import pygame

from game.world import World
from states.base_state import BaseState


class WorldState(BaseState):
    """
    Application state representing active gameplay.

    This class handles application-level transitions. The World object owns
    gameplay objects, physics, camera behavior, and rendering.
    """

    def __init__(
        self,
        screen: pygame.Surface,
        state_manager,
    ) -> None:
        super().__init__(screen, state_manager)

        self.world = World(
            self.screen.get_size()
        )

    def enter(self) -> None:
        # Every transition into gameplay starts a fresh run. This prevents
        # defeated mobs, collected power-ups, projectiles, camera locks, and
        # boss state from leaking into a restart.
        self.world = World(
            self.screen.get_size()
        )

    def exit(self) -> None:
        pass

    def handle_event(
        self,
        event: pygame.event.Event,
    ) -> None:
        # Application-level state transitions stay here.
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.state_manager.change_state("menu")
                return

            if event.key == pygame.K_o:
                self.state_manager.change_state("options")
                return

        # All remaining gameplay input belongs to the World.
        self.world.handle_event(event)

    def update(self, delta_time: float) -> None:
        self.world.update(delta_time)

        if self.world.player_defeated:
            self.state_manager.change_state(
                "defeat"
            )
            return

        if self.world.boss_defeated:
            self.state_manager.change_state(
                "victory"
            )
            return
        
    def render(self, screen: pygame.Surface, alpha: float) -> None:
        self.world.render(screen, alpha)