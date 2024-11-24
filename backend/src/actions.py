"""Actions that can be applied to entities in the world."""
from utils import Vec2


class Action:
  """Base class for all actions."""

  def __init__(self, target_uuid: str):
    self.target_uuid = target_uuid

  def apply(self, world):
    """Apply the action to the world."""
    raise NotImplementedError()


class MoveAction(Action):
  """Try moving an entity by a step."""

  def __init__(self, target_uuid: str, step: Vec2):
    super().__init__(target_uuid)
    self.step = step

  def apply(self, world):
    entity = world.uuid_to_entity[self.target_uuid]
    entity.queue_move(self.step)


class AddEntityAction(Action):
  """Add a player to the world."""

  def __init__(self, player):
    self.player = player
    super().__init__(None)

  def apply(self, world):
    world.add_entity(self.player)
