# -*- coding: utf-8 -*-

import json
import pandas as pd
import numpy as np
from nba_py import player as players
from nba_py.player import get_player


from datetime import date

def fixTeam(abbr):
    abbr = abbr.upper()
    if(abbr == "CHO"):
                return "CHA"
    if(abbr == "SAS"):
                return "SA"
    if (abbr == "GSW"):
                return "GS"
    if (abbr == "BRK"):
                return "BKN"
    if(abbr == "NOP"):
                return "NO"
    if(abbr == "NOR"):
                return "NO"
    if(abbr == "NYK"):
                return "NY"
    if(abbr == "LAK"):
                return "LAL"
    if(abbr == "MLW"):
                return "MIL"
    if(abbr=="PHX"):
                return "PHO"
    return abbr


#import requests
#import requests_cache

#requests_cache.install_cache('all_test_cache_1')


class Player:

    def __init__(self,data):
        self.name = data["Name"]
        self.salary = data["Salary"]
        self.position = data["Position"]
        self.gameInfo = data["GameInfo"]
        self.team = data["teamAbbrev"].upper()
        self.fantasyPointAverage = data["AvgPointsPerGame"]
        self.injury = None
        self.seasonStats = None
        self.seasonStatsWithDKFPS = None
        self.bonus = 0.0
        self.players = None
        self.pid = None
        self.error = 0
        if "dvp" in data:
            self.dvp = data["dvp"]

    def setEndDate(self, endDate):
        self.endDate = endDate
        return

    def setHome(self):
        where = self.gameInfo.split(" ")[0].upper().split("@")
        self.home = (where[1] == self.team)
        return

    def setName(self,name):
        self.name = name
        return

    def setSalary(self,salary):
        self.salary = salary
        return

    def setInjury(self,injury):
        self.injury = injury
        return

    def setPosition(self,position):
        self.position = position
        return

    def setTeam(self,team):
        self.team = team.upper().replace("NOP","NO")
        return

    def setOpponent(self, opp):
        self.opponent = opp.upper().replace("NOP","NO")
        return

    def setDvP(self,dvp):
        positions = self.position.lower().split("/")

        self.dvp = dvp.loc[:, positions].rank().loc[self.opponent,positions].mean()

        return

    def setFantasyAverage(self,avg):
        self.fantasyPointAverage= avg
        return
    def addBonus (self, val):
        self.bonus += val
        return

    def getLastGame(self):
        if self.seasonStats is None:
            self.getSeasonStats()

        try:
            return self.seasonStatsWithDKFPS[:1]
        except:
            pass

        return


    def getSeasonStats(self,endDate = None):
        if endDate is None :
            endDate = self.endDate

        if self.error == 1:
            return
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
        name = self.name \
                .replace("J.J. Redick", "JJ Redick") \
                .replace("T.J. Warren", "TJ Warren") \
                .replace("P.J. Warren", "PJ Warren") \
                .replace("P.J. Tucker", "PJ Tucker") \
                .replace("J.R. Smith", "JR Smith")   \
                .replace("C.J. McCollum", "CJ McCollum") \
                .replace("C.J. Miles", "CJ Miles")   \
                .replace("C.J. Watson", "CJ Watson") \
                .replace("C.J. Wilcox", "CJ Wilcox") \
                .replace("K.J. McDaniels", "KJ McDaniels") \
                .replace("T.J. McConnell", "TJ McConnell") \
                .replace("A.J. Hammons", "AJ Hammons") \
                .replace("R.J. Hunter", "RJ Hunter")   \
                .replace("Guillermo Hernangomez","Willy Hernangomez") \
                .replace("Juancho","Juan") \
                .replace("Robinson III","Robinson") \
                .replace("Zimmerman Jr.","Zimmerman") \
                .replace("Luc Richard Mbah a Moute","Luc Mbah a Moute") \
                .split(" ", maxsplit=1)
        # Some other names that break everything...
        if "McAdoo" in name[1]:
                name[0] = "James Michael"
                name[1] = "McAdoo"
        if "Derrick" in name[0] and "Jones" in  name[1]:
                name[0] = "Derrick"
                name[1] = "Jones, Jr."

        try:
            if "Nene" in name[0]:
                pid = 2403
            else:
                pid =  get_player(name[0].strip(),name[1].strip())
        except Exception as e:
            print("Problem with player " + self.name)
            print(e)
            self.error = 1
            return None

        c =  players.PlayerGameLogs(pid)
        k = c.info()
        k["GAME_DATE"] = pd.to_datetime(k["GAME_DATE"])
        k.set_index("GAME_DATE",inplace=True)
        k = k[endDate:'2016-01-01']
        k.PTS = k.PTS.astype(float)
        k.BLK = k.BLK.astype(float)
        k.STL = k.STL.astype(float)
        k.AST = k.AST.astype(float)
        k.REB = k.REB.astype(float)
        k.FG3M = k.FG3M.astype(float)
        k.TOV = k.TOV.astype(float)
        self.seasonStats = k
        return

    def getDKFPS(self):
            if self.seasonStats is None and self.error == 0:
                self.getSeasonStats()
            try:
                p = self.seasonStats.filter(items=['MATCHUP',"GAME_DATE",'PTS', 'BLK', 'STL', 'AST', 'REB', 'FG3M', 'TOV'])
                p["Bonus"] = p[p >= 10].count(axis=1,numeric_only=True)
                p.loc[p["Bonus"] < 2,"Bonus"] = 0.0
                p.loc[p["Bonus"] == 2,"Bonus"] = 1.5
                p.loc[p["Bonus"] > 2,"Bonus"] = 4.5
                p["DKFPS"] = 1 * (p.PTS) + 0.5 * (p.FG3M) + 1.25 * (p.REB) + 1.5 * (p.AST) + 2 * (p.STL) + 2 * (p.BLK) - 0.5 * (p.TOV) + p.Bonus
                self.seasonStatsWithDKFPS = p
            except:
                pass
            return


    def get7GameAvg(self):
            if self.seasonStats is None and self.error == 0:
                self.getSeasonStats()
                self.getDKFPS()
            try:
                p = self.seasonStatsWithDKFPS
                home =  p[p["MATCHUP"].str.contains("vs.")]["DKFPS"][:7].mean()
                away =  p[p["MATCHUP"].str.contains("@")]["DKFPS"][:7].mean()
            except:
                home = 0.0
                away = 0.0

            return {"home": home, "away": away}

    def get4GameAvg(self):
            if self.seasonStats is None and self.error == 0:
                self.getSeasonStats()
                self.getDKFPS()
            try:
                p = self.seasonStatsWithDKFPS
                avg =  p.iloc[:4]["DKFPS"].mean()
            except:
                avg = 0.0

            return avg

    def getFloorAverage(self):
            if self.seasonStats is None and self.error == 0:
                self.getSeasonStats()
                self.getDKFPS()
            try:
                p = self.seasonStatsWithDKFPS
                lowerBound = p[(p.DKFPS < p.DKFPS.mean())]
                lowerMean = lowerBound.DKFPS.mean()
            except:
                lowerMean = 0.0

            return lowerMean

    def getSeasonAverage(self):
            if self.seasonStats is None and self.error == 0:
                self.getSeasonStats()
                self.getDKFPS()

            p = self.seasonStatsWithDKFPS
            seasonAverage = p["DKFPS"].mean()
            return seasonAverage


    def __repr__(self):
         return "Player// "+self.name + ("(I)" if (self.injury!=None) else "")

    def __str__(self):
         return "Player// "+self.name + ("(I)" if (self.injury!=None) else "")

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.name == other.name
        return self.name == other

