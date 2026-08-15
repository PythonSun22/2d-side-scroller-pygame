from game.boss_ai.boss_state import BossState
from game.boss_tuning import BossTuning


class ChargeState(BossState):
    """
    Fast committed horizontal rush.

    The boss does not home toward Freddy after the charge begins.
    """

    def __init__(
        self,
        boss,
        direction: int,
    ) -> None:
        super().__init__(boss)

        self.charge_direction = (
            1 if direction > 0 else -1
        )

        self.elapsed = 0.0

    def enter(self) -> None:
        boss = self.boss

        boss.set_direction(
            self.charge_direction
        )

        boss.is_moving = True

    def update(
        self,
        delta_time: float,
        player,
    ) -> None:
        boss = self.boss

        self.elapsed += delta_time

        boss.feet_x += (
            self.charge_direction
            * BossTuning.CHARGE_SPEED
            * delta_time
        )

        hit_arena_edge = (
            boss.clamp_to_arena()
        )

        if (
            self.elapsed >= BossTuning.CHARGE_DURATION
            or hit_arena_edge
        ):
            from game.boss_ai.recovery_state import (
                RecoveryState,
            )

            boss.change_state(
                RecoveryState(boss)
            )