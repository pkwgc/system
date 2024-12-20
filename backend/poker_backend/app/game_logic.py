import random
from typing import List, Dict, Tuple, Optional
from .models import Card, Suit, Player, GameState, PlayerState, GamePhase

class PokerGame:
    def __init__(self, game_state: GameState):
        self.state = game_state

    def initialize_deck(self):
        """Create and shuffle a new deck of cards."""
        self.state.deck = []
        for suit in Suit:
            for rank in range(2, 15):  # 2 through Ace (14)
                self.state.deck.append(Card(suit=suit, rank=rank))
        random.shuffle(self.state.deck)

    def deal_cards(self):
        """Deal two cards to each active player."""
        if not self.state.deck:
            self.initialize_deck()

        for player in self.state.players.values():
            if player.state != PlayerState.FOLDED:
                player.cards = [self.state.deck.pop() for _ in range(2)]

    def deal_community_cards(self, count: int):
        """Deal specified number of community cards."""
        self.state.community_cards.extend([self.state.deck.pop() for _ in range(count)])

    def evaluate_hand(self, player: Player) -> Tuple[int, List[Card]]:
        """Evaluate the best poker hand for a player."""
        all_cards = player.cards + self.state.community_cards
        return self._find_best_hand(all_cards)

    def _find_best_hand(self, cards: List[Card]) -> Tuple[int, List[Card]]:
        """Find the best 5-card hand from given cards."""
        all_combinations = self._get_all_combinations(cards)
        best_score = 0
        best_hand = []

        for hand in all_combinations:
            score = self._score_hand(hand)
            if score > best_score:
                best_score = score
                best_hand = hand

        return best_score, best_hand

    def _score_hand(self, cards: List[Card]) -> int:
        """Score a 5-card poker hand."""
        if len(cards) != 5:
            return 0

        # Sort cards by rank
        sorted_cards = sorted(cards, key=lambda x: x.rank, reverse=True)

        # Check for flush
        is_flush = len(set(card.suit for card in cards)) == 1

        # Check for straight
        ranks = [card.rank for card in sorted_cards]
        is_straight = (max(ranks) - min(ranks) == 4 and len(set(ranks)) == 5) or \
                     (ranks == [14, 5, 4, 3, 2])  # Ace-low straight

        # Count rank frequencies
        rank_counts = {}
        for card in cards:
            rank_counts[card.rank] = rank_counts.get(card.rank, 0) + 1

        # Score based on hand type
        if is_straight and is_flush:
            return 8000000 + max(ranks)  # Straight flush
        elif 4 in rank_counts.values():
            return 7000000 + max(r for r, c in rank_counts.items() if c == 4)  # Four of a kind
        elif set(rank_counts.values()) == {2, 3}:
            return 6000000 + max(r for r, c in rank_counts.items() if c == 3)  # Full house
        elif is_flush:
            return 5000000 + sum(r * 100**i for i, r in enumerate(ranks))  # Flush
        elif is_straight:
            return 4000000 + max(ranks)  # Straight
        elif 3 in rank_counts.values():
            return 3000000 + max(r for r, c in rank_counts.items() if c == 3)  # Three of a kind
        elif list(rank_counts.values()).count(2) == 2:
            pairs = sorted([r for r, c in rank_counts.items() if c == 2], reverse=True)
            return 2000000 + pairs[0] * 100 + pairs[1]  # Two pair
        elif 2 in rank_counts.values():
            return 1000000 + max(r for r, c in rank_counts.items() if c == 2)  # One pair
        else:
            return sum(r * 100**i for i, r in enumerate(ranks))  # High card

    def _get_all_combinations(self, cards: List[Card]) -> List[List[Card]]:
        """Get all possible 5-card combinations from the given cards."""
        if len(cards) < 5:
            return []

        def _combinations(cards: List[Card], r: int) -> List[List[Card]]:
            if r == 0:
                return [[]]
            if not cards:
                return []
            result = []
            for i, card in enumerate(cards):
                for combo in _combinations(cards[i + 1:], r - 1):
                    result.append([card] + combo)
            return result


        return _combinations(cards, 5)

    def process_bet(self, player_id: str, amount: int) -> bool:
        """Process a bet from a player."""
        player = self.state.players.get(player_id)
        if not player or player.chips < amount:
            return False

        player.chips -= amount
        player.current_bet += amount
        self.state.pot += amount
        self.state.last_raise = max(self.state.last_raise, amount)
        return True

    def next_player(self) -> Optional[str]:
        """Get the next active player in the game."""
        active_players = [p for p in self.state.players.values()
                         if p.state in (PlayerState.ACTIVE, PlayerState.ALL_IN)]
        if not active_players:
            return None

        current_pos = self.state.current_player_position or 0
        positions = sorted(p.position for p in active_players)

        next_pos = next((pos for pos in positions if pos > current_pos), positions[0])
        self.state.current_player_position = next_pos

        return next(p.id for p in active_players if p.position == next_pos)

    def advance_phase(self) -> None:
        """Advance to the next phase of the game."""
        phase_order = [
            GamePhase.WAITING,
            GamePhase.PREFLOP,
            GamePhase.FLOP,
            GamePhase.TURN,
            GamePhase.RIVER,
            GamePhase.SHOWDOWN
        ]

        current_index = phase_order.index(self.state.current_phase)
        if current_index < len(phase_order) - 1:
            self.state.current_phase = phase_order[current_index + 1]

            if self.state.current_phase == GamePhase.FLOP:
                self.deal_community_cards(3)
            elif self.state.current_phase in (GamePhase.TURN, GamePhase.RIVER):
                self.deal_community_cards(1)
            elif self.state.current_phase == GamePhase.SHOWDOWN:
                self._handle_showdown()

    def _handle_showdown(self) -> Dict[str, int]:
        """Handle showdown and return pot distribution."""
        active_players = {
            player_id: player
            for player_id, player in self.state.players.items()
            if player.state in (PlayerState.ACTIVE, PlayerState.ALL_IN)
        }

        # Evaluate hands for all active players
        hand_scores = {
            player_id: self.evaluate_hand(player)[0]
            for player_id, player in active_players.items()
        }

        # Find winners
        max_score = max(hand_scores.values())
        winners = [pid for pid, score in hand_scores.items() if score == max_score]

        # Split pot among winners
        pot_share = self.state.pot // len(winners)
        pot_distribution = {winner: pot_share for winner in winners}

        # Update player chips
        for player_id, amount in pot_distribution.items():
            self.state.players[player_id].chips += amount

        self.state.pot = 0
        return pot_distribution
