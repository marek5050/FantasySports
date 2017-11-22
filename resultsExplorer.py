import json
import pandas as pd
import numpy as np

from datetime import date
import glob

#today = str(date.yesterday())
today = "2017-02-01"


from nba_py import player as players
from nba_py.player import get_player
from calculate import Player

from models.mysql import *

from nba_py import player
from nba_py.player import get_player


from sqlalchemy.sql import select
from nba_py.player import get_player


session = get_session()
_players = session.query(Player)
_players = _players.filter(Player.DISPLAY_FIRST_LAST.in_(["Gordon Hayward","Kemba Walker","Kawhi Leonard","Andre Drummond","Harrison Barnes","Tim Hardaway Jr.","Jabari Parker","Willie Cauley-Stein"]))
_players = _players.all()
logs = player.PlayerGameLogs(_player.PERSON_ID).info()


def updateResults(_date):
    history = 'data/HistoryWithResults/recent.csv'
    rosterscsv = 'data/generatedRosters/' + _date + '.csv'
    try:
        rrosters = pd.DataFrame.from_csv(rosterscsv)
        history = pd.DataFrame.from_csv(history)
    except Exception as e:
        print("Failed to open file. ")
        print(e)

    #if "DKFPS" not in rrosters:
    rrosters["DKFPS"] = 0.0
    for index,row in rrosters.iterrows():
        s = 0
        for name in row[0:8]:
                p = Player(name = name)
                g = p.getGameWithDate(_date)
                if g is not None and "DKFPS" in g:
                    s += g["DKFPS"][0]
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
            p = Player(data = row)
            l = p.getGameWithDate(_date)
            val = 0
            if l is not None:
                    val = l["DKFPS"].mean()
            df.loc[idx, ("Final")]= val
        except Exception as e:
            print("Failed to process " + row["Name"])
            print(e)
            pass

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

#calculateDKFPSforOutputFile("2017-02-01","data/final/2017-02-01.csv")


# path = r'data/generatedRosters/'  # use your path
# allFiles = glob.glob(path + "/*.csv")
# for _file in allFiles:
#    try:
#         _date = _file.split("/")[2].split(".csv")[0]
#         print("Processing salaries for date " + _date )
#         if "_" in _date:
#             _date = _date.split("_")[0]
#         updateResults(_date)
#         print("Finished processing salaries for date " + _date)
#    except Exception as e:
#        print("Error with date: " + _date)
#        print(e)
#        raise

# calculateDKFPSforOutput()
displayResults()
# addVegasForOutput()