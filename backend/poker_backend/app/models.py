from enum import Enum
from typing import List, Optional, Dict
from pydantic import BaseModel

class Suit(str, Enum):
    HEARTS = "hearts"
    DIAMONDS = "diamonds"
    CLUBS = "clubs"
    SPADES = "spades"

class Card(BaseModel):
    suit: Suit
    rank: int  # 2-14 (14 = Ace)

    def __str__(self):
        ranks = {11: 'J', 12: 'Q', 13: 'K', 14: 'A'}
        rank_str = ranks.get(self.rank, str(self.rank))
        return f"{rank_str}{self.suit.value[0].upper()}"

class PlayerState(str, Enum):
    WAITING = "waiting"
    ACTIVE = "active"
    FOLDED = "folded"
    ALL_IN = "all_in"

class Player(BaseModel):
    id: str
    name: str
    chips: int
    state: PlayerState = PlayerState.WAITING
    cards: List[Card] = []
    current_bet: int = 0
    position: int

class GamePhase(str, Enum):
    WAITING = "waiting"
    PREFLOP = "preflop"
    FLOP = "flop"
    TURN = "turn"
    RIVER = "river"
    SHOWDOWN = "showdown"

class GameState(BaseModel):
    id: str
    players: Dict[str, Player]
    deck: List[Card] = []
    community_cards: List[Card] = []
    current_phase: GamePhase = GamePhase.WAITING
    pot: int = 0
    current_player_position: Optional[int] = None
    dealer_position: int = 0
    min_bet: int = 0
    last_raise: int = 0
    small_blind: int = 10
    big_blind: int = 20
