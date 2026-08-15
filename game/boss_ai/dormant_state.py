from game.boss_ai.boss_state import BossState


class DormantState(BossState):
    """
    Boss remains completely inactive until the arena camera locks.
    """

    def enter(self) -> None:
        self.boss.is_moving = False

    def update(
        self,
        delta_time: float,
        player,
    ) -> None:
        pass