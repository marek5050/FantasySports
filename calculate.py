# -*- coding: utf-8 -*-

import json
import pandas as pd
import numpy as np

from datetime import date

today = str(date.today())
end_date = today

#today = "2017-01-20"
#end_date = "2017-01-19"
newest = 'data/teams/'+today+'.json'
injuries_file = 'data/injuries/'+today+'.json'
community_file = 'data/targets/'+today+'.json'
newestSalaries = 'data/salaries/'+today+'.csv'

try:
    blacklisted = pd.read_csv('data/blacklisted/list.csv')
    dvp = pd.read_csv('data/Defense/'+today+'.csv')
    dvp = dvp.set_index("team")
    dvp.sort_values(by="all",inplace=True)

    vegas = pd.read_csv('data/vegas/' + today + '.csv')
    vegas = vegas.set_index("team")


except Exception as e:
        print("Failed to load community file.")
        dvp = []
        blacklisted = []
        vegas = []

# dvp.loc["BKN", :].values

#with open(newest) as json_data:
#    d = json.load(json_data)
try:
    with open(injuries_file) as json_data:
        injuries = json.load(json_data)
except Exception as e:
        print("Failed to load community file.")
        injuries = []

try:
    with open(community_file) as json_data:
        community = json.load(json_data)
except Exception as e:
        print("Failed to load community file.")
        community = []

try:
    with open("data/calendar/full_schedule.json") as json_data:
        calendar = json.load(json_data)
except Exception as e:
        print("Failed to load community file.")
        calendar = []


def fixTeam(abbr):
    if(abbr == "CHO"):
             return "CHA"
    if(abbr == "SA"):
                return "SAS"
    if (abbr == "GS"):
                return "GSW"
    if (abbr == "BKN"):
                return "BRK"
    if(abbr == "NO"):
                return "NOP"
    if(abbr == "NY"):
                return "NYK"
    if(abbr == "LAK"):
        return "LAL"
    if(abbr == "MLW"):
        return "MIL"
    if(abbr == "CHA"):
                return "CHO"
    if(abbr == "SA"):
                return "SAS"
    if (abbr== "GS"):
                return"GSW"

    if(abbr == "NO"):
               return "NOP"
    if(abbr == "NY"):
                return"NYK"
    return abbr

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
        self.team = team.upper()
        return

    def setOpponent(self, opp):
        self.opponent = opp
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


    def getSeasonStats(self):
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
        name = self.name.replace("Jr.","")      \
            .replace("J.J. Redick","JJ Redick") \
            .replace("T.J. Warren","TJ Warren") \
            .replace("P.J. Warren","PJ Warren") \
            .replace("P.J. Tucker","PJ Tucker") \
            .replace("J.R. Smith" ,"JR Smith")  \
            .replace("C.J. McCollum","CJ McCollum") \
            .replace("C.J. Miles", "CJ Miles") \
            .replace("C.J. Watson", "CJ Watson") \
            .replace("C.J. Wilcox", "CJ Wilcox") \
            .replace("K.J. McDaniels", "KJ McDaniels") \
            .split(" ",maxsplit=1)
        try:
            pid =  get_player(name[0],name[1])
        except Exception as e:
            print("Problem with player " + player.name)
            self.error = 1
            return None

        c =  players.PlayerGameLogs(pid)
        k = c.info()
        k["GAME_DATE"] = pd.to_datetime(k["GAME_DATE"])
        k.set_index("GAME_DATE",inplace=True)
        k = k[end_date:'2016-01-01']
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
            if self.seasonStats is None and player.error == 0:
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
            if self.seasonStats is None and player.error == 0:
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
            if self.seasonStats is None and player.error == 0:
                self.getSeasonStats()
                self.getDKFPS()
            try:
                p = self.seasonStatsWithDKFPS
                avg =  p.iloc[:4]["DKFPS"].mean()
            except:
                avg = 0.0

            return avg

    def getFloorAverage(self):
            if self.seasonStats is None and player.error == 0:
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
            if self.seasonStats is None and player.error == 0:
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


    '''
            self.name = data["team"]

            for tables in data["data"]:
                for tableName, table in tables.items():
                    tableName = tableName.replace("-","_")
    #                setattr(self, tableName, table)
                    self.data[tableName] = table
                    if(tableName == "all_roster"):
                        for item in table:
                            self.roster.append(Player(item[1]))
    '''
    def load(self,data):
        print("loading")

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
        for idx, team in data.iterrows():
            abbr = team["teamAbbrev"].upper()
            if abbr not in self.teams:
                self.teams[abbr] = Team(abbr)
            self.teams[abbr].addPlayer(Player(team))
        return

    def setInjuries(self, injuries):
        for injury in injuries:
            if injury["team"] in self.teams:
                self.teams[injury['team']].setInjury(injury['player'])
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

