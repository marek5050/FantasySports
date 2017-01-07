import json
import pandas as pd
import numpy as np
from datetime import date

from nba_py import player as players
from nba_py.player import get_player

name = "Stephen Curry".split(" ")
try:
    pid = get_player(name[0], name[1])
except:
    print("Problem with player")
    print(name)

c = players.PlayerGameLogs(pid)
k = c.info()

k.PTS = k.PTS.astype(float)
k.BLK = k.BLK.astype(float)
k.STL = k.STL.astype(float)
k.AST = k.AST.astype(float)
k.REB = k.REB.astype(float)
k.FG3M = k.FG3M.astype(float)
k.TOV = k.TOV.astype(float)
seasonStats = k