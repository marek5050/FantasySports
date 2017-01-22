import json
import pandas as pd
import numpy as np

from datetime import date
import glob

#today = str(date.yesterday())
today = "2017-01-21"

rosterscsv = 'data/generatedRosters/'+today+'.csv'

from nba_py import player as players
from nba_py.player import get_player


def getName(_name):
    name = _name.replace("J.J. Redick", "JJ Redick") \
        .replace("T.J. Warren", "TJ Warren") \
        .replace("P.J. Warren", "PJ Warren") \
        .replace("P.J. Tucker", "PJ Tucker") \
        .replace("J.R. Smith", "JR Smith") \
        .replace("C.J. McCollum", "CJ McCollum") \
        .replace("C.J. Miles", "CJ Miles") \
        .replace("C.J. Watson", "CJ Watson") \
        .replace("C.J. Wilcox", "CJ Wilcox") \
        .replace("K.J. McDaniels", "KJ McDaniels") \
        .split(" ", maxsplit=1)
    return name

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
        first,last = getName(name)
        try:
            pid =  get_player(first,last)
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
    print(grouped)
    return

pLogs = {}

def calculateDKFPSforOutputFile(_date,_file):
    df = pd.read_csv(_file, index_col=None, header=1)
    df["Final"] = 0
    for idx,row in df.iterrows():
        first, last = getName(row["Name"])
        pId = players.get_player(first, last)
        if pId not in pLogs:
            pLogs[pId] = players.PlayerGameLogs(pId).info()

        logs = pLogs[pId]
        logs["GAME_DATE"] = pd.to_datetime(logs["GAME_DATE"],utc=True)
        _r = logs[logs["GAME_DATE"] == _date]
        _rReturn = getDKFPS(_r)
        row["Final"]=_rReturn["DKFPS"]

    df.to_csv(_file)
    return

def calculateDKFPSforOutput():
    #all = glob.iglob('data/generatedRosters/' + today + '.csv')
    #results = pd.DataFrame.from_csv(all)

    path = r'data/output/'  # use your path
    allFiles = glob.glob(path + "/*.csv")
    for _file in allFiles:
        try:
            _date = _file.split("/")[2].split(".csv")[0]
            if "_" in _date:
                _date = _date.split("_")[0]
            calculateDKFPSforOutputFile(_date,_file)
        except:
            pass
    return

displayResults()