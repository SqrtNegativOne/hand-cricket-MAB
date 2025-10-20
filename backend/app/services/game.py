from app.services.bandit import MultiArmedBandit as Bandit
from app.schemas import UserIs, BatterState


class Game:
    def __init__(self, mode: UserIs, target: int = -1):
        self.user_mode = mode
        self.bandit = Bandit(mode=mode)
        self.runs = 0
        self.wickets_left = 5
        self._bat_history = []
        self._bowl_history = []
        self.target = target
    
    @staticmethod
    def return_score(user_move: int) -> BatterState:
        match user_move:
            case 1: return BatterState.Scored1
            case 2: return BatterState.Scored2
            case 3: return BatterState.Scored3
            case 4: return BatterState.Scored4
            case 5: return BatterState.Scored5
            case 6: return BatterState.Scored6
        raise ValueError("user_move must be between 1 and 6.")
    
    def step(self, user_move: int) -> BatterState:
        if user_move < 1 or user_move > 6:
            raise ValueError("user_move must be between 1 and 6.")
        
        if self.bandit is None:
            raise ValueError("Game not started. Call start_batting or start_bowling first.")

        if self.user_mode == UserIs.BATTING:
            comp_move = self.bandit.select_arm(
                comp_history=self._bowl_history,
                user_history=self._bat_history
            )
            self._bat_history.append(user_move)
            self._bowl_history.append(comp_move)
            self.bandit.update(
                user_history=self._bat_history,
                comp_history=self._bowl_history
            )
        else: # Bowling mode
            comp_move = self.bandit.select_arm(
                comp_history=self._bat_history,
                user_history=self._bowl_history
            )
            self._bowl_history.append(user_move)
            self._bat_history.append(comp_move)
            self.bandit.update(
                user_history=self._bowl_history,
                comp_history=self._bat_history
            )

        # Calculate game state.
        if comp_move != user_move: # Not Out
            self.runs += user_move if self.user_mode == UserIs.BATTING else comp_move
            if self.target != -1:
                if self.runs >= self.target:
                    return BatterState.Won
            return self.return_score(user_move)
        self.wickets_left -= 1
        if not self.wickets_left:
            return BatterState.Lost
        return BatterState.Out