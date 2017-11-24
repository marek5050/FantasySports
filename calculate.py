# -*- coding: utf-8 -*-

import datetime
import json
import os.path

import pandas as pd
import scipy.stats as st
from nba_py.player import get_player
from scipy.stats import zscore
from sqlalchemy.sql import select

import mysql as sql

session = sql.get_session()

from datetime import date


# if item["team"] == "SA":
#     item["team"] = "SAS"
# if item["team"] == "NO":
#     item["team"] = "NOP"
#
# if item["team"] == "NY":
#     item["team"] = "NYK"
# if item["team"] == "GS":
#     item["team"] = "GSW"
#
# if item["team"] == "PHO":
#     item["team"] = "PHX"
def fixTeam(abbr):
    abbr = abbr.upper()
    if "UTH" in abbr:
                return "UTA"
    if abbr == "CHO":
                return "CHA"
    if abbr == "SA":
        return "SAS"
    if abbr == "GS":
        return "GSW"
    if abbr == "BRK":
                return "BKN"
    if abbr == "NO":
        return "NOP"
    if abbr == "NOR":
        return "NOP"
    if abbr == "NY":
        return "NYK"
    if abbr == "LAK":
                return "LAL"
    if abbr == "MLW":
                return "MIL"
    if abbr == "PHX":
                return "PHO"
    return abbr


class Player:
    pid = None
    name = None
    salary = None
    position = None
    gameInfo = None
    team = None
    fantasyPointAverage = 0
    injury = None
    seasonStats = None
    bonus = 0.0
    players = None
    pid = None
    error = 0
    dvp = 0
    endDate = None
    logs = None
    info = None
    db = 0

    @staticmethod
    def fixName(name):
        _name = name \
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
            .replace("T.J. McConnell", "TJ McConnell") \
            .replace("A.J. Hammons", "AJ Hammons") \
            .replace("R.J. Hunter", "RJ Hunter") \
            .replace("Guillermo Hernangomez", "Willy Hernangomez") \
            .replace("Juancho", "Juan") \
            .replace("Robinson III", "Robinson") \
            .replace("Zimmerman Jr.", "Zimmerman") \
            .replace("Luc Richard Mbah a Moute", "Luc Mbah a Moute") \
            .replace("Moe Harkless", "Maurice Harkless") \
            .replace("Wes Johnson", "Wesley Johnson") \
            .replace("DeAndre Bembry", "DeAndre\' Bembry") \
            .split(" ", maxsplit=1)

        # Some other names that break everything...
        if "McAdoo" in _name[1]:
            _name[0] = "James Michael"
            _name[1] = "McAdoo"
        if "Derrick" in _name[0] and "Jones" in _name[1]:
            _name[0] = "Derrick"
            _name[1] = "Jones, Jr."

        return _name

    def __init__(self,name=None, data=None):

        if name is not None:
            self.name = name

        if data is not None:
            self.name = data["Name"]
            self.salary = data["Salary"]
            self.position = data["Position"]
            self.gameInfo = data["GameInfo"]
            self.team = data["teamAbbrev"].upper()
            self.fantasyPointAverage = data["AvgPointsPerGame"]
            if "dvp" in data:
                self.dvp = data["dvp"]

        first, last = Player.fixName(self.name)

        try:
            if "Nene" in first:
                self.pid = 2403
            else:
                self.pid = get_player(first, last, only_current=1)
                self.pid = self.pid.values[0]
        except Exception as ee:
            print("Problem with player " + self.name)
            print(ee)
            self.error = 1
            self.db = 0
            pass
            return None

        _info = session.execute(select([sql.Player]).where(sql.Player.PERSON_ID == self.pid))
        self.info = pd.DataFrame(_info.fetchall(), _info.keys())

        _logs2 = session.query(sql.PlayerLog).filter(sql.PlayerLog.Player_ID == self.pid).all()
        _logs = [getattr(x,"__dict__") for x in _logs2]

        _logs = pd.DataFrame.from_dict(_logs)

        if "GAME_DATE" in _logs.columns.values:
            _logs["GAME_DATE"] = pd.to_datetime(_logs["GAME_DATE"], utc=True)
            _logs.set_index("GAME_DATE", inplace=True)
            cols = ["PTS", "BLK", "STL", "AST", "REB", "FG3M", "TOV","DKFPS"]
            _logs[cols] = _logs[cols].apply(pd.to_numeric)
            self.seasonStats = _logs.sort_index(ascending=False)
        else:
            print("No GAME_DATE for " + self.name)
            self.error = 1
            self.logs = None
            self.db = 0
            pass

        self.db = 1
        return


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

    def getGameWithDate(self,_date):
        row = None
        from dateutil import parser
        _date = parser.parse(_date).strftime('%Y%m%d')

        if self.db:
            row = session.query(sql.PlayerLog).filter(sql.PlayerLog.Player_ID == self.pid,
                                                      sql.PlayerLog.GAME_DATE == _date).first()
            if row is not None:
                row = pd.DataFrame.from_dict([row.__dict__])

        return row

    def setFantasyAverage(self,avg):
        self.fantasyPointAverage= avg
        return

    def addBonus (self, val):
        self.bonus += val
        return

    def getLastGame(self):
        if self.error == 1 or self.db == 0:
            return None

        try:
            return self.getSeasonStats()[:1]
        except:
            pass

        return

    def getSeasonStats(self,endDate = None):
        if self.error == 1:
            return

        statsTillDate = self.seasonStats

        if endDate is not None and statsTillDate is not None:
            statsTillDate = statsTillDate[endDate:'2016-01-01']
        elif self.endDate is not None and statsTillDate is not None:
            statsTillDate = statsTillDate[self.endDate:'2016-01-01']

        return statsTillDate

    def get7GameAvg(self):
            home = 0.0
            away = 0.0

            if self.error == 1 or self.db == 0:
                return  {"home": home, "away": away}

            try:
                p = self.getSeasonStats()
                home = p[p["MATCHUP"].str.contains("vs.")]["DKFPS"][:7].mean()
                away = p[p["MATCHUP"].str.contains("@")]["DKFPS"][:7].mean()
            except:
                home = 0.0
                away = 0.0

            return {"home": home, "away": away}

    def get4GameAvg(self):
            if self.error == 1 or self.db == 0:
                return 0

            try:
                p = self.getSeasonStats()
                avg = p.iloc[:4]["DKFPS"].mean()
            except:
                avg = 0.0

            return avg

    def getFloorAverage(self):
            if self.error == 1 or self.db == 0:
                return 0

            try:
                p = self.getSeasonStats()
                lowerBound = p[(p.DKFPS < p.DKFPS.mean())]
                lowerMean = lowerBound.DKFPS.mean()
            except:
                lowerMean = 0.0

            return lowerMean

    def getSeasonAverage(self):
        if self.error == 1 or self.db == 0:
            return 0

            p = self.getSeasonStats()
            if p is not None:
                seasonAverage = p["DKFPS"].mean()
            else:
                print("Could not find player..." + p.name)
                self.error = 1
                seasonAverage = 0

            return seasonAverage


    def __repr__(self):
         return "Player// "+self.name + ("(I)" if (self.injury!=None) else "")

    def __str__(self):
         return "Player// "+self.name + ("(I)" if (self.injury!=None) else "")

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.name == other.name
        return self.name == other


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
            self.teams[abbr].addPlayer(Player(data = playerdata))

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