#calendar["lscd"][0]["mscd"]["g"][0]
class Calendar:
    schedule = []

    def __init__(self):
        return

    def findByDate(self,string):
        return (item for item in self.schedule if string == item[0])

    def load(self,data):
        months = data["lscd"]
        for month in months:
            month = month["mscd"]
            self.schedule += [[game["gdte"],game["v"]["ta"],game["h"]["ta"]] for game in month["g"]]
        return

class Team:
    def __init__(self,abbrev = None):
        self.name = ""
        self.abbrev = abbrev
        self.roster = []
        self.expectedScore = 0
        self.opponent = ""
        self.home = 0
        self.injuries = []
        return

    def addPlayer(self, player):
        self.roster.append(player)
        return

    def setInjury(self, injury):
        player = self.findPlayer(injury[0])
        if player != None:
            player.setInjury(injury)
        else:
            print(self.name + " could not find player: " + injury[0])
        return


    def setInjuries(self, injuryList):
        for injury in injuryList:
           player = self.findPlayer(injury[0])
           if player != None:
               player.setInjury(injury)
           else:
               print("Could not find injured player: " + injury[0])

        return

    def setExpectedScore(self,score=0):
        self.expectedScore = score
        return

    def setOpponent(self, opponent = "" ):
        self.opponent = opponent
        return

    def findPlayer(self,player):
        try:
            return self.roster[self.roster.index(player)]
        except ValueError:
            pass
        return None

    def getInjuries(self):
        return self.data["all_injury"]

    def getTeamAndOpponentStats(self):
        return self.data["all_team_and_opponent"]

    def getPerGame(self):
        return [] #self.data["all_per_game"]

    def setEndDate(self, _date):
        for player in self.roster:
            try:
                player.setEndDate(_date)
            except ValueError:
                pass
        return


    def teamAndOppStats(self):
        return [] #(self.name, [self.data["all_team_and_opponent"][2],self.data["all_team_and_opponent"][6]])

   #'all_team_misc', 'all_per_minute', 'all_totals', 'all_salaries', 'all_roster', 'all_per_poss', 'all_shooting', 'all_injury', 'all_team_and_opponent', 'all_draft_rights', 'all_per_game', 'all_advanced'
    def __repr__(self):
          return "Team// "+self.name

    def __str__(self):
         return "member of Team"

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.name == other.name
        return self.name == other

