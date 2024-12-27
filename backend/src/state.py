import random
from copy import deepcopy
from typing import Dict, List

from actions import Action, AddEntityAction, MoveAction
from entities import Entity, Player, WanderingEnemy, TileType, char_to_tiletype
from utils import Vec2


def parse_ascii_map(ascii_map: str) -> 'World':
  """Parse an ASCII map and turn it into a World."""
  lines = ascii_map.strip().split("\n")
  height = len(lines)
  width = len(lines[0])
  w = World(Vec2(width, height))
  for y, line in enumerate(lines):
    for x, char in enumerate(line):
      pos = Vec2(x, y)
      tile = char_to_tiletype[char]
      # TODO: parse other entities
      if tile == TileType.PLAYER:
        w.spawn = pos
      if tile == TileType.ENEMY:
        enemy = WanderingEnemy(pos)
        w.add_entity(enemy)
      else:
        w.set(pos, tile)
  return w


class World:
  """The game world, containing all entities and tiles."""

  def __init__(self, size: Vec2, seed: int = 0):
    self.size = deepcopy(size)
    self.tiles = [TileType.EMPTY] * (size.x * size.y)
    self.entities: List[Entity] = []
    self.pos_to_entities: Dict[Vec2, List[Entity]] = {}
    self.uuid_to_entity: Dict[str, Entity] = {}
    self.players: List[Player] = []
    self.spawn = Vec2(1, 1)
    self.seed = seed
    random.seed(seed)
    self.random_state = random.getstate()
    # TODO: do random.setstate and random.getstate when serializing

  def get(self, pos: Vec2) -> TileType:
    """Get the tile at the given position."""
    if pos.x < 0 or pos.x >= self.size.x or pos.y < 0 or pos.y >= self.size.y:
      raise ValueError("Out of bounds")
    if pos in self.pos_to_entities:
      return self.pos_to_entities[pos][0].tile
    return self.tiles[pos.y * self.size.x + pos.x]

  def get_safe(self, pos: Vec2) -> TileType:
    """Get the tile at the given position, or EMPTY if out of bounds."""
    if pos.x < 0 or pos.x >= self.size.x or pos.y < 0 or pos.y >= self.size.y:
      return TileType.EMPTY
    return self.tiles[pos.y * self.size.x + pos.x]

  def set(self, pos: Vec2, tile: TileType):
    """Set the tile at the given position."""
    if pos.x < 0 or pos.x >= self.size.x or pos.y < 0 or pos.y >= self.size.y:
      raise ValueError(f"Out of bounds. pos={pos}, size={self.size}")
    self.tiles[pos.y * self.size.x + pos.x] = tile

  def set_safe(self, pos: Vec2, tile: TileType):
    """Set the tile at the given position, or do nothing if out of bounds."""
    if pos.x < 0 or pos.x >= self.size.x or pos.y < 0 or pos.y >= self.size.y:
      return
    self.tiles[pos.y * self.size.x + pos.x] = tile

  def add_entity(self, entity: Entity):
    """Add an entity to the world."""
    self.entities.append(entity)
    if entity.pos not in self.pos_to_entities:
      self.pos_to_entities[entity.pos] = []
    self.pos_to_entities[entity.pos].append(entity)
    self.uuid_to_entity[entity.uuid] = entity
    print(f"Added entity: {entity}, {entity.uuid}")
    if isinstance(entity, Player):
      self.players.append(entity)

  def __str__(self):
    result = ""
    for y in range(self.size.y):
      for x in range(self.size.x):
        pos = Vec2(x, y)
        result += self.get(pos).value
      result += "\n"
    return result

  def __repr__(self):
    return self.__str__()

  def _resolve_move(self) -> bool:
    """Performs one iteration of the move resolution algorithm.
    Returns True if still running."""

    # identify conflicting movements
    target_pos_to_entities: Dict[Vec2, List[Entity]] = {}
    for entity in self.entities:
      # if trying to move,
      if entity.pos != entity.target_pos:
        if entity.target_pos not in target_pos_to_entities:
          target_pos_to_entities[entity.target_pos] = []
        # register desire to move
        target_pos_to_entities[entity.target_pos].append(entity)

    # resolve resolvable conflicts
    moved = False
    for target_pos, entities in target_pos_to_entities.items():
      if len(entities) > 1:
        # multiple entities want to move to the same position
        # sort by priority
        entities.sort(key=lambda e: e.priority())
        # do nothing if tied
        if entities[0].priority() == entities[1].priority():
          continue
        # move the entity with the highest priority
        entity = entities[0]
        # check if the target position is walkable
        if self.get(target_pos).is_walkable():
          # move the entity
          self.pos_to_entities[entity.pos].remove(entity)
          if len(self.pos_to_entities[entity.pos]) == 0:
            self.pos_to_entities.pop(entity.pos)
          entity.pos = target_pos
          if target_pos not in self.pos_to_entities:
            self.pos_to_entities[target_pos] = []
          self.pos_to_entities[target_pos].append(entity)
          moved = True
      elif len(entities) == 1:
        # only one entity wants to move to the position
        entity = entities[0]
        # check if the target position is walkable
        if self.get(target_pos).is_walkable():
          # move the entity
          # self.pos_to_entity.pop(entity.pos)
          self.pos_to_entities[entity.pos].remove(entity)
          if len(self.pos_to_entities[entity.pos]) == 0:
            self.pos_to_entities.pop(entity.pos)
          entity.pos = target_pos
          # self.pos_to_entity[target_pos] = entity
          if target_pos not in self.pos_to_entities:
            self.pos_to_entities[target_pos] = []
          self.pos_to_entities[target_pos].append(entity)
          moved = True

    return moved

  def update(self, actions: List[Action]):
    """Update the world based on the given actions."""
    # apply actions
    for action in actions:
      action.apply(self)

    # run updates on entities
    for entity in self.entities:
      entity.update(self)

    # resolve moves
    while self._resolve_move():
      pass


if __name__ == "__main__":
  test_map = """######################
#                    #
#                    #
#             e      #
#                    #
#       @            #
#                    #
#           #        #
#                    #
#       ##           #
#        #           #
#                    #
######################"""

  world = parse_ascii_map(test_map)

  player_1 = Player(world.spawn)
  player_2 = Player(world.spawn)

  world.update([AddEntityAction(player_1), AddEntityAction(player_2)])

  running = True
  while running:
    print(world)
    player_actions = []
    for player in world.players:
      move = input(f"Move for player {player.uuid}: ")
      if move == "w":
        player_actions.append(MoveAction(player.uuid, Vec2(0, -1)))
      elif move == "a":
        player_actions.append(MoveAction(player.uuid, Vec2(-1, 0)))
      elif move == "s":
        player_actions.append(MoveAction(player.uuid, Vec2(0, 1)))
      elif move == "d":
        player_actions.append(MoveAction(player.uuid, Vec2(1, 0)))
      elif move == " ":
        player_actions.append(MoveAction(player.uuid, Vec2(0, 0)))
      else:
        running = False
    world.update(player_actions)
