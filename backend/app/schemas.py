from enum import Enum

class UserIs(Enum): # No INIT mode!
    BOWLING = "bowling"
    BATTING = "batting"

class BatterState(Enum): # Game states of the batter in both batter and bowling modes.
    Lost = -2
    Out = -1
    Scored1 = 1
    Scored2 = 2
    Scored3 = 3
    Scored4 = 4
    Scored5 = 5
    Scored6 = 6
    Won = 7