class Teams:
    def __init__(self):
        self.teams = {}
        return

    def load(self,data):
        self.teams = {}
        for idx, playerdata in data.iterrows():
            abbr = playerdata["teamAbbrev"].upper()
            if abbr not in self.teams:
                self.teams[abbr] = Team(abbr)
            self.teams[abbr].addPlayer(Player(playerdata))

        return

    def setInjuries(self, injuries):
        for injury in injuries:
            if injury["team"] in self.teams:
                self.teams[injury['team']].setInjury(injury['player'])
        return

    def setEndDate(self, _date):
        for key in self.teams:
            try:
                a = self.teams[key].setEndDate(_date)
                if a!= None :
                    return a
            except ValueError:
                pass
        return

    def findPlayer(self,player):
        for key in self.teams:
            try:
                a = self.teams[key].findPlayer(player)
                if a!= None :
                    return a
            except ValueError:
                pass
#        print("Teams: Failed to find player: "+ player)
        return None

    def getPerGameData(self):
        data = []
        for key in self.teams:
            data.append(self.teams[key].getPerGame())
        return data

    def teamAndOppStats(self):
        '''data = {}
        for key in self.teams:
            vals = self.teams[key].teamAndOppStats()
            data[vals[0]] = vals[1]
            '''
        return []

class Matchups:

    def __init__(self):
        self.cal = []
        self.games = []
        self.teams = []
        return

    def load(self, teams, cal):
        self.cal = cal
        for game in cal:
           game[1] = game[1].replace("BKN","BRK").replace("PHX","PHO")
           game[2] = game[2].replace("BKN","BRK").replace("PHX","PHO")

           self.games.append([game[1],game[2]])
           self.teams += [teams.teams[game[1]], teams.teams[game[2]]]
        return

    def findTeam(self, team):
        return self.teams[self.teams.index(team)]

class Lineup:
    def __init__(self):
        self.players = []
        self.playerTeam = []
        return

    def load(self, matchups, players):
        self.players+=players
        for player in self.players:
            for team in matchups.teams:
                t = team.findPlayer(player)
                if(t != None):
                    self.playerTeam.append([player,team])
        return

today = str(date.today())
end_date = today

from scipy.stats import zscore
import os.path
import scipy.stats as st

