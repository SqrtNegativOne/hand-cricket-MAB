import torch
import app.services.bowlers as bowlers
import app.services.batters as batters
from app.schemas import UserIs
from loguru import logger


def bowling_loss_fn(player_move, comp_move):
    return 0 if player_move == comp_move else player_move


class MultiArmedBandit: # Experts-as-Arms
    def __init__(self, mode: UserIs, lr: float = 0.1):
        if mode == UserIs.BOWLING:
            self.agents = bowlers.bowlers
        elif mode == UserIs.BATTING:
            self.agents = batters.batters
        else:
            raise ValueError("Invalid mode. Choose 'bowling' or 'batting'.")
        self.mode = mode
        self.num_agents = len(self.agents)
        self.weights = torch.zeros(self.num_agents, dtype=torch.float32) # Log-counts
        self.lr = lr
    
    def _select_agent(self) -> bowlers.Agent:
        probs = torch.softmax(self.weights, dim=0)
        idx = int(torch.multinomial(probs, num_samples=1).item())
        return self.agents[idx]

    def select_arm(self, comp_history, user_history) -> int: # The user is the adversary.
        return self._select_agent().step(comp_history, user_history)

    def update(self, user_history, comp_history) -> None:
        if not user_history or not comp_history: return

        # Get losses
        losses = torch.zeros(self.num_agents, dtype=torch.float32)
        for i, agent in enumerate(self.agents):
            # Use history_step instead of step to avoid the update(); we wouldn't want the agent we just played to update twice.
            agent_arm = agent.step(comp_history[:-1], user_history[:-1]) # Forward pass on the history, excluding the last move.
            losses[i] = bowling_loss_fn(user_history[-1], agent_arm)                 # Test on last move
            if self.mode == UserIs.BATTING: losses[i] = -losses[i]

            agent.update(comp_history, user_history) # Update the agent with the full history

        
        self.weights -= self.lr * losses

        logger.info(f"{user_history=}")
        logger.info(f"{comp_history=}")
        logger.info({str(agent) : loss.item() for agent, loss in zip(self.agents, losses)})
        logger.info({str(agent) : round(weight.item()*100, 2) for agent, weight in zip(self.agents, torch.softmax(self.weights, dim=0))}) # Updated weights