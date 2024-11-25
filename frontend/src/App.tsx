import { useState } from 'react';

function App() {
  const [currentMap, setCurrentMap] = useState<string>('');
  const [playerId, setPlayerId] = useState<string>('');
  const [moveResult, setMoveResult] = useState<string>('');

  const fetchCurrentMap = async () => {
    try {
      const response = await fetch('http://localhost:8000/current_map');
      const data = await response.text();
      setCurrentMap(data);
    } catch (error) {
      console.error('Error fetching current map:', error);
    }
  };

  const addPlayer = async () => {
    try {
      const response = await fetch('http://localhost:8000/add_player');
      const playerId = await response.text();
      setPlayerId(playerId);
      alert(`Player added with ID: ${playerId}`);
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
      const response = await fetch(`http://localhost:8000/move_player?player_uuid=${playerId}&x=${x}&y=${y}`);
      const result = await response.text();
      setMoveResult(result);
      alert(`Player moved to (${x}, ${y})`);
    } catch (error) {
      console.error('Error moving player:', error);
    }
  };

  const updateWorld = async () => {
    try {
      await fetch('http://localhost:8000/update', { method: 'POST' });
      alert('World updated!');
    } catch (error) {
      console.error('Error updating world:', error);
    }
  };

  return (
    <div className="App">
      <h1>Game Control Panel</h1>
      <div>
        <button onClick={fetchCurrentMap}>Fetch Current Map</button>
        <pre>{currentMap}</pre>
      </div>
      <div>
        <button onClick={addPlayer}>Add Player</button>
        <p>Player ID: {playerId}</p>
      </div>
      <div>
        <button onClick={() => movePlayer(1, 0)}>Move Player Right</button>
        <button onClick={() => movePlayer(-1, 0)}>Move Player Left</button>
        <button onClick={() => movePlayer(0, 1)}>Move Player Down</button>
        <button onClick={() => movePlayer(0, -1)}>Move Player Up</button>
        <p>Move Result: {moveResult}</p>
      </div>
      <div>
        <button onClick={updateWorld}>Update World</button>
      </div>
    </div>
  );
}

export default App;