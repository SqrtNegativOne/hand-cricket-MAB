from abc import ABC, abstractmethod
import random
import torch
import torch.nn as nn
import inspect


class Agent(ABC):
    def initial_step(self) -> int:
        return random.randint(1, 6)

    @abstractmethod
    def history_step(self, self_history, adversary_history) -> int:
        pass
    
    def step(self, self_history, adversary_history) -> int:

        self.update(self_history, adversary_history)

        if not adversary_history:
            return self.initial_step()
        else:
            return self.history_step(self_history, adversary_history)
    
    def update(self, self_history, adversary_history) -> None:
        pass

    def __repr__(self) -> str:
        # Use the class name and the parameters of the constructor
        params = inspect.signature(self.__init__).parameters
        param_str = ', '.join(f"{name}={getattr(self, name)}" for name in params if hasattr(self, name))
        return f"{self.__class__.__name__}({param_str})"


class RandomAgent(Agent):
    def history_step(self, self_history, adversary_history):
        return random.randint(1, 6)


class PlayersModeAgent(Agent): # The adversary may have a favourite number
    def __init__(self):
        super().__init__()

        # Use Boyer-Moore algorithm
        self.mode = None # Number from 1 to 6 that the user has played the most
        self.count = 0
    
    def update(self, self_history, adversary_history):
        if not adversary_history: return
        
        if adversary_history[-1] == self.mode:
            self.count += 1
        else:
            if self.count == 0:
                self.mode = adversary_history[-1]
                self.count = 1
            else:
                self.count -= 1

    def history_step(self, self_history, adversary_history):
        if self.mode is None:
            print(f"{self.count=}")
            raise ValueError("Mode has not been set. Call update() with a valid adversary history first.")
        return self.mode


class AntiPlayersModeAgent(Agent): # The adversary may try to play a number that they have not played in the past
    def __init__(self):
        super().__init__()

        self.frequency = torch.zeros(6, dtype=torch.int32) # Frequency of each number from 1 to 6

    def update(self, self_history, adversary_history):
        if not adversary_history: return
        self.frequency[adversary_history[-1] - 1] += 1

    def history_step(self, self_history, adversary_history):
        return torch.argmin(self.frequency).item() + 1 # Add 1 to convert from 0-indexed to 1-indexed


class AntiComputersModeAgent(Agent): # The adversary may try to play a number that the computer has not played in the past
    def __init__(self):
        super().__init__()

        self.frequency = torch.zeros(6, dtype=torch.int32)
    
    def update(self, self_history, adversary_history):
        if not self_history: return
        self.frequency[self_history[-1] - 1] += 1
    
    def history_step(self, self_history, adversary_history):
        return torch.argmin(self.frequency).item() + 1


class FrequencyAgent(Agent): # The adversary may have a couple of favourite numbers
    def __init__(self):
        super().__init__()

        self.frequency = torch.ones(6, dtype=torch.float32) # Using ones for better smoothing. Float because multinomial only supports float tensors.

    def update(self, self_history, adversary_history):
        if not adversary_history: return
        self.frequency[adversary_history[-1] - 1] += 1 # Increment frequency of the last action taken by the adversary

    def history_step(self, self_history, adversary_history):
        return torch.multinomial(self.frequency, num_samples=1).item() + 1 # Sample from the frequency distribution and convert to 1-indexed
    

class nGramAgent(Agent):
    def __init__(self, n=2):
        super().__init__()

        self.n = n
        if n < 1:
            raise ValueError("n must be at least 1")
        
        self.model = torch.ones([6] * n, dtype=torch.float32) # Using ones instead of zeros for better smoothing. Use float because multinomial only supports them.
    
    def update(self, self_history, adversary_history):
        if len(adversary_history) < self.n:
            return

        # Add latest action to the model
        zero_indexed_adversary_history = [action - 1 for action in adversary_history]
        latest_action = zero_indexed_adversary_history[-1]
        self.model[tuple(
            zero_indexed_adversary_history[-self.n + 1:] + [latest_action]
        )] += 1

    def history_step(self, self_history, adversary_history):
        if len(adversary_history) < self.n:
            return random.randint(1, 6)
        
        zero_indexed_adversary_history = [action - 1 for action in adversary_history]
        
        # We can also return argmax(self.model[tuple(history[-self.n + 1:])]) + 1
        return torch.multinomial(
            self.model[tuple(
                zero_indexed_adversary_history[-self.n + 1:]
            )],
            num_samples=1
        ).item() + 1 # Add 1 to convert back to 1-indexed


"""
Discarding this because it just requires too much data.

class MLPModel(nn.Module):
    def __init__(self, context_len, hidden_dims=64):
        super().__init__()

        # self.C = nn.Embedding(6, 2) # 6 possible actions represented by a 2-dimensional vector # nm requires too much data
        self.linear_path = nn.Linear(2 * context_len, 6) # Linear layer to process the concatenated embeddings
        self.hidden_path = nn.Sequential(
            nn.Linear(2 * context_len, hidden_dims),
            nn.ReLU(),
            nn.Linear(hidden_dims, 6)
        )
    
    def forward(self, X):
        cat = self.C(X).view(X.shape[0], -1)
        return self.model(cat)

class MLPAgent(Agent):
    def __init__(self):
        super().__init__()
        self.model = MLPModel()

    def history_step(self, history):
        
        # Convert history to tensor and pass through the model
        input_tensor = torch.tensor(history, dtype=torch.float32).unsqueeze(0)
"""

bowlers = [RandomAgent(), PlayersModeAgent(), AntiPlayersModeAgent(), AntiComputersModeAgent(), FrequencyAgent(), nGramAgent(2), nGramAgent(3), nGramAgent(4)]