def calculate(_date):

    # today = "2017-01-20"
    # end_date = "2017-01-19"
    # injuries_file = 'data/injuries/' + _date + '.json'
    # community_file = 'data/targets/' + _date + '.json'
    newestSalaries = 'data/salaries/' + _date + '.csv'
    defense_file = 'data/Defense/' + _date + '.csv'
    vegas_file = 'data/vegas/' + _date + '.csv'
    calendar_file = "data/calendar/full_schedule.json"
    output_file = "data/output/"+_date+".csv"

    try:
        blacklisted = pd.read_csv('data/blacklisted/list.csv')
        if os.path.isfile(defense_file):
            dvp = pd.read_csv(defense_file)
        else:
            dvp = pd.read_csv(defense_file.replace(_date,today))
        dvp = dvp.set_index("team")
        dvp.sort_values(by="all", inplace=True)
    except:
        print("Failed to load DVP file.")
        dvp = []

    try:
        vegas = pd.read_csv(vegas_file)
        vegas = vegas.set_index("team")
    except:
        print("Failed to load vegas file.")
    #
    # try:
    #     if os.path.isfile(injuries_file):
    #         with open(injuries_file) as json_data:
    #             injuries = json.load(json_data)
    #     else:
    #         injuries = []
    # except:
    #     print("Failed to load injuries file.")
    #     injuries = []
    #
    # try:
    #     if os.path.isfile(community_file):
    #          with open(community_file) as json_data:
    #                community = json.load(json_data)
    #     else:
    #         community = []
    # except Exception as e:
    #     print("Failed to load community file.")
    #     community = []

    try:
        with open(calendar_file) as json_data:
            calendar = json.load(json_data)
    except:
        print("Failed to load calendar file.")
        calendar = []

    cal = Calendar()
    cal.load(calendar)
    t = pd.read_csv(newestSalaries)
    teams = Teams()
    teams.load(t)
    # teams.setInjuries(injuries)
    teams.setEndDate(_date)

    if os.path.isfile(newestSalaries):
        dataset = pd.read_csv(newestSalaries)
    else:
        Exception("Failed to load salaries")

    for index, row in dataset.iterrows():
        p = teams.findPlayer(row["Name"])
        if p is not None:
            p.setOpponent(
                row["GameInfo"].split(" ")[0].replace("@", "").lower().replace(p.team.lower(), "").upper())
            p.setDvP(dvp)
            p.setHome()
        else:
            print("Could not find  " + row["Name"])

    # for updates in community:
    #     for target in updates["targets"]:
    #         player = teams.findPlayer(target['name'])
    #         if player is not None and player.fantasyPointAverage > 0:
    #             player.addBonus(target["value"])

    efgs = dataset
    efgs["atHome"] = 0
    efgs["injured"] = 0
    efgs["7GameAvg"] = 0.0
    efgs["FloorAvg"] = 0.0
    efgs["4GameAvg"] = 0.0
    # efgs["communityBonus"] = 0.0
    efgs["dvp"] = 0.0
    efgs["value"] = 0.0

    for index, row in efgs.iterrows():
        try:
            player = teams.findPlayer(row[1])
        except:
            print("failed to load player: " + row[1])
            pass

        if player is not None and player.team != '':
            efgs.loc[index, ("injured")] = 1 if (player.injury) else 0
            SvnGameAvg = player.get7GameAvg()
            efgs.loc[index, ("atHome")] = 1 if player.home else 0
            efgs.loc[index, ("7GameAvg")] = (SvnGameAvg["home"] if player.home else SvnGameAvg["away"]) or 0.00
            efgs.loc[index, ("FloorAvg")] = player.getFloorAverage() or 0.00
            efgs.loc[index, ("4GameAvg")] = player.get4GameAvg() or 0.0

            lg = player.getLastGame()
            val = 0.00
            if lg is not None and len(lg) > 0:
                val = lg["DKFPS"][0]
            efgs.loc[index, ("LastGame")] = val
            ### Bonuses need to be moved out... we're just calculating averages....
            # bonus = 0.0
            # if player.bonus > 0 and player.bonus <= 5:
            #     bonus = 0.10
            # elif player.bonus > 5:
            #     bonus = 0.25
            # efgs.loc[index, ("communityBonus")] = bonus * player.fantasyPointAverage
            playerValue = player.salary * 0.001 * 6
            games= list(player.seasonStatsWithDKFPS["DKFPS"].values)
            games.append(playerValue)
            chanceOfHittingValue = st.norm.cdf(zscore(games))[-1:][0]
            efgs.loc[index, ("dvp")] = player.dvp or 0.00
            efgs.loc[index, ('value')] = playerValue
            # CDF gives us the probability of it being < than X ...so 1- gives us more than
            efgs.loc[index, ("fvalue")] = 1.0 - chanceOfHittingValue
            efgs.loc[index, ("O/U")] = vegas.loc[player.team]["overUnder"]
            efgs.loc[index, ("odds")] = vegas.loc[player.team]["odds"]

    ### Something went wrong with these people
    notInjured = efgs[(efgs["Salary"] != 0) & (efgs["7GameAvg"] > 0) & (efgs["FloorAvg"] > 0)]
    # We'll filter out players somewhere else in the pipeline
    #    notInjured = notInjured[~notInjured["Name"].isin(blacklisted["name"])]
    notInjured.to_csv(output_file, sep=',', encoding='utf-8', index=False, float_format='%.3f')

import glob
if __name__ == "__main__":
    calculate(today)

    # path = r'data/salaries/'  # use your path
    # allFiles = glob.glob(path + "/*.csv")
    # for _file in allFiles:
    #    try:
    #         _date = _file.split("/")[2].split(".csv")[0]
    #         print("Processing salaries for date " + _date )
    #         if "_" in _date:
    #             _date = _date.split("_")[0]
    #         calculate(_date)
    #         print("Finished processing salaries for date " + _date)
    #    except Exception as e:
    #        print("Error with date: " + _date)
    #        print(e)
    #        raise
