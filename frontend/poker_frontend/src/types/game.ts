export interface Card {
  suit: 'hearts' | 'diamonds' | 'clubs' | 'spades';
  rank: string;
}

export interface Player {
  id: string;
  name: string;
  chips: number;
  cards: Card[];
  position: number;
  state: 'WAITING' | 'PLAYING' | 'FOLDED';
  currentBet: number;
}

export interface GameState {
  id: string;
  players: Record<string, Player>;
  communityCards: Card[];
  pot: number;
  currentPlayer: string;
  minimumBet: number;
  canCheck: boolean;
}
