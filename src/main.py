import torch
import pprint

import bowlers
import batters


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
        return self.agents[torch.multinomial(probs, num_samples=1).item()]

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

    def player_bats(self):
        print("\n== You are batting! ==\n")
        bandit = MultiArmedBandit(mode="bowling", lr=0.1)
        self.player_score = 0
        player_history = []
        computer_history = []

        while True:

            # Computer move
            comp_move = bandit.select_arm(self_history=computer_history, adversary_history=player_history)
            
            # Player move
            try:
                player_move = int(input("Enter your run (1-6): "))
                if player_move < 1 or player_move > 6:
                    print("Invalid input. Choose between 1 and 6.")
                    continue
            except ValueError:
                print("Invalid input. Enter a number.")
                continue
            
            print(f"AI bowls: {comp_move}")

            # Only after both moves are made, do we append them to the histories
            player_history.append(player_move)
            computer_history.append(comp_move)

            if player_move == comp_move:
                print("=> You are OUT! <=\n")
                break
            else:
                self.player_score += player_move
                print(f"=> Your runs: {self.player_score}\n")

            
            bandit.update(player_history, computer_history)

    def computer_bats(self):
        print("\n== AI is batting! ==\n")
        bandit = MultiArmedBandit(mode="batting", lr=0.1)
        self.computer_score = 0
        player_history = []
        computer_history = []

        while True:

            # Computer move
            comp_move = bandit.select_arm(computer_history, player_history)
            
            # Player move
            try:
                player_move = int(input("Enter your bowl (1-6): "))
                if player_move < 1 or player_move > 6:
                    print("Invalid input. Choose between 1 and 6.")
                    continue
            except ValueError:
                print("Invalid input. Enter a number.")
                continue
            
            print(f"AI bats: {comp_move}")

            # Only after both moves are made, do we append them to the histories
            player_history.append(player_move)
            computer_history.append(comp_move)

            if player_move == comp_move:
                print("=> AI is OUT! <=\n")
                break
            else:
                self.computer_score += comp_move
                if self.computer_score > self.player_score: break
                print(f"=> AI's runs: {self.computer_score}")
                print(f"=> To chase: {self.player_score - self.computer_score}\n")

            bandit.update(player_history, computer_history)

    def play(self):
        print("\nWelcome to Hand Cricket!")
        print("Rules: Choose a number between 1 and 6.\nIf both choose the same, the batsman is OUT.")

        self.player_bats()
        print(f"\nYour final score: {self.player_score}")
        self.computer_bats()

        print(f"\nYour final score: {self.player_score}")
        print(f"Computer's final score: {self.computer_score}\n")
        if self.player_score > self.computer_score:
            print(f"Homo Sapien wins by {self.player_score - self.computer_score} runs!")
        elif self.player_score < self.computer_score:
            print(f"AI wins by {self.computer_score - self.player_score} runs!")
        else:
            print("It's a TIE!")


if __name__ == "__main__":
    game = HandCricketGame()
    game.play()