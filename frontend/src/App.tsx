import { useState, useEffect } from "react";
import axios from "axios";

const API_BASE = "http://localhost:8000"; // change if backend runs elsewhere

export default function App() {
  const [mode, setMode] = useState(null);
  const [targetScore, setTargetScore] = useState("");
  const [move, setMove] = useState("");
  const [message, setMessage] = useState("");
  const [gameState, setGameState] = useState({
    player_score: 0,
    computer_score: 0,
    strikes: 0,
    mode: null,
  });

  const fetchScore = async () => {
    try {
      const res = await axios.get(`${API_BASE}/score`);
      setGameState(res.data);
    } catch {
      setMessage("Failed to fetch score.");
    }
  };

  useEffect(() => {
    fetchScore();
  }, []);

  const startBatting = async () => {
    try {
      const res = await axios.post(`${API_BASE}/start/batting`);
      setMessage(res.data.message);
      setMode("batting");
      fetchScore();
    } catch {
      setMessage("Failed to start batting.");
    }
  };

  const startBowling = async () => {
    if (!targetScore) return setMessage("Enter a target score.");
    try {
      const res = await axios.post(`${API_BASE}/start/bowling`, {
        target_score: parseInt(targetScore),
      });
      setMessage(res.data.message);
      setMode("bowling");
      fetchScore();
    } catch {
      setMessage("Failed to start bowling.");
    }
  };

  const makeMove = async () => {
    if (!move) return setMessage("Enter your move (1–6).");
    try {
      const res = await axios.post(`${API_BASE}/move`, { move: parseInt(move) });
      setMessage(JSON.stringify(res.data));
      fetchScore();
    } catch (e) {
      setMessage(e.response?.data?.detail || "Invalid move.");
    }
  };

  return (
    <div className="min-h-screen bg-gray-100 text-gray-900 flex flex-col items-center p-8 space-y-6">
      <h1 className="text-2xl font-bold">Hand Cricket Game</h1>

      <div className="space-x-4">
        <button
          onClick={startBatting}
          className="bg-blue-600 text-white px-4 py-2 rounded"
        >
          Start Batting
        </button>
        <input
          type="number"
          placeholder="Target Score"
          value={targetScore}
          onChange={(e) => setTargetScore(e.target.value)}
          className="border p-2 rounded"
        />
        <button
          onClick={startBowling}
          className="bg-green-600 text-white px-4 py-2 rounded"
        >
          Start Bowling
        </button>
      </div>

      <div className="flex space-x-2 items-center">
        <input
          type="number"
          placeholder="Your Move"
          value={move}
          onChange={(e) => setMove(e.target.value)}
          className="border p-2 rounded"
        />
        <button
          onClick={makeMove}
          className="bg-gray-800 text-white px-4 py-2 rounded"
        >
          Play Move
        </button>
      </div>

      <div className="border p-4 rounded w-80 bg-white shadow">
        <h2 className="text-lg font-semibold mb-2">Game Status</h2>
        <p>Mode: {gameState.mode || "N/A"}</p>
        <p>Player Score: {gameState.player_score}</p>
        <p>Computer Score: {gameState.computer_score}</p>
        <p>Strikes: {gameState.strikes}</p>
      </div>

      <div className="text-sm text-gray-700 whitespace-pre-wrap">
        {message}
      </div>
    </div>
  );
}
