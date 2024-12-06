
from fastapi import FastAPI

from utils import Vec2
from state import parse_ascii_map
from actions import AddEntityAction, MoveAction
from entities import Player
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import PlainTextResponse

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Replace "*" with specific domains in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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

@app.get("/current_map", response_class=PlainTextResponse)
async def current_map() -> str:
  """Return the current map as a string."""
  return str(world)

@app.get("/add_player")
async def add_player() -> str:
  """Add a new player to the world and return their UUID."""
  new_player = Player(world.spawn)
  actions.append(AddEntityAction(new_player))
  return new_player.uuid

@app.post("/move_player")
async def move_player(player_uuid: str, x: int, y: int) -> None:
  """Queue a move for the player with the given UUID."""
  actions.append(MoveAction(player_uuid, Vec2(x, y)))

@app.post("/update")
async def update() -> None:
  """Update the world based on the queued actions."""
  world.update(actions)
  actions.clear()
