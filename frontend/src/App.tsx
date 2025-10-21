import React, { useState } from "react";
import axios from "axios";

interface MoveResponse {
  name: string; // Enum name, e.g., "Scored4", "Out", "Lost", "Won"
}

const API_BASE = "http://localhost:8000";

const App: React.FC = () => {
  const [gameMode, setGameMode] = useState<"batting" | "bowling" | null>(null);
  const [targetScore, setTargetScore] = useState<number>(-1);
  const [runs, setRuns] = useState<number>(0);
  const [wickets, setWickets] = useState<number>(5);
  const [message, setMessage] = useState<string>("Welcome! Choose a mode to start.");
  const [gameActive, setGameActive] = useState<boolean>(false);

  const startBatting = async () => {
    try {
      await axios.post(`${API_BASE}/start_batting`);
      setGameMode("batting");
      resetGameState();
      setMessage("Game started in batting mode.");
      setGameActive(true);
    } catch (err) {
      console.error(err);
      setMessage("Failed to start batting mode.");
    }
  };

  const startBowling = async () => {
    if (targetScore < 1) {
      setMessage("Please enter a valid target score.");
      return;
    }
    try {
      await axios.post(`${API_BASE}/start_bowling`, { target_score: targetScore });
      setGameMode("bowling");
      resetGameState();
      setMessage(`Game started in bowling mode (target = ${targetScore}).`);
      setGameActive(true);
    } catch (err) {
      console.error(err);
      setMessage("Failed to start bowling mode.");
    }
  };

  const resetGameState = () => {
    setRuns(0);
    setWickets(5);
  };

  const makeMove = async (move: number) => {
    try {
      const response = await axios.post<MoveResponse>(`${API_BASE}/move`, { move });
      const result = response.data.name;

      if (result === "Out") {
        setWickets((prev) => prev - 1);
        setMessage("You're out!");
      } else if (result === "Lost") {
        setGameActive(false);
        setMessage("Game Over. You lost.");
      } else if (result === "Won") {
        setGameActive(false);
        setMessage("You won!");
      } else {
        const scored = parseInt(result.replace("Scored", ""), 10);
        if (!isNaN(scored)) setRuns((prev) => prev + scored);
        setMessage(`You ${result.toLowerCase()}.`);
      }
    } catch (err: any) {
      setMessage(err.response?.data?.detail || "Error making move.");
    }
  };

  return (
    <div className="min-h-screen bg-gray-100 text-gray-900 flex flex-col items-center p-6">
      <h1 className="text-3xl font-bold mb-6">Cricket Game</h1>

      {!gameActive && (
        <div className="mb-8 space-y-4">
          <button
            onClick={startBatting}
            className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
          >
            Start Batting
          </button>

          <div className="flex items-center space-x-3">
            <input
              type="number"
              value={targetScore === -1 ? "" : targetScore}
              onChange={(e) => setTargetScore(Number(e.target.value))}
              placeholder="Target Score"
              className="border px-3 py-2 rounded-md"
            />
            <button
              onClick={startBowling}
              className="px-6 py-3 bg-green-600 text-white rounded-lg hover:bg-green-700"
            >
              Start Bowling
            </button>
          </div>
        </div>
      )}

      <div className="text-lg mb-4">{message}</div>

      {gameActive && (
        <>
          <div className="mb-4 text-center">
            <div>Mode: <strong>{gameMode}</strong></div>
            <div>Runs: <strong>{runs}</strong></div>
            <div>Wickets Left: <strong>{wickets}</strong></div>
            {gameMode === "bowling" && targetScore > 0 && (
              <div>Target: <strong>{targetScore}</strong></div>
            )}
          </div>

          <div className="grid grid-cols-3 gap-3">
            {[1, 2, 3, 4, 5, 6].map((n) => (
              <button
                key={n}
                onClick={() => makeMove(n)}
                className="px-6 py-3 bg-gray-800 text-white rounded-lg hover:bg-gray-900"
              >
                {n}
              </button>
            ))}
          </div>
        </>
      )}
    </div>
  );
};

export default App;
