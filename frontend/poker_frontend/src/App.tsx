import { useState, useEffect, useCallback } from 'react'
import './App.css'

interface GameState {
  game_id: string;
  players: Record<string, string>;
}

function App() {
  const [playerName, setPlayerName] = useState('')
  const [gameId, setGameId] = useState('')
  const [playerId, setPlayerId] = useState<string | null>(null)
  const [gameState, setGameState] = useState<GameState | null>(null)
  const [ws, setWs] = useState<WebSocket | null>(null)
  const [error, setError] = useState<string | null>(null)

  const connectWebSocket = useCallback((gameId: string, playerId: string) => {
    const wsUrl = `ws://localhost:8000/ws/${gameId}/${playerId}`
    const newWs = new WebSocket(wsUrl)

    newWs.onopen = () => {
      console.log('WebSocket connected')
      setError(null)
    }

    newWs.onmessage = (event) => {
      const data = JSON.parse(event.data)
      setGameState(data)
    }

    newWs.onerror = (event) => {
      console.error('WebSocket error:', event)
      setError('Connection error')
    }

    newWs.onclose = () => {
      console.log('WebSocket disconnected')
      setWs(null)
      // Attempt to reconnect after 1 second
      setTimeout(() => {
        if (gameId && playerId) {
          connectWebSocket(gameId, playerId)
        }
      }, 1000)
    }

    setWs(newWs)
    return newWs
  }, [])

  useEffect(() => {
    return () => {
      if (ws) {
        ws.close()
      }
    }
  }, [ws])

  const createGame = async () => {
    if (!playerName) {
      setError('Please enter your name')
      return
    }

    try {
      const response = await fetch('http://localhost:8000/game/create', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ player_name: playerName }),
      })

      if (!response.ok) {
        throw new Error('Failed to create game')
      }

      const data = await response.json()
      setGameId(data.game_id)
      setPlayerId(data.player_id)
      setGameState(data.game_state)
      connectWebSocket(data.game_id, data.player_id)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to create game')
    }
  }

  const joinGame = async () => {
    if (!playerName || !gameId) {
      setError('Please enter your name and game ID')
      return
    }

    try {
      const response = await fetch(`http://localhost:8000/game/${gameId}/join`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ player_name: playerName }),
      })

      if (!response.ok) {
        throw new Error('Failed to join game')
      }

      const data = await response.json()
      setPlayerId(data.player_id)
      setGameState(data.game_state)
      connectWebSocket(gameId, data.player_id)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to join game')
    }
  }

  return (
    <div className="container">
      <h1>Texas Hold'em Poker</h1>
      {error && <div className="error">{error}</div>}

      {!playerId ? (
        <div className="join-form">
          <input
            type="text"
            placeholder="Enter your name"
            value={playerName}
            onChange={(e) => setPlayerName(e.target.value)}
          />
          <input
            type="text"
            placeholder="Game ID (for joining)"
            value={gameId}
            onChange={(e) => setGameId(e.target.value)}
          />
          <div className="buttons">
            <button onClick={createGame}>Create Game</button>
            <button onClick={joinGame}>Join Game</button>
          </div>
        </div>
      ) : (
        <div className="game-container">
          <h2>Game ID: {gameId}</h2>
          <div className="players">
            <h3>Players:</h3>
            {gameState && Object.entries(gameState.players).map(([id, name]) => (
              <div key={id} className="player">
                {name} {id === playerId && '(You)'}
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}

export default App
