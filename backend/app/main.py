from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from app.services.game import Game
from app.schemas import UserIs, BatterHas
from loguru import logger


class MoveRequest(BaseModel):
    move: int

class StartBowlingRequest(BaseModel):
    target_score: int

game = None

app = FastAPI(title="Hand Cricket API")

from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/start_batting")
def start_batting():
    global game
    game = Game(mode=UserIs.BATTING)
    logger.info("Game started in batting mode.")
    return {"message": "Game started in batting mode."}

@app.post("/start_bowling")
def start_bowling(request: StartBowlingRequest):
    global game
    game = Game(mode=UserIs.BOWLING, target=request.target_score)
    logger.info(f"Game started in bowling mode with target score {request.target_score}.")
    return {"message": f"Game started in bowling mode with target score {request.target_score}."}

@app.post("/move")
def make_move(request: MoveRequest) -> BatterHas:
    global game
    if game is None:
        raise HTTPException(status_code=400, detail="Game not started. Please start a game first.")
    
    try:
        result = game.step(user_move=request.move)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    
    return result


def main():
    import uvicorn
    logger.info("Starting Hand Cricket API server...")
    uvicorn.run(app, host="0.0.0.0", port=8000)


if __name__ == "__main__":
    main()