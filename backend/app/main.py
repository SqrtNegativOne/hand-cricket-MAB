from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from app.services.game import HandCricketGame
from loguru import logger


class MoveRequest(BaseModel):
    move: int

class StartBowlingRequest(BaseModel):
    target_score: int


game = HandCricketGame()

app = FastAPI(title="Hand Cricket API")

from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/start/batting")
def start_batting():
    game.start_batting()
    return {"message": "Player batting started. You have 3 lives."}


@app.post("/start/bowling")
def start_bowling(req: StartBowlingRequest):
    game.start_bowling(req.target_score)
    return {"message": f"AI batting started. Target: {req.target_score}"}


@app.post("/move")
def play_move(req: MoveRequest):
    try:
        result = game.step(req.move)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/score")
def get_score():
    return {
        "player_score": game.player_score,
        "computer_score": game.computer_score,
        "strikes": game.strikes,
        "mode": game.mode,
    }


def main():
    import uvicorn
    logger.info("Starting Hand Cricket API server...")
    uvicorn.run(app, host="0.0.0.0", port=8000)


if __name__ == "__main__":
    main()