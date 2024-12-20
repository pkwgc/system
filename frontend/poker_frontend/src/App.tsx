import { useState, useEffect, useCallback } from 'react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Card } from '@/components/ui/card'
import './App.css'
import { GameState } from './types/game'

function App() {
  const [playerName, setPlayerName] = useState('')
  const [gameId, setGameId] = useState('')
  const [playerId, setPlayerId] = useState('')
  const [gameState, setGameState] = useState<GameState | null>(null)
  const [ws, setWs] = useState<WebSocket | null>(null)

  console.log('App rendered with:', { playerName, gameId, playerId, gameState })

  const createGame = useCallback(async () => {
    try {
      console.log('Attempting to create game with player name:', playerName)
      if (!playerName) {
        console.error('Player name is required')
        return
      }
      const response = await fetch(`${import.meta.env.VITE_API_URL}/game/create`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'application/json'
        },
        body: JSON.stringify({ player_name: playerName })
      });
      console.log('Create game response status:', response.status);
      const data = await response.json();
      console.log('Create game response data:', data);
      setGameId(data.game_id);
      setPlayerId(data.player_id);
      setGameState(data.game_state);
      setupWebSocket(data.game_id, data.player_id);
    } catch (error) {
      console.error('Failed to create game:', error);
    }
  }, [playerName])

  const joinGame = useCallback(async () => {
    try {
      console.log('Attempting to join game...')
      if (!playerName || !gameId) {
        console.error('Player name and game ID are required')
        return
      }
      const response = await fetch(`${import.meta.env.VITE_API_URL}/game/${gameId}/join`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'application/json'
        },
        body: JSON.stringify({ player_name: playerName })
      });
      console.log('Join game response status:', response.status);
      const data = await response.json();
      console.log('Join game response data:', data);
      setPlayerId(data.player_id);
      setGameState(data.game_state);
      setupWebSocket(gameId, data.player_id);
    } catch (error) {
      console.error('Failed to join game:', error);
    }
  }, [playerName, gameId])

  const setupWebSocket = useCallback((gameId: string, playerId: string) => {
    console.log('Setting up WebSocket connection...')
    if (!gameId || !playerId) {
      console.error('Game ID and Player ID are required for WebSocket connection')
      return
    }
    const wsUrl = `${import.meta.env.VITE_WS_URL}/ws/${gameId}/${playerId}`
    console.log('WebSocket URL:', wsUrl)
    const websocket = new WebSocket(wsUrl)

    websocket.onmessage = (event) => {
      console.log('WebSocket message received:', event.data)
      const data = JSON.parse(event.data)
      setGameState(data)
    }

    websocket.onerror = (error) => {
      console.error('WebSocket error:', error)
    }

    websocket.onclose = () => {
      console.log('WebSocket connection closed')
      setWs(null)
    }

    setWs(websocket)
  }, [])

  useEffect(() => {
    return () => {
      if (ws) {
        ws.close()
      }
    }
  }, [ws])

  return (
    <div className="container mx-auto p-4">
      <h1 className="text-2xl font-bold mb-4">德州扑克</h1>
      <div className="space-y-4">
        <Input
          type="text"
          placeholder="玩家名称"
          value={playerName}
          onChange={(e) => setPlayerName(e.target.value)}
        />
        <Input
          type="text"
          placeholder="游戏ID (可选)"
          value={gameId}
          onChange={(e) => setGameId(e.target.value)}
        />
        <div className="space-x-4">
          <Button onClick={createGame} disabled={!playerName}>
            创建游戏
          </Button>
          <Button onClick={joinGame} disabled={!playerName || !gameId}>
            加入游戏
          </Button>
        </div>
        {gameState && (
          <Card className="p-4">
            <pre>{JSON.stringify(gameState, null, 2)}</pre>
          </Card>
        )}
      </div>
    </div>
  )
}

export default App