if __name__ == "__main__":

    cal = Calendar()
    cal.load(calendar)
    t = pd.read_csv(newestSalaries)
    teams = Teams()
    teams.load(t)
    teams.setInjuries(injuries)
    #a = teams.getPerGameData()
    cleanedData = []
    header = None
    '''
    for item in a:
        if header == None:
            header = item[0]
        del item[0]
        cleanedData += item

    df = pd.DataFrame(cleanedData)
    '''
    '''
    idx = header.index('eFG%')

    efgs = df.iloc[:,[header.index('Player')]]

    #efgs = pd.DataFrame(cleanedData)
    #efgs = efgs.sort_values([header.index('eFG%'),header.index('PTS')],ascending=False)
    #efgs[5] = efgs[5].apply(pd.to_numeric)
    #efgs[15] = efgs[15].apply(pd.to_numeric)
    #efgs[27] = efgs[27].apply(pd.to_numeric)
    '''
    '''
    matchups = Matchups()
    matchups.load(teams, cal.findByDate(today))
    '''
    # l = Lineup()
    # l.load(matchups, ["John Wall","Zach LaVine","Otto Porter","Thaddeus Young","Steven Adams","Kyle Korver","Gorgui Dieng","Nikola Jokic"])
    # print(l.playerTeam)

    dataset = pd.read_csv(newestSalaries)
