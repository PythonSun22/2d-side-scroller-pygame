from __future__ import annotations


class PlayerTuning:
    """
    Central configuration for Freddy's movement, animation, and hitbox.

    These values can be adjusted without changing Player's core logic.
    """

    # Collision box
    HITBOX_WIDTH = 39
    HITBOX_HEIGHT = 80
    HITBOX_FACING_OFFSET = 0
    HITBOX_VERTICAL_OFFSET = 6

    # Movement
    MOVEMENT_SPEED = 300.0

    # Animation
    ANIMATION_INTERVAL = 0.2

    # Idle sprite alignment
    IDLE_IMAGE_OFFSET_X = 8

    # Vertical physics
    GRAVITY = 1800.0
    JUMP_SPEED = 700.0
    MAX_FALL_SPEED = 1000.0
