import { useState, useEffect } from 'react';

function App() {
  const [currentMap, setCurrentMap] = useState<string>("");
  const [playerId, setPlayerId] = useState<string>("");
  const [moveResult, setMoveResult] = useState<string>("");

  // Websocket connection
  useEffect(() => {
    const socket = new WebSocket('ws://localhost:8000/ws');

    socket.onmessage = (event) => {
      setCurrentMap(event.data);
    };

    // Cleanup on unmount
    // This immediately severs the connection in strict mode lol
    return () => {
      socket.close();
    };
  }, []);

  useEffect(() => {
    // Only add a player if one has not been added yet
    if (!playerId) {
      addPlayer();
    }
  }, [playerId]);

  const addPlayer = async () => {
    try {
      const response = await fetch('http://localhost:8000/add_player');
      const playerId = await response.text();
      setPlayerId(playerId);
      console.log(`Player added with ID: ${playerId}`);
      await updateWorld();
    } catch (error) {
      console.error('Error adding player:', error);
    }
  };

  const movePlayer = async (x: number, y: number) => {
    if (!playerId) {
      alert('Add a player first!');
      return;
    }
    try {
      const sanitizedPlayerId = playerId.replace(/^"|"$/g, '');
      //console.log(sanitizedPlayerId);
      const response = await fetch(`http://localhost:8000/move_player?player_uuid=${sanitizedPlayerId}&x=${x}&y=${y}`);
      const result = await response.text();
      setMoveResult(result);
      
      // Update player position on the map
      await updateWorld();
    } catch (error) {
      console.error('Error moving player:', error);
    }
  };

  const updateWorld = async () => {
    try {
      await fetch('http://localhost:8000/update', { method: 'POST' });
    } catch (error) {
      console.error('Error updating world:', error);
    }
  };

  // New effect for keyboard controls
  useEffect(() => {
    const handleKeyDown = (event: KeyboardEvent) => {
      if (!playerId) {
        alert('Add a player first!');
        return;
      }
      switch (event.key) {
        case 'ArrowUp':
        case 'w':
        case 'W':
          movePlayer(0, -1);
          break;
        case 'ArrowDown':
        case 's':
        case 'S':
          movePlayer(0, 1);
          break;
        case 'ArrowLeft':
        case 'a':
        case 'A':
          movePlayer(-1, 0);
          break;
        case 'ArrowRight':
        case 'd':
        case 'D':
          movePlayer(1, 0);
          break;
        default:
          break;
      }
    };

    window.addEventListener('keydown', handleKeyDown);

    // Cleanup the event listener on unmount
    return () => {
      window.removeEventListener('keydown', handleKeyDown);
    };

  }, [playerId]); // Include playerId for the handler to have updated info

  return (
    <div className="App">
      <h1>Game Control Panel</h1>
      <div>
        <h2>Current Map:</h2>
        <pre style={{ whiteSpace: "pre-wrap" }}>{currentMap}</pre>
      </div>
      <div>
        <p>Player ID: {playerId}</p>
      </div>
      <div>
        <p>Move Result: {moveResult}</p>
      </div>
    </div>
  );
}

export default App;