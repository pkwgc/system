import { GameState } from '../types/game'
import { Card } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Slider } from '@/components/ui/slider'

interface PokerTableProps {
  gameState: GameState
  playerId: string
  onAction: (action: string, amount?: number) => void
  betAmount: number
  onBetChange: (amount: number) => void
}

export function PokerTable({ gameState, playerId, onAction, betAmount, onBetChange }: PokerTableProps) {
  const isCurrentPlayer = gameState.currentPlayer === playerId
  const currentPlayer = gameState.players[playerId]

  const renderPlayerSpot = (position: number) => {
    const player = Object.values(gameState.players).find(p => p.position === position)
    if (!player) return null

    return (
      <div key={position} className={`absolute ${getPositionClasses(position)}`}>
        <Card className="w-32 p-2 bg-gray-800">
          <div className="text-center">
            <div className="font-bold text-white">{player.name}</div>
            <div className="text-sm text-white">筹码: {player.chips}</div>
            {player.currentBet > 0 && (
              <div className="text-sm text-yellow-400">下注: {player.currentBet}</div>
            )}
          </div>
        </Card>
      </div>
    )
  }

  const getPositionClasses = (position: number): string => {
    const positions = {
      0: 'bottom-4 left-1/2 -translate-x-1/2',
      1: 'bottom-1/4 left-4',
      2: 'bottom-1/2 left-4',
      3: 'top-1/2 left-4',
      4: 'top-1/4 left-4',
      5: 'top-4 left-1/2 -translate-x-1/2',
      6: 'top-1/4 right-4',
      7: 'top-1/2 right-4',
      8: 'bottom-1/2 right-4'
    }
    return positions[position as keyof typeof positions] || ''
  }

  return (
    <div className="relative w-full aspect-video bg-green-800 rounded-full">
      {/* Community Cards */}
      <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 flex gap-2">
        {gameState.communityCards.map((card, index) => (
          <Card key={index} className="w-16 h-24 bg-white flex items-center justify-center text-xl">
            {card.rank}{card.suit === 'hearts' || card.suit === 'diamonds' ? '♥️' : '♠️'}
          </Card>
        ))}
      </div>

      {/* Player Positions */}
      {[0, 1, 2, 3, 4, 5, 6, 7, 8].map(position => renderPlayerSpot(position))}

      {/* Controls */}
      {isCurrentPlayer && (
        <div className="absolute bottom-0 left-1/2 transform -translate-x-1/2 mb-8 flex flex-col items-center gap-4 w-96">
          <Slider
            value={[betAmount]}
            min={gameState.minimumBet}
            max={currentPlayer.chips}
            step={1}
            onValueChange={([value]) => onBetChange(value)}
            className="w-full"
          />
          <div className="flex gap-2">
            <Button
              variant="destructive"
              onClick={() => onAction('fold')}
            >
              弃牌
            </Button>
            {gameState.canCheck && (
              <Button
                variant="secondary"
                onClick={() => onAction('check')}
              >
                让牌
              </Button>
            )}
            <Button
              variant="default"
              onClick={() => onAction('bet', betAmount)}
            >
              {betAmount === gameState.minimumBet ? '跟注' : '加注'} ({betAmount})
            </Button>
          </div>
        </div>
      )}
    </div>
  )
}
