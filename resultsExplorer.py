import json
import pandas as pd
import numpy as np

from datetime import date
import glob

#today = str(date.yesterday())
today = "2017-01-17"

rosterscsv = 'data/generatedRosters/'+today+'.csv'

def getSeasonStats(name):
        '''
            Point = +1 PT
            Made 3pt. shot = +0.5 PTs
            Rebound = +1.25 PTs
            Assist = +1.5 PTs
            Steal = +2 PTs
            Block = +2 PTs
            Turnover = -0.5 PTs
            Double-Double = +1.5PTs (MAX 1 PER PLAYER: Points, Rebounds, Assists, Blocks, Steals)
            Triple-Double = +3PTs (MAX 1 PER PLAYER: Points, Rebounds, Assists, Blocks, Steals)
            '''

        from nba_py import player as players
        from nba_py.player import get_player
        name = name.split(" ")
        try:
            pid =  get_player(name[0],name[1])
        except:
            print("Problem with player")
            print(name)
            return None

        c =  players.PlayerGameLogs(pid)
        k = c.info()

        k.PTS = k.PTS.astype(float)
        k.BLK = k.BLK.astype(float)
        k.STL = k.STL.astype(float)
        k.AST = k.AST.astype(float)
        k.REB = k.REB.astype(float)
        k.FG3M = k.FG3M.astype(float)
        k.TOV = k.TOV.astype(float)
        return k


def getDKFPS(seasonStats):
            try:
                p = seasonStats.filter(items=['MATCHUP',"GAME_DATE",'PTS', 'BLK', 'STL', 'AST', 'REB', 'FG3M', 'TOV'])
                p["Bonus"] = p[p >= 10].count(axis=1,numeric_only=True)
                p.Bonus[p.Bonus < 2] = 0.0
                p.Bonus[p.Bonus == 2] = 1.5
                p.Bonus[p.Bonus >= 3] = 4.5
                p["DKFPS"] = 1 * (p.PTS) + 0.5 * (p.FG3M) + 1.25 * (p.REB) + 1.5 * (p.AST) + 2 * (p.STL) + 2 * (p.BLK) - 0.5 * (p.TOV) + p.Bonus
            except:
                pass
            return p

def updateResults():
    history = 'data/HistoryWithResults/recent.csv'

    try:
        rrosters = pd.DataFrame.from_csv(rosterscsv)
        history = pd.DataFrame.from_csv(history)
    except:
        print("Failed to open file. ")

    rrosters["DKFPS"] = 0.0
    for index,row in rrosters.iterrows():
        s = 0
        for player in row[0:8]:
                stats = getSeasonStats(player)
                if stats is not None:
                    pts = getDKFPS(stats)
                    s += pts.loc[0,"DKFPS"]
        rrosters.loc[index, "DKFPS"] = s

    rrosters["Result"] = "None"
    for index,row in rrosters.iterrows():
        r = history[(history["Points"] == row["DKFPS"]) & (history["Contest_Date_EST"] == "2017-01-08 20:00:00")][:1]
        if r is not None and len(r) > 0:
            rrosters.loc[index,"Result"] = "Win" if r.loc["NBA","Place"] <= r.loc["NBA","Places_Paid"] else "Loss"

    rrosters.to_csv(rosterscsv)

results = []
try:
    results = pd.DataFrame.from_csv(rosterscsv)
    if "DKFPS" not in results:
        updateResults()
        results = pd.DataFrame.from_csv(rosterscsv)
except:
    pass


def displayResults():
    #all = glob.iglob('data/generatedRosters/' + today + '.csv')
    #results = pd.DataFrame.from_csv(all)

    path = r'data/generatedRosters/'  # use your path
    allFiles = glob.glob(path + "/*.csv")
    list_ = []
    for file_ in allFiles:
        try:
            df = pd.read_csv(file_, index_col=None, header=0)
            _date = file_.split("/")[2].split(".csv")[0]
            if "_" in _date:
                _date = _date.split("_")[0]
            df["date"] = _date
            list_.append(df)
        except:
            pass
    frame = pd.concat(list_)
    loss = frame[(frame.Result == "Loss")].groupby(["Strategy"])["Result"].count()
    win = frame[(frame.Result == "Win")].groupby(["Strategy"])["Result"].count()
    grouped = frame.groupby(["Strategy"]).mean()
    grouped["ratio"] = win / (loss+win)
    return

displayResults()