#    dataset["matchup"] = 0.0
#    dataset["GameInfo"].str.replace("","")
#    dataset[(dataset["Position"].isin(['PG']) & dataset["teamAbbrev"].isin(["Cha"]))]["matchup"]=dvp.loc["CHA","pg"]



    for index,row in dataset.iterrows():
        p = teams.findPlayer(row["Name"])
        if p != None:
            p.setOpponent(row["GameInfo"].split(" ")[0].replace("@","").lower().replace(row["teamAbbrev"].lower(),"").upper())
            p.setDvP(dvp)
            p.setHome()
        else:
            print("Could not find  "+row["Name"])

    for updates in community:
        for target in updates["targets"]:
                player = teams.findPlayer(target['name'])
                if player != None and player.fantasyPointAverage > 0:
                    player.addBonus(target["value"])

    #teamStats = teams.teamAndOppStats()
    '''
    for matchup in matchups.games:
        v = matchup[0] # Visiting team
        h = matchup[1] # Home team
        homeStats = teamStats[h]
        visitorStats = teamStats[v]

        hTeamG = float(homeStats[0][23])
        hTeamOG = float(homeStats[1][23])
        vTeamG = float(visitorStats[0][23])
        vTeamOG = float(visitorStats[1][23])
        score = (hTeamG + hTeamOG + vTeamG + vTeamOG)/4
        teams.teams[h].setExpectedScore(score)
        teams.teams[h].setOpponent(v)
        teams.teams[h].setHome(1)
        teams.teams[v].setExpectedScore(score)
        teams.teams[v].setOpponent(h)
    '''
    efgs = dataset
    efgs["atHome"]  = 0
    efgs["injured"] = 0
    efgs["7GameAvg"] = 0.0
    efgs["FloorAvg"] = 0.0
    efgs["4GameAvg"] = 0.0
    efgs["communityBonus"] = 0.0
    efgs["penalty"] = 0.0
    efgs["dvp"] = 0.0
    efgs["value"] = 0.0

    for index,row in efgs.iterrows():
        player = teams.findPlayer(row[1])
        if player != None and player.team != '':
                efgs.loc[index,("injured")] = 1 if (player.injury) else 0
                SvnGameAvg = player.get7GameAvg()
                efgs.loc[index,("atHome")]= player.home
                efgs.loc[index, "teamAbbrev"] = player.team
                efgs.loc[index,("7GameAvg")] = (SvnGameAvg["home"] if (player.home) else SvnGameAvg["away"]) or 0.00
                efgs.loc[index,("FloorAvg")] = player.getFloorAverage() or 0.00
                efgs.loc[index,("4GameAvg")] = player.get4GameAvg() or 0.0

                bonus = 0.0
                if player.bonus > 0 and player.bonus <= 5:
                    bonus = 0.10
                elif player.bonus > 5:
                    bonus = 0.25

                efgs.loc[index,("communityBonus")] = bonus * player.fantasyPointAverage
                efgs.loc[index,("dvp")] = player.dvp or 0.00
                efgs.loc[index,('value')] = player.salary*0.001*6
                efgs.loc[index,("O/U")] = vegas.loc[player.team]["overUnder"]
                efgs.loc[index,("±")] = vegas.loc[player.team]["odds"]
                positions = player.position.lower().split("/")
                #efgs.loc[index,("penalty")] =
                penalty = 0
                if player.injury:
                     penalty = 9999.0
                elif player.salary < 4500 and player.dvp <= 13:
                    penalty = 9000.0
                elif player.salary < 6500 and player.dvp <= 7:
                    penalty = (10 + 10 / player.dvp)
                elif player.salary > 4500 and player.dvp <= 7:
                    penalty = (10 + 10 / player.dvp)

                overUnder = vegas.loc[player.team]["overUnder"]
                odds = abs(vegas.loc[player.team]["odds"])
                s = ""
                overUnderMean = vegas["overUnder"].mean()
                oddsMean = vegas[(vegas["odds"] >= 0)]["odds"].mean()
                '''
                    Bonus to ppl in high scoring games (215)    (220)/(220+205(mean)) (230-215)/(237-215)...
                    Blowout definition : 4% = odds/overUnder ratio
                    Penalize losing team in blowouts especially bench ...
                    Penalize bench in tight games....
                '''
                penalty += 200 * (overUnderMean-overUnder)/overUnderMean
                s+= " o/u: "+ str((200 * (overUnderMean - overUnder)/overUnderMean))

                #blowout
                if odds / overUnder > 0.3 or odds > oddsMean:
                    penalty += 10 #(odds-oddsMean)/oddsMean
                #cheap players on losing team penalty
                # if + and < 4500 -10%
                if player.salary < 4500 and odds > oddsMean:
                    penalty += 10
                    s += " low player: " + str(10)


                lastGame = player.getLastGame()
                try:
                    std = player.seasonStatsWithDKFPS.loc[:,"DKFPS"].std()
                    #if last game sucked
                    if len(lastGame["DKFPS"]) > 0 and (lastGame["DKFPS"][0] < (player.fantasyPointAverage-std)):
                       penalty += std*10
                       s+= " bad last game: " + str((std*10))
                except:
                    pass

                penalty = -1 * player.fantasyPointAverage * (penalty/100)

                efgs.loc[index, "penalty"] = penalty


    #notInjured[(efgs["4GameAvg"] < efgs["7GameAvg"]) & (efgs["4GameAvg"] < efgs["AvgPtsPerGame"])]
    #notInjured = efgs[)]
    notInjured = efgs[(efgs["Salary"] != 0) & (efgs["7GameAvg"]>0) & (efgs["FloorAvg"]>0)]
    # Blacklisted players
    #df[~df['stn'].isin(remove_list)]
    notInjured = notInjured[~notInjured["Name"].isin(blacklisted["name"])]

    #notInjured.rename(columns={1: 'Name'}, inplace=True)
    #efgs = efgs.filter(items=['one', 'three'])
    notInjured.to_csv("data/output/"+str(date.today())+'.csv', sep=',', encoding='utf-8', index=False, float_format='%.3f')

    #efgs = efgs.loc[(efgs[5]>=efgs[5].mean()) &  (efgs[15]>=efgs[15].mean()) & (efgs[27]>=efgs[27].mean()) & (efgs["Salary"] > 0)]

    #efgs["KeyStat"] = 0
    #ESmean = efgs["expectedScore"].mean()
    #for index,row in efgs.iterrows():
    #    efgs["KeyStat"][index] = (row["Salary"]/(row[5]*row[15]*row["AvgPointsPerGame"]))

    #stats = pd.DataFrame.from_dict(team.data["all_team_and_opponent"][1:])
    #del stats[0]
    #stats = stats.set_value(0,0,"header")
    #stats = stats.set_index(stats.columns[0])
    #stats.columns = stats[0:1].values[0]
    #stats = stats[1:]