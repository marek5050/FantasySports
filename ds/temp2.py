import json
import pandas as pd
import numpy as np
from datetime import date

from nba_py import player
from nba_py import team
from nba_py.player import get_player

import requests
import requests_cache

requests_cache.install_cache('demo_cache')

# Preparing for NNs
import pickle
players = {}
teamLogs = {}
df = player.PlayerList().info()
dft = team.TeamList().info()

def downloadTeamData():
    for key,row in dft.iterrows():
        teamLogs[row["TEAM_ID"]]=team.TeamGameLogs(row["TEAM_ID"]).info()
    output = open("data/extras/teams.pickle", 'wb')
    pickle.dump(teamLogs, output)


def loadTeamData():
    input = open("data/extras/teams.pickle", 'rb')
    return pickle.load(input)


def downloadPlayerData():
    for idx, row in df.iterrows():
        id = row["PERSON_ID"]
        players[id] =  player.PlayerGameLogs(id).info()

    for key in players:
        p = players[key].filter(items=['MATCHUP', "GAME_DATE", 'PTS', 'BLK', 'STL', 'AST', 'REB', 'FG3M', 'TOV'])
        p["Bonus"] = p[p >= 10].count(axis=1, numeric_only=True)
        p.loc[p["Bonus"] < 2, "Bonus"] = 0.0
        p.loc[p["Bonus"] == 2, "Bonus"] = 1.5
        p.loc[p["Bonus"] > 2, "Bonus"] = 4.5
        players[key]["DKFPS"] = 1*(p.PTS) + 0.5*(p.FG3M) + 1.25*(p.REB) + 1.5*(p.AST) + 2*(p.STL) + 2*(p.BLK) - 0.5*(p.TOV) +p.Bonus

    output = open("data/extras/players.pickle", 'wb')
    pickle.dump(players,output)


def loadPlayerData():
    input = open("data/extras/players.pickle", 'rb')
    return pickle.load(input)


def loadTeamBaseData():
    input = open("data/extras/teamBases.pickle", 'rb')
    return pickle.load(input)


def downloadTeamBaseData():
    for _team in teamLogs:
        teamLogs[_team]["GAME_DATE"] = pd.to_datetime(teamLogs[_team]["GAME_DATE"],utc=True)

    for _player in players:
        players[_player]["GAME_DATE"]=pd.to_datetime(players[_player]["GAME_DATE"],utc=True)
        players[_player].set_index("GAME_DATE",inplace=True)

    teamBases =  {}
    for tIDX in teamLogs:
        teamBases[tIDX] = pd.DataFrame(teamLogs[tIDX]["GAME_DATE"])
        teamBases[tIDX].set_index("GAME_DATE",inplace=True)
        try:
            playerList = team.TeamCommonRoster(tIDX).roster()["PLAYER_ID"]
            print(str(tIDX) + " " + str(len(playerList)))
            for playerId in playerList:
                teamBases[tIDX] = pd.concat([teamBases[tIDX],players[playerId]["DKFPS"]],axis=1, join='outer')
                teamBases[tIDX] = teamBases[tIDX].rename(columns={"DKFPS":playerId})
        except Exception as e:
            print("Failed at " + str(tIDX))
            print(e)
            pass
    output = open("data/extras/teamBases.pickle", 'wb')
    pickle.dump(teamBases,output)


#downloadTeamData()
#downloadPlayerData()
#downloadTeamBaseData()

players = loadPlayerData()
teamLogs = loadTeamData()
teamBases = loadTeamBaseData()

for _team in list(teamBases.keys()):
    if len(teamBases[_team]) == 0:
        teamBases.pop(_team,None)

for _team in teamBases:
    teamBases[_team].fillna(value=0,inplace=True)

k = teamBases[1610612766]

#mostRecent = {}
testSeason = {}
trainSeason = {}
for _team in teamBases:
#    mostRecent[_team] = teamBases[_team][-1:]  # N
    trainSeason[_team] = teamBases[_team][-40:-1]  # All the way to N-1
    players = list(trainSeason[_team].columns.values)
    names = {x:player.PlayerSummary(x).info()["DISPLAY_FIRST_LAST"][0] for x in players}
    trainSeason[_team] = trainSeason[_team].rename(columns=names)
    trainSeason[_team].T.to_csv("data/extras/train.csv", sep=',', encoding='utf-8', index=True, float_format='%.1f',
                            mode='a', header=False)
for _team in teamBases:
    testSeason[_team] = teamBases[_team][-39:]  # All the way to N-1
    players = list(testSeason[_team].columns.values)
    names = {x:player.PlayerSummary(x).info()["DISPLAY_FIRST_LAST"][0] for x in players}
    testSeason[_team] = testSeason[_team].rename(columns=names)
    testSeason[_team].T.to_csv("data/extras/test.csv", sep=',', encoding='utf-8', index=True, float_format='%.1f',mode='a',header=False)

#    mostRecent[_team].T.to_csv("data/extras/test.csv", sep=',', encoding='utf-8', index=True, float_format='%.1f',mode='a',header=False)
#    restOfSeason[_team].T.to_csv("data/extras/train.csv", sep=',', encoding='utf-8', index=True, float_format='%.1f',mode='a',header=False)

# mostRecentFinal = pd.DataFrame()
# restOfSeasonFinal = pd.DataFrame()
# for _team in teamBases:
#     try:
#         mostRecentFinal = mostRecentFinal.append(mostRecent[_team])
#         restOfSeasonFinal = mostRecentFinal.append(restOfSeason[_team])
#     except Exception as e:
#         print("Failed on "+str(_team))
#         print(e)


# Additional information
from datetime import date

today = str(date.today())
end_date = today
dvp = pd.read_csv('data/Defense/'+today+'.csv')
dvp = dvp.set_index("team")
dvp.sort_values(by="all",inplace=True)
### Needs player position information ...

# O/U
vegas = pd.read_csv('data/vegas/' + today + '.csv')
vegas = vegas.set_index("team")

#GameN DKFPS,Game1, Game2...GameN-1,O/U,Odds,Pace,At home, DvP

try:
    with open("data/calendar/full_schedule.json") as json_data:
        calendar = json.load(json_data)
except Exception as e:
        print("Failed to load community file.")
        calendar = []

# for _team in teamLogs:
#     teamLogs[_team]["abbrev"] = team.TeamSummary(1610612737).info()["TEAM_ABBREVIATION"]

from calculate import Calendar
cal = Calendar()
cal.load(calendar)
list(cal.findByDate("2017-01-20"))
# team_id = TEAMS['ATL']['id']
'''
df = pd.read_csv("data/historicalDFS/2017-01-20.csv")
df.dropna(inplace=True)
df["date"] = pd.to_datetime(df["date"])

player = df[df["name"]=="Kevin Durant"]
end_date = "2016-12-06"
player.set_index("date",inplace=True)
k = player[:end_date]

from calculate import Player
hm = Player({"Position":"PG/SG","Name":"James Harden","Salary":12200,"GameInfo":"GS@Hou 08:00PM ET","AvgPointsPerGame":61.011,"teamAbbrev": "Hou"})
hm.getDKFPS()
hm.get7GameAvg()
averages=[]
results = []
for i in range(1,len(hm.seasonStatsWithDKFPS["DKFPS"])):
     averages.append(hm.seasonStatsWithDKFPS[:i-1].mean())
     results.append(hm.seasonStatsWithDKFPS.iloc[i]["DKFPS"])


print(list(hm.seasonStatsWithDKFPS["DKFPS"]))
'''