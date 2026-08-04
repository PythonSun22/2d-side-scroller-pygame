from __future__ import annotations

from dataclasses import dataclass

import pygame

from game.assets import assets
from states.base_state import BaseState


@dataclass
class MenuButton:
    """
    Lightweight text button used by the main menu.

    This class does not poll events or draw the display. It only tracks its
    own presentation and hitbox.
    """

    label: str
    center: tuple[int, int]
    font: pygame.font.Font
    base_color: pygame.Color
    hover_color: pygame.Color

    def __post_init__(self) -> None:
        self.is_hovered = False
        self.rect = pygame.Rect(0, 0, 0, 0)
        self._refresh_rect()

    @property
    def color(self) -> pygame.Color:
        if self.is_hovered:
            return self.hover_color

        return self.base_color

    def _create_text_surface(self) -> pygame.Surface:
        return self.font.render(
            self.label,
            True,
            self.color,
        )

    def _refresh_rect(self) -> None:
        text_surface = self._create_text_surface()
        self.rect = text_surface.get_rect(center=self.center)

    def update_hover(self, mouse_position: tuple[int, int]) -> None:
        self.is_hovered = self.rect.collidepoint(mouse_position)

    def contains(self, position: tuple[int, int]) -> bool:
        return self.rect.collidepoint(position)

    def render(self, screen: pygame.Surface) -> None:
        text_surface = self._create_text_surface()
        self.rect = text_surface.get_rect(center=self.center)
        screen.blit(text_surface, self.rect)


class MenuState(BaseState):
    BACKGROUND_FILE = "Background.png"
    FONT_FILE = "Gothic Pixels.ttf"
    LEFT_SELECTOR_FILE = "Selectors.png"
    RIGHT_SELECTOR_FILE = "Selector_2.png"

    TITLE = "Freddy's World"

    TITLE_COLOR = pygame.Color("#b68f40")
    BUTTON_COLOR = pygame.Color("#d7fcd4")
    HOVER_COLOR = pygame.Color("white")

    def __init__(
        self,
        screen: pygame.Surface,
        state_manager,
    ) -> None:
        super().__init__(screen, state_manager)

        self.background = assets.load_image(
            self.BACKGROUND_FILE,
            alpha=False,
        )

        self.background = pygame.transform.smoothscale(
            self.background,
            self.screen.get_size(),
        )

        self.left_selector = assets.load_image(
            self.LEFT_SELECTOR_FILE
        )

        self.right_selector = assets.load_image(
            self.RIGHT_SELECTOR_FILE
        )

        self.title_font = assets.load_font(
            self.FONT_FILE,
            100,
        )

        self.button_font = assets.load_font(
            self.FONT_FILE,
            75,
        )

        center_x = self.screen.get_width() // 2

        self.play_button = MenuButton(
            label="PLAY",
            center=(center_x, 250),
            font=self.button_font,
            base_color=self.BUTTON_COLOR,
            hover_color=self.HOVER_COLOR,
        )

        self.options_button = MenuButton(
            label="OPTIONS",
            center=(center_x, 400),
            font=self.button_font,
            base_color=self.BUTTON_COLOR,
            hover_color=self.HOVER_COLOR,
        )

        self.quit_button = MenuButton(
            label="QUIT",
            center=(center_x, 550),
            font=self.button_font,
            base_color=self.BUTTON_COLOR,
            hover_color=self.HOVER_COLOR,
        )

        self.buttons = [
            self.play_button,
            self.options_button,
            self.quit_button,
        ]

        self.selected_index = 0

    def enter(self) -> None:
        self.selected_index = 0
        self._apply_keyboard_selection()

    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type == pygame.MOUSEMOTION:
            self._update_mouse_hover(event.pos)

        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == pygame.BUTTON_LEFT:
                self._handle_mouse_click(event.pos)

        elif event.type == pygame.KEYDOWN:
            self._handle_keyboard_input(event.key)

    def update(self, delta_time: float) -> None:
        # Hover remains responsive even if the mouse does not produce a new
        # motion event immediately after entering the menu.
        mouse_position = pygame.mouse.get_pos()

        if any(button.contains(mouse_position) for button in self.buttons):
            self._update_mouse_hover(mouse_position)

    def render(self, screen: pygame.Surface) -> None:
        screen.blit(self.background, (0, 0))

        self._render_title(screen)

        for button in self.buttons:
            button.render(screen)

            if button.is_hovered:
                self._render_selectors(screen, button)

    def _render_title(self, screen: pygame.Surface) -> None:
        title_surface = self.title_font.render(
            self.TITLE,
            True,
            self.TITLE_COLOR,
        )

        title_rect = title_surface.get_rect(
            center=(screen.get_width() // 2, 100)
        )

        screen.blit(title_surface, title_rect)

    def _render_selectors(
        self,
        screen: pygame.Surface,
        button: MenuButton,
    ) -> None:
        horizontal_gap = 20

        left_position = (
            button.rect.left
            - self.left_selector.get_width()
            - horizontal_gap,
            button.rect.centery
            - self.left_selector.get_height() // 2,
        )

        right_position = (
            button.rect.right + horizontal_gap,
            button.rect.centery
            - self.right_selector.get_height() // 2,
        )

        screen.blit(self.left_selector, left_position)
        screen.blit(self.right_selector, right_position)

    def _update_mouse_hover(
        self,
        mouse_position: tuple[int, int],
    ) -> None:
        hovered_index: int | None = None

        for index, button in enumerate(self.buttons):
            button.update_hover(mouse_position)

            if button.is_hovered:
                hovered_index = index

        if hovered_index is not None:
            self.selected_index = hovered_index

    def _handle_mouse_click(
        self,
        mouse_position: tuple[int, int],
    ) -> None:
        if self.play_button.contains(mouse_position):
            self.state_manager.change_state("world")

        elif self.options_button.contains(mouse_position):
            self.state_manager.change_state("options")

        elif self.quit_button.contains(mouse_position):
            # The main loop remains responsible for handling application exit.
            pygame.event.post(pygame.event.Event(pygame.QUIT))

    def _handle_keyboard_input(self, key: int) -> None:
        if key in (pygame.K_DOWN, pygame.K_s):
            self.selected_index = (
                self.selected_index + 1
            ) % len(self.buttons)

            self._apply_keyboard_selection()

        elif key in (pygame.K_UP, pygame.K_w):
            self.selected_index = (
                self.selected_index - 1
            ) % len(self.buttons)

            self._apply_keyboard_selection()

        elif key in (pygame.K_RETURN, pygame.K_SPACE):
            self._activate_selected_button()

        elif key == pygame.K_o:
            self.state_manager.change_state("options")

        elif key == pygame.K_ESCAPE:
            pygame.event.post(pygame.event.Event(pygame.QUIT))

    def _apply_keyboard_selection(self) -> None:
        for index, button in enumerate(self.buttons):
            button.is_hovered = index == self.selected_index

    def _activate_selected_button(self) -> None:
        selected_button = self.buttons[self.selected_index]

        if selected_button is self.play_button:
            self.state_manager.change_state("world")

        elif selected_button is self.options_button:
            self.state_manager.change_state("options")

        elif selected_button is self.quit_button:
            pygame.event.post(pygame.event.Event(pygame.QUIT))