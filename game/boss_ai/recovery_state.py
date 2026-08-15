from game.boss_ai.boss_state import BossState
from game.boss_tuning import BossTuning


class RecoveryState(BossState):
    """
    Vulnerability/recovery pause after a charge.
    """

    def __init__(self, boss) -> None:
        super().__init__(boss)

        self.elapsed = 0.0

    def enter(self) -> None:
        self.boss.is_moving = False
        self.elapsed = 0.0

    def update(
        self,
        delta_time: float,
        player,
    ) -> None:
        self.elapsed += delta_time

        if (
            self.elapsed
            >= BossTuning.RECOVERY_DURATION
        ):
            from game.boss_ai.stalk_state import (
                StalkState,
            )

            self.boss.change_state(
                StalkState(self.boss)
            )