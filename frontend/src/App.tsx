import { useState, useEffect } from "react";
import axios from "axios";

const API_BASE = "http://localhost:8000"; // change if backend runs elsewhere

enum GameMode {
    DecideInitMode = "decide_init_mode",
    Batting = "batting",
    Bowling = "bowling",
    GameOver = "game_over",
}

export default function App() {
    const [mode, setMode] = useState<GameMode>(GameMode.DecideInitMode);
    const [targetScore, setTargetScore] = useState<number | undefined>();
    const [move, setMove] = useState<number | undefined>();
    const [gameState, setGameState] = useState({
        player_score: 0,
        computer_score: 0,
        strikes: 0,
        mode: GameMode.DecideInitMode,
    });

    

    return (
        <h1>Hand Cricket</h1>

    )
}
