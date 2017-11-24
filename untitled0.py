#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Jan  7 10:14:27 2017

@author: marek5050
"""

from nba_py import player as players
from nba_py.player import get_player

name = "Tim Frazier".split(" ")
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

            

p = seasonStats.filter(items=['MATCHUP',"GAME_DATE",'PTS', 'BLK', 'STL', 'AST', 'REB', 'FG3M', 'TOV'])
p["Bonus"] = p[p >= 10].count(axis=1,numeric_only=True)            
p.Bonus[p.Bonus <2] = 0.0
p.Bonus[p.Bonus==2] = 1.5
p.Bonus[p.Bonus>=3] = 4.5
p["DKFPS"] = 1*(p.PTS) + 0.5*(p.FG3M) + 1.25*(p.REB) + 1.5*(p.AST) + 2*(p.STL) + 2*(p.BLK) - 0.5*(p.TOV)+ p.Bonus

seasonStatsWithDKFPS = p
lowerBound = seasonStatsWithDKFPS[(p.DKFPS < p.DKFPS.mean())]
lowerMean = lowerBound.DKFPS.mean()                   