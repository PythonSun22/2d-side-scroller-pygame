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

    # Jump forgiveness
    COYOTE_TIME = 0.08

    # Health and damage
    MAX_HEALTH = 3
    CONTACT_DAMAGE = 1

    INVULNERABILITY_DURATION = 1.0

    KNOCKBACK_HORIZONTAL_SPEED = 420.0
    KNOCKBACK_VERTICAL_SPEED = 420.0
    KNOCKBACK_DECELERATION = 1600.0

    # Fire transformation
    FIRE_TRANSFORM_DURATION = 1.0
    FIRE_TRANSFORM_FLOAT_HEIGHT = 30.0
    FIRE_TRANSFORM_FLASH_RATE = 12.0

    MOVE_SPEED = 300.0
    SPRINT_MULTIPLIER = 1.6

    