def calculate(_date):

    injuries_file = 'data/injuries/' + _date + '.json'
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

    try:
        if os.path.isfile(injuries_file):
            with open(injuries_file) as json_data:
                injuries = json.load(json_data)
        else:
            injuries = []
    except:
        print("Failed to load injuries file.")
        injuries = []


    try:
        with open(calendar_file) as json_data:
            calendar = json.load(json_data)
    except:
        print("Failed to load calendar file.")
        calendar = []

    cal = Calendar()
    cal.load(calendar)
    all_players = pd.read_csv(newestSalaries)
    teams = Teams()
    teams.load(all_players)
    teams.setInjuries(injuries)

    from dateutil import parser
    dt = parser.parse(_date)
    day = datetime.timedelta(days=1)
    teams.setEndDate(dt - day)

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

    efgs = dataset
    efgs["atHome"] = 0
    efgs["injured"] = 0
    efgs["7GameAvg"] = 0.0
    efgs["FloorAvg"] = 0.0
    efgs["4GameAvg"] = 0.0
    efgs["LastGame"] = 0.0
    efgs["dvp"] = 0.0
    efgs["value"] = 0.0
    efgs["fvalue"] = 0.0
    efgs["odds"] = 0.0
    efgs["O/U"] = 0.0

    for index, row in efgs.iterrows():
        try:
            player = teams.findPlayer(row[1])
        except:
            print("failed to load player: " + row[1])
            pass

        if player is not None and player.team != '':
            efgs.loc[index, ("injured")] = 1 if (player.injury) else 0

            efgs.loc[index, ("atHome")] = 1 if player.home else 0

            SvnGameAvg = player.get7GameAvg()

            if player.home:
                SvnGameAvg = SvnGameAvg["home"]
            else:
                SvnGameAvg = SvnGameAvg["away"]

            if SvnGameAvg > 0:
                efgs.loc[index, ("7GameAvg")] = SvnGameAvg

            floorAvg = player.getFloorAverage()

            if floorAvg > 0:
                efgs.loc[index, ("FloorAvg")] =  floorAvg

            frGameAvg = player.get4GameAvg()
            if frGameAvg > 0:
                efgs.loc[index, ("4GameAvg")] = frGameAvg

            val = 0.00
            lg = player.getLastGame()

            if player.error == 0 and player.db == 1 and lg is not None and "DKFPS" in lg.columns.values:
                    val = lg["DKFPS"].mean()

            efgs.loc[index, ("LastGame")] = val

            playerValue = player.salary * 0.001 * 6

            efgs.loc[index, ("fvalue")] = 0.0

            if player.error == 0 and player.db == 1 and player.getSeasonStats() is not None and "DKFPS" in player.getSeasonStats().columns.values:
                games= list(player.getSeasonStats()["DKFPS"].values)
                games.append(playerValue)
                chanceOfHittingValue = st.norm.cdf(zscore(games))[-1:][0]
                # CDF gives us the probability of it being < than X ...so 1 - gives us more than
                efgs.loc[index, ("fvalue")] = 1.0 - chanceOfHittingValue
            else:
                print("Failed to get seasonStats for " + player.name)

            efgs.loc[index, ("dvp")] = player.dvp or 0.00
            efgs.loc[index, ('value')] = playerValue or 0.00

            ou = 0
            odds = 0
            if player.team.upper() in vegas.index.values:
                ou = vegas.loc[player.team.upper()]["overUnder"]
                odds = vegas.loc[player.team.upper()]["odds"]
            else:
                print("player not in vegas " + player.name + " " + player.team.upper())

            if ou > 0:
                efgs.loc[index, ("O/U")] = ou

            if abs(odds) > 0:
                efgs.loc[index, ("odds")] = odds

    efgs.to_csv(output_file, sep=',', encoding='utf-8', index=False, float_format='%.3f')


if __name__ == "__main__":
    calculate(today)
    # #calculate("2017-01-28")
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
