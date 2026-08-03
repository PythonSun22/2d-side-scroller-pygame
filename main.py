from __future__ import annotations

import asyncio
import sys

import pygame

from state_manager import StateManager
from states.level1_state import Level1State
from states.menu_state import MenuState
from states.options_state import OptionsState


# ---------------------------------------------------------------------------
# Application configuration
# ---------------------------------------------------------------------------

SCREEN_WIDTH = 1500
SCREEN_HEIGHT = 600
WINDOW_TITLE = "FREDDY WORLD"

TARGET_FPS = 60
BACKGROUND_COLOR = (20, 20, 30)


class Game:
    """
    Main application controller.

    Game owns:
        - Pygame initialization
        - the display surface
        - the frame clock
        - the single application loop
        - global quit handling
        - the state manager

    Individual states own:
        - state-specific event handling
        - state-specific updates
        - state-specific rendering
    """

    def __init__(self) -> None:
        self.running = True

        self.screen: pygame.Surface
        self.clock: pygame.time.Clock
        self.state_manager: StateManager

        self._initialize_pygame()
        self._create_state_manager()

    def _initialize_pygame(self) -> None:
        """Initialize Pygame and create the application's shared resources."""
        pygame.init()

        # Mixer initialization can fail on systems without an audio device.
        try:
            pygame.mixer.init()
        except pygame.error as error:
            print(f"Audio initialization warning: {error}")

        self.screen = pygame.display.set_mode(
            (SCREEN_WIDTH, SCREEN_HEIGHT)
        )

        pygame.display.set_caption(WINDOW_TITLE)

        self.clock = pygame.time.Clock()

    def _create_state_manager(self) -> None:
        """
        Create the state manager and register all application states.

        States receive references to shared application resources instead of
        creating their own windows, clocks, or event loops.
        """
        self.state_manager = StateManager()

        menu_state = MenuState(
            screen=self.screen,
            state_manager=self.state_manager,
        )

        level1_state = Level1State(
            screen=self.screen,
            state_manager=self.state_manager,
        )

        options_state = OptionsState(
            screen=self.screen,
            state_manager=self.state_manager,
        )

        self.state_manager.register_state("menu", menu_state)
        self.state_manager.register_state("level1", level1_state)
        self.state_manager.register_state("options", options_state)

        self.state_manager.change_state("menu")

    def handle_global_event(self, event: pygame.event.Event) -> None:
        """
        Handle events that apply to the entire application.

        State-specific controls should remain inside the active state.
        """
        if event.type == pygame.QUIT:
            self.running = False

    def update(self, delta_time: float) -> None:
        """Update the currently active state."""
        current_state = self.state_manager.current_state

        if current_state is not None:
            current_state.update(delta_time)

    def render(self) -> None:
        """Render the currently active state."""
        self.screen.fill(BACKGROUND_COLOR)

        current_state = self.state_manager.current_state

        if current_state is not None:
            current_state.render(self.screen)

        pygame.display.flip()

    async def run(self) -> None:
        """
        Run the application's one and only game loop.

        asyncio.sleep(0) yields control back to the browser when running
        through Pygbag. It is harmless during normal desktop execution.
        """
        while self.running:
            delta_time = self.clock.tick(TARGET_FPS) / 1000.0

            for event in pygame.event.get():
                self.handle_global_event(event)

                current_state = self.state_manager.current_state

                if current_state is not None:
                    current_state.handle_event(event)

            self.update(delta_time)
            self.render()

            await asyncio.sleep(0)

        self.shutdown()

    def shutdown(self) -> None:
        """Release Pygame resources."""
        pygame.quit()


async def main() -> None:
    """Application entry point."""
    game = Game()
    await game.run()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pygame.quit()
        sys.exit(0)