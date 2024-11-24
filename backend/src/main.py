
from fastapi import FastAPI

from utils import Vec2
from state import World, parse_ascii_map
from actions import AddEntityAction, MoveAction
from entities import Player

app = FastAPI()


@app.get("/")
async def root():
  return {"message": "Hello World"}

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
actions = []

@app.get("/current_map")
async def current_map() -> str:
  return str(world)

@app.get("/add_player")
async def add_player() -> str:
  new_player = Player(world.spawn)
  actions.append(AddEntityAction(new_player))
  return new_player.uuid

@app.get("/move_player")
async def move_player(player_uuid: str, x: int, y: int) -> str:
  actions.append(MoveAction(player_uuid, Vec2(x, y)))
  return player_uuid

@app.post("/update")
async def update() -> None:
  world.update(actions)
  actions.clear()
