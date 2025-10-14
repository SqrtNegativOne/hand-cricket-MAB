import torch
import pprint

import services.bowlers as bowlers
import services.batters as batters


DEBUG_MODE = False


def bowling_loss_fn(player_move, comp_move):
    return 0 if player_move == comp_move else player_move


class MultiArmedBandit: # Experts-as-Arms
    def __init__(self, mode, lr=0.1):
        if mode == "bowling":
            self.agents = bowlers.bowlers
        elif mode == "batting":
            self.agents = batters.batters
        else:
            raise ValueError("Invalid mode. Choose 'bowling' or 'batting'.")
        self.mode = mode
        self.num_agents = len(self.agents)
        self.weights = torch.zeros(self.num_agents, dtype=torch.float32) # Log-counts
        self.lr = lr
    
    def select_agent(self) -> bowlers.Agent:
        probs = torch.softmax(self.weights, dim=0)
        idx = int(torch.multinomial(probs, num_samples=1).item())
        return self.agents[idx]

    def select_arm(self, self_history, adversary_history) -> int:
        return self.select_agent().step(self_history, adversary_history)

    def update(self, player_history, computer_history) -> None:
        if not player_history or not computer_history: return

        # Get losses
        losses = torch.zeros(self.num_agents, dtype=torch.float32)
        for i, agent in enumerate(self.agents):
            # Use history_step instead of step to avoid the update(); we wouldn't want the agent we just played to update twice.
            agent_arm = agent.step(computer_history[:-1], player_history[:-1]) # Forward pass on the history, excluding the last move.
            losses[i] = bowling_loss_fn(player_history[-1], agent_arm)                 # Test on last move
            if self.mode == "batting": losses[i] = -losses[i]

            agent.update(computer_history, player_history) # Update the agent with the full history

        
        self.weights -= self.lr * losses

        if DEBUG_MODE:
            print()
            print(f"{player_history=}")
            print(f"{computer_history=}")
            pprint.pprint({str(agent) : loss.item() for agent, loss in zip(self.agents, losses)})
            pprint.pprint({str(agent) : round(weight.item()*100, 2) for agent, weight in zip(self.agents, torch.softmax(self.weights, dim=0))}) # Updated weights
            print()


class HandCricketGame:
    def __init__(self):
        self.player_score = 0
        self.computer_score = 0
        self.player_history = []
        self.computer_history = []
        self.strikes = 0
        self.bandit = None
        self.mode = None

    def start_batting(self):
        self.mode = "batting"
        self.bandit = MultiArmedBandit(mode="bowling", lr=0.1)
        self.player_score = 0
        self.computer_score = 0
        self.strikes = 0
        self.player_history = []
        self.computer_history = []

    def start_bowling(self, target_score):
        self.mode = "bowling"
        self.bandit = MultiArmedBandit(mode="batting", lr=0.1)
        self.player_score = target_score
        self.computer_score = 0
        self.strikes = 0
        self.player_history = []
        self.computer_history = []

    def step(self, player_move: int):
        if player_move < 1 or player_move > 6:
            raise ValueError("Move must be between 1 and 6")
        
        if self.bandit is None:
            raise ValueError("Game not started. Call start_batting or start_bowling first.")

        comp_move = self.bandit.select_arm(
            self.computer_history if self.mode == "bowling" else self.player_history,
            self.player_history if self.mode == "bowling" else self.computer_history,
        )

        self.player_history.append(player_move)
        self.computer_history.append(comp_move)

        result = {"player_move": player_move, "comp_move": comp_move}

        # Player batting
        if self.mode == "batting":
            if player_move == comp_move:
                self.strikes += 1
                result["out"] = True
                if self.strikes >= 3:
                    result["game_over"] = True
                else:
                    result["game_over"] = False
            else:
                self.player_score += player_move
                result["out"] = False
                result["score"] = self.player_score
        # Player bowling
        else:
            if player_move == comp_move:
                self.strikes += 1
                result["out"] = True
                if self.strikes >= 3:
                    result["game_over"] = True
                else:
                    result["game_over"] = False
            else:
                self.computer_score += comp_move
                result["out"] = False
                result["score"] = self.computer_score
                result["to_chase"] = max(self.player_score - self.computer_score, 0)
                if self.computer_score > self.player_score:
                    result["game_over"] = True

        self.bandit.update(self.player_history, self.computer_history)
        return result