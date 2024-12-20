from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, List, Optional
import uuid
import json

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class Player(BaseModel):
    player_name: str

class GameState:
    def __init__(self, game_id: str):
        self.game_id = game_id
        self.players: Dict[str, str] = {}  # player_id -> player_name
        self.active_connections: Dict[str, WebSocket] = {}  # player_id -> websocket

    def add_player(self, player_name: str) -> str:
        player_id = str(uuid.uuid4())
        self.players[player_id] = player_name
        return player_id

    def remove_player(self, player_id: str):
        if player_id in self.players:
            del self.players[player_id]
        if player_id in self.active_connections:
            del self.active_connections[player_id]

    async def broadcast_state(self):
        if not self.active_connections:
            return

        state_data = {
            "game_id": self.game_id,
            "players": self.players
        }

        for connection in self.active_connections.values():
            try:
                await connection.send_json(state_data)
            except Exception as e:
                print(f"Error broadcasting state: {e}")

active_games: Dict[str, GameState] = {}

@app.post("/game/create")
async def create_game(player: Player):
    game_id = str(uuid.uuid4())
    game_state = GameState(game_id)
    player_id = game_state.add_player(player.player_name)
    active_games[game_id] = game_state

    return {
        "game_id": game_id,
        "player_id": player_id,
        "game_state": {
            "players": game_state.players
        }
    }

@app.post("/game/{game_id}/join")
async def join_game(game_id: str, player: Player):
    if game_id not in active_games:
        raise HTTPException(status_code=404, detail="Game not found")

    game_state = active_games[game_id]
    player_id = game_state.add_player(player.player_name)

    return {
        "player_id": player_id,
        "game_state": {
            "players": game_state.players
        }
    }

@app.websocket("/ws/{game_id}/{player_id}")
async def websocket_endpoint(websocket: WebSocket, game_id: str, player_id: str):
    if game_id not in active_games:
        await websocket.close(code=4000)
        return

    game_state = active_games[game_id]
    if player_id not in game_state.players:
        await websocket.close(code=4001)
        return

    await websocket.accept()
    game_state.active_connections[player_id] = websocket

    try:
        await game_state.broadcast_state()

        while True:
            data = await websocket.receive_text()
            await game_state.broadcast_state()

    except WebSocketDisconnect:
        game_state.remove_player(player_id)
        await game_state.broadcast_state()
