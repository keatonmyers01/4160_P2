from enum import Enum

import pygame
from pygame.event import Event

import engine
from engine.sprite import Sprite

TEXTURE_PATH = 'game/asset/player'
MOVING_SPEED = 3


class PlayerRotation(Enum):

    FACING = 0
    LEFT = 1
    RIGHT = 2
    TURNED = 3


class PlayerAction(Enum):

    IDLE = 0
    WALK = 1
    ATTACK = 2


class PlayerState(Enum):

    # Idle
    IDLE_FACING = '/idle/facing'
    IDLE_LEFT = '/idle/left'
    IDLE_RIGHT = '/idle/right'
    IDLE_TURNED = '/idle/turned'
    # Walking
    WALK_FACING = '/walk/facing'
    WALK_LEFT = '/walk/left'
    WALK_RIGHT = '/walk/right'
    WALK_TURNED = '/walk/turned'
    # Attacking
    ATTACK_FACING = '/attack/facing'
    ATTACK_LEFT = '/attack/left'
    ATTACK_RIGHT = '/attack/right'
    ATTACK_TURNED = '/attack/turned'

    @staticmethod
    def bind(action: PlayerAction, rotation: PlayerRotation) -> 'PlayerState':
        match action:
            case PlayerAction.IDLE:
                match rotation:
                    case PlayerRotation.FACING:
                        return PlayerState.IDLE_FACING
                    case PlayerRotation.LEFT:
                        return PlayerState.IDLE_LEFT
                    case PlayerRotation.RIGHT:
                        return PlayerState.IDLE_RIGHT
                    case PlayerRotation.TURNED:
                        return PlayerState.IDLE_TURNED
            case PlayerAction.WALK:
                match rotation:
                    case PlayerRotation.FACING:
                        return PlayerState.WALK_FACING
                    case PlayerRotation.LEFT:
                        return PlayerState.WALK_LEFT
                    case PlayerRotation.RIGHT:
                        return PlayerState.WALK_RIGHT
                    case PlayerRotation.TURNED:
                        return PlayerState.WALK_TURNED
            case PlayerAction.ATTACK:
                match rotation:
                    case PlayerRotation.FACING:
                        return PlayerState.ATTACK_FACING
                    case PlayerRotation.LEFT:
                        return PlayerState.ATTACK_LEFT
                    case PlayerRotation.RIGHT:
                        return PlayerState.ATTACK_RIGHT
                    case PlayerRotation.TURNED:
                        return PlayerState.ATTACK_TURNED


class Player(Sprite):

    def __init__(self):
        super().__init__(PlayerState.IDLE_FACING,
                         bound_to_screen=True,
                         health_bar=True,
                         priority=50,
                         scalar=0.6,
                         ticks_per_frame=5)
        self.add_state(PlayerState.IDLE_FACING, TEXTURE_PATH, 5)
        self.add_state(PlayerState.IDLE_LEFT, TEXTURE_PATH, 5)
        self.add_state(PlayerState.IDLE_RIGHT, TEXTURE_PATH, 5)
        self.add_state(PlayerState.IDLE_TURNED, TEXTURE_PATH, 5)
        self.add_state(PlayerState.WALK_FACING, TEXTURE_PATH, 9)
        self.add_state(PlayerState.WALK_LEFT, TEXTURE_PATH, 9)
        self.add_state(PlayerState.WALK_RIGHT, TEXTURE_PATH, 9)
        self.add_state(PlayerState.WALK_TURNED, TEXTURE_PATH, 9)
        self.add_state(PlayerState.ATTACK_FACING, TEXTURE_PATH, 3)
        self.add_state(PlayerState.ATTACK_LEFT, TEXTURE_PATH, 3)
        self.add_state(PlayerState.ATTACK_RIGHT, TEXTURE_PATH, 3)
        self.add_state(PlayerState.ATTACK_TURNED, TEXTURE_PATH, 3)
        self._accept_input = False
        self._rotation = PlayerRotation.FACING

    def _on_load(self) -> None:
        self._accept_input = True
        engine.event_handler.register(pygame.KEYDOWN, self.on_key_press)
        engine.event_handler.register(pygame.KEYUP, self.on_key_release)
        engine.event_handler.register(pygame.MOUSEBUTTONDOWN, self.on_mouse_press)

    def on_key_press(self, event: Event) -> None:
        if not self._accept_input or self._state_change:
            return
        current_velocity = self.velocity
        match event.key:
            case pygame.K_w:
                self._velocity = (current_velocity[0], -MOVING_SPEED)
                self._rotation = PlayerRotation.TURNED
            case pygame.K_a:
                self._velocity = (-MOVING_SPEED, current_velocity[1])
                self._rotation = PlayerRotation.LEFT
            case pygame.K_s:
                self._velocity = (current_velocity[0], MOVING_SPEED)
                self._rotation = PlayerRotation.FACING
            case pygame.K_d:
                self._velocity = (MOVING_SPEED, current_velocity[1])
                self._rotation = PlayerRotation.RIGHT
        self.state = PlayerState.bind(PlayerAction.WALK, self._rotation)

    def on_key_release(self, event: Event) -> None:
        if not self._accept_input or self._state_change:
            return
        current_velocity = self.velocity
        match event.key:
            case pygame.K_w:
                self._velocity = (current_velocity[0], 0)
            case pygame.K_a:
                self._velocity = (0, current_velocity[1])
            case pygame.K_s:
                self._velocity = (current_velocity[0], 0)
            case pygame.K_d:
                self._velocity = (0, current_velocity[1])
        action = PlayerAction.WALK if self.is_moving else PlayerAction.IDLE
        self.state = PlayerState.bind(action, self._rotation)

    def on_mouse_press(self, event: Event) -> None:
        if not self._accept_input or self._state_change or event.button != pygame.BUTTON_LEFT:
            return
        self.queue_state(PlayerState.bind(PlayerAction.ATTACK, self._rotation), self.post_attack)

    def post_attack(self) -> None:
        pass

    @property
    def accept_input(self) -> bool:
        return self._accept_input

    @accept_input.setter
    def accept_input(self, value: bool) -> None:
        self._accept_input = value

    @property
    def max_health(self) -> int:
        return 500

    def _on_damage(self) -> None:
        pass

    def _on_heal(self) -> None:
        pass

    def _on_death(self) -> None:
        pass
