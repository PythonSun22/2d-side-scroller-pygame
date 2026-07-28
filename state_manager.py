from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from states.base_state import BaseState


class StateManager:
    """
    Registers game states and controls which state is currently active.
    """

    def __init__(self) -> None:
        self._states: dict[str, BaseState] = {}
        self._current_state: BaseState | None = None
        self._current_state_name: str | None = None

    @property
    def current_state(self) -> BaseState | None:
        return self._current_state

    @property
    def current_state_name(self) -> str | None:
        return self._current_state_name

    def register_state(
        self,
        name: str,
        state: BaseState,
    ) -> None:
        if not name:
            raise ValueError("State name cannot be empty.")

        if name in self._states:
            raise ValueError(f"State '{name}' is already registered.")

        self._states[name] = state

    def change_state(self, name: str) -> None:
        if name not in self._states:
            raise KeyError(f"State '{name}' is not registered.")

        if name == self._current_state_name:
            return

        if self._current_state is not None:
            self._current_state.exit()

        self._current_state = self._states[name]
        self._current_state_name = name

        self._current_state.enter()