"""Alternative frontend for the roguelike using tcod and websockets."""

import tcod
import asyncio
import websockets
import json
import aiohttp


async def get_map_updates(uri, callback):
  """Connects to websocket and handles incoming map updates."""
  async with websockets.connect(uri) as websocket:
    while True:
      map_str = await websocket.recv()
      callback(map_str)


async def create_player(session, server):
  """Creates a new player and returns the UUID."""
  async with session.get(f"http://{server}:8000/add_player") as response:
    return await response.text()


async def move_player(session, server, uuid, dx, dy):
  """Sends a move request for the player."""
  async with session.get(
      f"http://{server}:8000/move_player",
      params={"player_uuid": uuid, "x": dx, "y": dy}
  ) as response:
    await response.text()


async def update_world(session, server):
  """Triggers a world update."""
  async with session.post(f"http://{server}:8000/update") as response:
    await response.text()


def render_map(console, map_str):
  """Renders the map using tcod console."""
  console.clear()

  # Split the map into lines and render each character
  for y, line in enumerate(map_str.split('\n')):
    for x, char in enumerate(line):
      if char == '@':
        color = (255, 255, 0)  # Yellow
      elif char == '#':
        color = (255, 255, 255)  # White
      elif char == '.':
        color = (128, 128, 128)  # Gray
      elif char == 'e':
        color = (255, 0, 0)  # Red for enemies
      else:
        color = (255, 255, 255)  # Default white

      console.print(x=x, y=y, string=char, fg=color)


async def main():
  # Initialize window
  WIDTH = 40
  HEIGHT = 30

  tileset = tcod.tileset.load_tilesheet(
      "terminal8x8_gs_tc.png", 32, 8, tcod.tileset.CHARMAP_TCOD
  )

  # Get server address
  server = input("Enter the server's address (default: localhost): ")
  if not server:
    server = "localhost"

  uri = f"ws://{server}:8000/ws"

  async with aiohttp.ClientSession() as session:
    # Create player and get UUID
    player_uuid = await create_player(session, server)
    await update_world(session, server)

    with tcod.context.new_terminal(
        WIDTH,
        HEIGHT,
        tileset=tileset,
        title="Roguelike Client",
        vsync=True,
    ) as context:
      console = tcod.Console(WIDTH, HEIGHT, order="F")

      # Create a callback to update the map
      current_map = None

      def update_map(map_str):
        nonlocal current_map
        current_map = map_str

      # Start websocket connection in the background
      asyncio.create_task(get_map_updates(uri, update_map))

      try:
        while True:
          # Handle events (like window closing and keyboard input)
          for event in tcod.event.wait():
            if event.type == "QUIT":
              raise SystemExit()

            if event.type == "KEYDOWN":
              dx, dy = 0, 0
              if event.sym == tcod.event.K_UP:
                dy = -1
              elif event.sym == tcod.event.K_DOWN:
                dy = 1
              elif event.sym == tcod.event.K_LEFT:
                dx = -1
              elif event.sym == tcod.event.K_RIGHT:
                dx = 1

              if dx != 0 or dy != 0:
                await move_player(session, server, player_uuid, dx, dy)
                await update_world(session, server)

          # Render current map if available
          if current_map:
            render_map(console, current_map)
            context.present(console)

          # Give control back to asyncio
          await asyncio.sleep(0.016)  # Roughly 60 FPS

      except KeyboardInterrupt:
        pass

if __name__ == "__main__":
  asyncio.run(main())
