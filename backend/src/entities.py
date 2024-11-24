"""Entities are things that exist in the game world,
and can be acted upon, or can act on their own."""
from copy import deepcopy
from enum import Enum
from typing import Dict, Optional
from uuid import uuid4

from utils import Vec2


class TileType(Enum):
  """Enum for the different types of tiles in the game."""
  EMPTY = ' '
  WALL = '#'
  PLAYER = '@'
  ENEMY = 'e'
  BOSS = 'B'

  def is_walkable(self) -> bool:
    """Return whether the tile is walkable."""
    return self in [TileType.EMPTY]


char_to_tiletype: Dict[str, TileType] = {t.value: t for t in TileType}


class Entity:
  """Base class for all entities in the game."""

  def __init__(self, pos: Vec2):
    self.pos = deepcopy(pos)
    self.target_pos = deepcopy(pos)
    self.uuid: str = str(uuid4())
    self.tile: Optional[TileType] = None

  def queue_move(self, step: Vec2) -> None:
    """Queue a move for the entity."""
    self.target_pos = self.pos + step

  def priority(self) -> int:
    """Return the priority of the entity. Used for movement tie-breaking."""
    return 0

  def update(self, world) -> None:
    """Update the entity's state."""


class Player(Entity):
  def __init__(self, pos: Vec2):
    super().__init__(pos)
    self.tile = TileType.PLAYER

  def priority(self) -> int:
    return 9999
