from fastapi import FastAPI, WebSocket
from fastapi.websockets import WebSocketDisconnect
from typing import List

from utils import Vec2
from state import parse_ascii_map
from actions import AddEntityAction, MoveAction
from entities import Player
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import PlainTextResponse
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

# Store active websocket connections


class ConnectionManager:
  def __init__(self):
    self.active_connections: List[WebSocket] = []

  async def connect(self, websocket: WebSocket):
    await websocket.accept()
    self.active_connections.append(websocket)

  def disconnect(self, websocket: WebSocket):
    self.active_connections.remove(websocket)

  async def broadcast_map(self, map_str: str):
    for connection in self.active_connections:
      await connection.send_text(map_str)


manager = ConnectionManager()

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


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
  await manager.connect(websocket)
  try:
    # Send initial map state
    await websocket.send_text(str(world))

    while True:
      # Wait for any messages (can be used for player input later)
      data = await websocket.receive_text()

  except WebSocketDisconnect:
    manager.disconnect(websocket)


@app.get("/add_player", response_class=PlainTextResponse)
async def add_player() -> str:
  """Add a new player to the world and return their UUID."""
  new_player = Player(world.spawn)
  actions.append(AddEntityAction(new_player))
  return new_player.uuid


@app.get("/move_player", response_class=PlainTextResponse)
async def move_player(player_uuid: str, x: int, y: int) -> str:
  """Queue a move for the player with the given UUID."""
  actions.append(MoveAction(player_uuid, Vec2(x, y)))
  return player_uuid


@app.post("/update")
async def update() -> None:
  """Update the world based on the queued actions."""
  world.update(actions)
  actions.clear()
  # Broadcast new map state to all connected clients
  await manager.broadcast_map(str(world))
