from __future__ import annotations

from game.ai.mob_state import MobState
from game.mob_tuning import MobTuning


class ReturnState(MobState):
    """Return the mob to its original patrol position."""

    def enter(self) -> None:
        self.mob.is_moving = True

    def update(self, delta_time: float, player) -> None:
        mob = self.mob

        distance_to_player = abs(
            player.feet_x - mob.feet_x
        )

        if distance_to_player <= MobTuning.DETECTION_RANGE:
            from game.ai.alert_state import AlertState

            mob.change_state(AlertState(mob))
            return

        difference_x = mob.home_x - mob.feet_x

        if abs(difference_x) <= MobTuning.RETURN_TOLERANCE:
            mob.feet_x = mob.home_x

            from game.ai.patrol_state import PatrolState

            mob.change_state(PatrolState(mob))
            return

        if difference_x > 0:
            mob.set_direction(1)
        else:
            mob.set_direction(-1)

        mob.feet_x += (
            mob.direction
            * MobTuning.RETURN_SPEED
            * delta_time
        )