from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict, Optional
import json
import uuid
import psycopg
from .models import GameState, Player, PlayerState, GamePhase
from .game_logic import PokerGame

# In-memory storage for active games
active_games: Dict[str, PokerGame] = {}

app = FastAPI()

# Disable CORS. Do not remove this for full-stack development.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

# WebSocket connections store
connections: Dict[str, WebSocket] = {}

@app.get("/healthz")
async def healthz():
    return {"status": "ok"}

@app.post("/game/create")
async def create_game():
    game_id = str(uuid.uuid4())
    game_state = GameState(
        id=game_id,
        players={},
        current_phase=GamePhase.WAITING,
        dealer_position=0
    )
    active_games[game_id] = PokerGame(game_state)
    return {"game_id": game_id}

@app.post("/game/{game_id}/join")
async def join_game(game_id: str, player: dict):
    if game_id not in active_games:
        raise HTTPException(status_code=404, detail="Game not found")

    game = active_games[game_id]
    if len(game.state.players) >= 9:
        raise HTTPException(status_code=400, detail="Game is full")

    player_name = player.get("player_name")
    if not player_name:
        raise HTTPException(status_code=422, detail="player_name is required")

    player_id = str(uuid.uuid4())
    position = len(game.state.players)

    new_player = Player(
        id=player_id,
        name=player_name,
        chips=1000,  # Starting chips
        position=position,
        state=PlayerState.WAITING
    )

    game.state.players[player_id] = new_player
    return {"player_id": player_id, "game_state": game.state}

@app.websocket("/ws/{game_id}/{player_id}")
async def websocket_endpoint(websocket: WebSocket, game_id: str, player_id: str):
    await websocket.accept()
    connections[player_id] = websocket

    try:
        while True:
            data = await websocket.receive_json()
            game = active_games.get(game_id)
            if not game:
                await websocket.close()
                break

            action = data.get("action")
            if action == "bet":
                amount = data.get("amount", 0)
                if game.process_bet(player_id, amount):
                    await broadcast_game_state(game_id)
            elif action == "fold":
                player = game.state.players.get(player_id)
                if player:
                    player.state = PlayerState.FOLDED
                    await broadcast_game_state(game_id)
            elif action == "check":
                next_player = game.next_player()
                if next_player:
                    await broadcast_game_state(game_id)
            elif action == "start_game":
                if len(game.state.players) >= 2:
                    game.initialize_deck()
                    game.deal_cards()
                    game.state.current_phase = GamePhase.PREFLOP
                    await broadcast_game_state(game_id)

    except WebSocketDisconnect:
        if player_id in connections:
            del connections[player_id]
        await handle_player_disconnect(game_id, player_id)

async def broadcast_game_state(game_id: str):
    """Broadcast the current game state to all connected players."""
    game = active_games.get(game_id)
    if not game:
        return

    for player_id, websocket in connections.items():
        player_view = create_player_view(game, player_id)
        try:
            await websocket.send_json({"type": "game_state", "data": player_view})
        except WebSocketDisconnect:
            continue

def create_player_view(game: PokerGame, player_id: str) -> dict:
    """Create a player-specific view of the game state."""
    state_dict = game.state.dict()
    for pid, player in state_dict["players"].items():
        if pid != player_id:
            player["cards"] = [None] * len(player["cards"])
    return state_dict

async def handle_player_disconnect(game_id: str, player_id: str):
    """Handle cleanup when a player disconnects."""
    game = active_games.get(game_id)
    if game and player_id in game.state.players:
        game.state.players[player_id].state = PlayerState.FOLDED
        await broadcast_game_state(game_id)
