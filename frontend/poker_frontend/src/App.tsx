import { useState, useEffect } from 'react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Card } from '@/components/ui/card'
import { GameState } from './types/game'
import { PokerTable } from './components/PokerTable'

function App() {
  const [gameId, setGameId] = useState<string>('')
  const [playerName, setPlayerName] = useState<string>('')
  const [playerId, setPlayerId] = useState<string>('')
  const [gameState, setGameState] = useState<GameState | null>(null)
  const [betAmount, setBetAmount] = useState<number>(0)
  const [ws, setWs] = useState<WebSocket | null>(null)

  const createGame = async () => {
    try {
      console.log('Attempting to create game...');
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
  }

  const joinGame = async () => {
    try {
      console.log('Attempting to join game...');
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
  }

  const setupWebSocket = (gameId: string, playerId: string) => {
    const wsUrl = `${import.meta.env.VITE_WS_URL}/ws/${gameId}/${playerId}`
    const websocket = new WebSocket(wsUrl)

    websocket.onmessage = (event) => {
      const data = JSON.parse(event.data)
      if (data.type === 'game_state') {
        setGameState(data.data)
        setBetAmount(data.data.minimumBet)
      }
    }

    websocket.onerror = (error) => {
      console.error('WebSocket error:', error)
    }

    websocket.onclose = () => {
      console.log('WebSocket disconnected')
      setTimeout(() => setupWebSocket(gameId, playerId), 1000)
    }

    setWs(websocket)
  }

  const sendAction = (action: string, amount: number = 0) => {
    if (ws && ws.readyState === WebSocket.OPEN) {
      ws.send(JSON.stringify({ action, amount }))
    }
  }

  useEffect(() => {
    return () => {
      if (ws) {
        ws.close()
      }
    }
  }, [ws])

  if (!gameState) {
    return (
      <div className="min-h-screen bg-gray-900 text-white flex items-center justify-center">
        <Card className="w-96 p-6 bg-gray-800">
          <h1 className="text-2xl font-bold mb-4">德州扑克</h1>
          <div className="space-y-4">
            <Input
              placeholder="玩家名称"
              value={playerName}
              onChange={(e) => setPlayerName(e.target.value)}
              className="bg-gray-700 text-white"
            />
            <Input
              placeholder="游戏ID (可选)"
              value={gameId}
              onChange={(e) => setGameId(e.target.value)}
              className="bg-gray-700 text-white"
            />
            <div className="flex gap-2">
              <Button onClick={createGame} className="flex-1">
                创建游戏
              </Button>
              <Button onClick={joinGame} className="flex-1" disabled={!gameId || !playerName}>
                加入游戏
              </Button>
            </div>
          </div>
        </Card>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-900 text-white p-4">
      <div className="container mx-auto">
        <div className="text-center mb-4">
          <h2 className="text-xl">游戏ID: {gameState.id}</h2>
          <p>当前奖池: {gameState.pot}</p>
        </div>
        <PokerTable
          gameState={gameState}
          playerId={playerId}
          onAction={sendAction}
          betAmount={betAmount}
          onBetChange={setBetAmount}
        />
      </div>
    </div>
  )
}

export default App
