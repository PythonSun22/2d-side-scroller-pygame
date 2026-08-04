from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

import pygame

if TYPE_CHECKING:
    from state_manager import StateManager


class BaseState(ABC):
    """
    Shared interface for every game state.

    States may handle input, update their own logic, and render themselves,
    but they must never create their own game loop.
    """

    def __init__(
        self,
        screen: pygame.Surface,
        state_manager: StateManager,
    ) -> None:
        self.screen = screen
        self.state_manager = state_manager

    def enter(self) -> None:
        """Called whenever this state becomes active."""

    def exit(self) -> None:
        """Called before this state stops being active."""

    @abstractmethod
    def handle_event(self, event: pygame.event.Event) -> None:
        """Handle one event passed down by the main game loop."""

    @abstractmethod
    def update(self, delta_time: float) -> None:
        """Update state-specific behavior."""

    @abstractmethod
    def render(self, screen: pygame.Surface, alpha: float) -> None:
        """Draw the state onto the shared display surface."""