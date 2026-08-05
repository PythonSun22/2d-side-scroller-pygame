from __future__ import annotations

from game.ai.mob_state import MobState
from game.mob_tuning import MobTuning


class PatrolState(MobState):
    """Patrol between the mob's configured boundaries."""

    def update(self, delta_time: float, player) -> None:
        mob = self.mob

        distance_to_player = abs(
            player.feet_x - mob.feet_x
        )

        if distance_to_player <= MobTuning.DETECTION_RANGE:
            from game.ai.alert_state import AlertState

            mob.change_state(AlertState(mob))
            return

        mob.feet_x += (
            mob.direction
            * MobTuning.PATROL_SPEED
            * delta_time
        )

        if mob.feet_x >= mob.patrol_right:
            mob.feet_x = mob.patrol_right
            mob.set_direction(-1)

        elif mob.feet_x <= mob.patrol_left:
            mob.feet_x = mob.patrol_left
            mob.set_direction(1)