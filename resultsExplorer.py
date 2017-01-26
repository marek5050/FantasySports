import json
import pandas as pd
import numpy as np

from datetime import date
import glob

#today = str(date.yesterday())
today = "2017-01-25"

rosterscsv = 'data/generatedRosters/'+today+'.csv'

from nba_py import player as players
from nba_py.player import get_player



#import requests
#import requests_cache

#requests_cache.install_cache('demo_cache')



def getName(_name):
    name = _name\
        .replace("J.J. Redick", "JJ Redick") \
        .replace("T.J. Warren", "TJ Warren") \
        .replace("P.J. Warren", "PJ Warren") \
        .replace("P.J. Tucker", "PJ Tucker") \
        .replace("J.R. Smith", "JR Smith") \
        .replace("C.J. McCollum", "CJ McCollum") \
        .replace("C.J. Miles", "CJ Miles") \
        .replace("C.J. Watson", "CJ Watson") \
        .replace("C.J. Wilcox", "CJ Wilcox") \
        .replace("K.J. McDaniels", "KJ McDaniels") \
        .replace("T.J. McConnell","TJ McConnell") \
        .replace("A.J. Hammons","AJ Hammons") \
        .split(" ", maxsplit=1)
    if "McAdoo" in name[1]:
        name[0] = "James Michael"
        name[1] = "McAdoo"

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
                p.loc[p["Bonus"] < 2,"Bonus"] = 0.0
                p.loc[p["Bonus"] == 2,"Bonus"] = 1.5
                p.loc[p["Bonus"] > 2,"Bonus"] = 4.5
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
    if "DKFPS" not in rrosters:
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
from calculate import Player

def calculateDKFPSforOutputFile(_date,_file):
    df = pd.read_csv(_file, index_col=None, header=0)
    if "Final" in df:
        return
    for idx,row in df.iterrows():
        try:
            p = Player(row)
            p.setEndDate(today)
            p.getSeasonAverage()
            p.getDKFPS()
            logs = p.seasonStatsWithDKFPS
            #logs["GAME_DATE"] = pd.to_datetime(logs["GAME_DATE"],utc=True)
            _r = logs[_date]["DKFPS"]
            val = 0

            if len(_r) > 0:
                val = _r[0]

            df.loc[idx, ("Final")]= val
        except Exception as e:
            print("Failed to process " + row["Name"])
            print(e)
            raise

    df.to_csv(_file, sep=',', encoding='utf-8', index=False, float_format='%.3f')
    return

def calculateDKFPSforOutput():
    # all = glob.iglob('data/generatedRosters/' + today + '.csv')
    # results = pd.DataFrame.from_csv(all)

    path = r'data/final/'  # use your path
    allFiles = glob.glob(path + "/2*.csv")
    for _file in allFiles:
        print("Starting to calculate finals for " + _file)
        try:
            _date = _file.split("/")[2].split(".csv")[0]
            if "_" in _date:
                _date = _date.split("_")[0]
            calculateDKFPSforOutputFile(_date,_file)
            print("Finished calculating finals for " + _file)
        except Exception as e:
            print("failed something ")
            print(e)
            pass
    return


def addVegasForOutput():
    # all = glob.iglob('data/generatedRosters/' + today + '.csv')
    # results = pd.DataFrame.from_csv(all)

    path = r'data/output/'  # use your path
    allFiles = glob.glob(path + "/*.csv")
    for _file in allFiles:
        try:
            _date = _file.split("/")[2].split(".csv")[0]
            if "_" in _date:
                _date = _date.split("_")[0]
            df = pd.read_csv("data/output/"+_date+".csv",header=0, index_col=None)
            vegas = pd.read_csv("data/vegas/"+_date+".csv")
            vegas = vegas.set_index("team")
            for idx, row in df.iterrows():
                df.loc[idx, "O/U"] = vegas.loc[row["teamAbbrev"].upper()]["overUnder"]
                df.loc[idx, "odds"] = vegas.loc[row["teamAbbrev"].upper()]["odds"]

            df.to_csv("data/output/"+_date+".csv", sep=',', encoding='utf-8', index=False, float_format='%.3f')

        except Exception as e:
            print("Error with date: " + _date)
            print(e)
            pass

    return

'''
results = []
try:
    results = pd.DataFrame.from_csv(rosterscsv)
    if "DKFPS" not in results:
        updateResults()
        results = pd.DataFrame.from_csv(rosterscsv)
except:
        pass
'''

#updateResults()
#displayResults()
calculateDKFPSforOutput()
#addVegasForOutput()