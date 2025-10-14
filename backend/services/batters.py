from abc import ABC, abstractmethod
import random
import torch
import torch.nn as nn

import services.bowlers as bowlers


class MiddleFrequencyAgent(bowlers.Agent): # Avoid Bowler's favourite and least favourite numbers
    def __init__(self):
        super().__init__()

        self.counts = torch.zeros(6, dtype=torch.int32)  # Counts for each number from 1 to 6
    
    def update(self, self_history, adversary_history):
        self.counts[adversary_history[-1] - 1] += 1
    
    def history_step(self, self_history, adversary_history):
        return random.choice(
            [i + 1 for i in range(6) if i != self.counts.argmin() and i != self.counts.argmax()]
        )
    

class CounterAgent(bowlers.Agent):  # Try to play the opposite of what a bowler agent is about to play
    def __init__(self, bowler):
        super().__init__()

        self.bowler = bowler
    
    def update(self, self_history, adversary_history):
        self.bowler.update(self_history, adversary_history)

    def history_step(self, self_history, adversary_history): # Using history_step instead of step because I made that an abstract method in Agent
        if self.bowler.history_step is None:
            raise ValueError("Bowler's history_step method is not defined.")
        if self.bowler.history_step(self_history, adversary_history) is None:
            print(self.bowler)
            raise ValueError("Bowler's history_step method returned None.")
        
        return 7 - self.bowler.history_step(self_history, adversary_history)


counter_batters = [CounterAgent(bowler) for bowler in bowlers.bowlers] # Should automatically include RandomAgent, PlayersModeAgent, AntiPlayersModeAgent, AntiComputersModeAgent
batters = [MiddleFrequencyAgent()] + counter_batters