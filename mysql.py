#!/usr/bin/env python

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy import Column, DateTime, String, DECIMAL, Integer, ForeignKey, func,Date,Float, Numeric, Boolean
from sqlalchemy.sql import select
from sqlalchemy.ext.hybrid import hybrid_property,hybrid_method
from sqlalchemy import UniqueConstraint
from dateutil import parser

settings = {
    "mysql_user": "root",
    "mysql_pwd": "",
    "mysql_host":"127.0.0.1",
    "mysql_db": "fantasy"
}
MysqlBase = declarative_base()

import pandas as pd

class Player(MysqlBase):
    __tablename__ ='playerlist'

    PERSON_ID = Column(Integer, primary_key=True, unique=True)
    DISPLAY_LAST_COMMA_FIRST = Column(String(32))
    DISPLAY_FIRST_LAST = Column(String(32))
    ROSTERSTATUS = Column(String(32))
    FROM_YEAR = Column(String(32))
    TO_YEAR = Column(String(32))
    PLAYERCODE = Column(String(32))
    TEAM_ID = Column(String(32))
    TEAM_CITY = Column(String(32))
    TEAM_NAME = Column(String(32))
    TEAM_ABBREVIATION = Column(String(32))
    TEAM_CODE = Column(String(32))
    GAMES_PLAYED_FLAG = Column(String(32))
    logs = None
    __logs = relationship("PlayerLog", lazy='joined')
    news = relationship("PlayerNews", lazy='joined')
    # df_logs = None

    def __repr__(self):
        return'<Player {0} {1}: {2}>'.format(self.PERSON_ID,
                                             self.DISPLAY_FIRST_LAST,
                                             self.TEAM_ABBREVIATION)

    def getLogs(self,session = None):
        if not session:
            session = get_session()
        _logs = session.execute(select([PlayerLog]).where(PlayerLog.Player_ID == self.PERSON_ID))
        self.logs = pd.DataFrame(data=_logs.fetchall(), columns=_logs.keys())
        return self.logs



class Season(MysqlBase):
    __tablename__ ='season'
    SEASON_ID = Column(Integer, primary_key = True)
    SEASON_IDS = Column(String(32))
    start = Column(Integer)
    end   =  Column(Integer)

    # "SELECT * FROM fantasy.game where id > 21700000 AND id <= 21701000;"
    def __init__(self,season):
        year = int(season.split("-")[1])-1
        self.SEASON_ID = 22000 + year
        self.SEASON_IDS = season
        self.start =  20000000+(year*10**5)
        self.end   = self.start + 1000
        super().__init__()
        return

#http://data.nba.net/json/cms/2017/league/nba_games.json
# {"h_abrv": "MIA", "v_abrv": "CHA", "id": 1421700001, "dt": "2017-07-01 11:00:00.0", "r_reg": "", "is_lp": true, "sg": true}
class Game(MysqlBase):
    __tablename__ = 'game'

    id = Column(Integer,primary_key=True)
    h_abrv = Column(String(32))
    v_abrv = Column(String(32))
    dt = Column(DateTime)
    r_reg = Column(String(32))
    is_lp = Column(Boolean)
    sg = Column(Boolean)

    def __repr__(self):
        return'<Game {0} {1}: {2}@{3}>'.format(self.id,
                                               self.dt,
                                               self.h_abrv,
                                               self.v_abrv)


class Salary(MysqlBase):
    __tablename__ ='salary'
    __table_args__ = (UniqueConstraint('GAME_ID', 'Player_ID', name='_player_per_game_per_season'),)
    #{"player_id":"712595",
    # "player_name":"Denzel Valentine",
    # "nickname":"Bulls",
    # "pos_main":"SG",
    # "fantasy_pts":"26.79",
    # "avg_pts":"23.17",
    # "fpts_diff":"+3.62",
    # "date":"2017-11-22",
    # "salary":"5,400",
    # "salary_diff":"600",
    # "salary_diff_percentage":"12.5",
    # "salary_change_html":"<td class=\"width-15 green\" id=\"salary-col\">+$600 (12.5%)<\/td>",
    # "salary_change":"12.5"}

    id = Column(Integer, primary_key=True, unique=True)
    fantasy_pts = Column(Numeric(5,2))
    avg_pts = Column(Numeric(5,2))
    fpts_diff = Column(Numeric(5,2))
    player_name = Column(String(100))
    date=Column(Date)
    salary = Column(Integer)
    salary_change = Column(Numeric(5,2))
    salary_diff = Column(Integer)
    salary_diff_percentage = Column(Numeric(5,2))
    GAME_ID = Column(Integer, ForeignKey(Game.id))
    GAME_DATE = Column(Date)
    Player_ID = Column(Integer, ForeignKey(Player.PERSON_ID))



    def __repr__(self):
        return'<Salary Player: {0} $>'.format(self.GAME_DATE,self.FAV,self.ODDS,self.OU)

class Vegas(MysqlBase):
    __tablename__ ='vegas'
    __table_args__ = (UniqueConstraint('GAME_ID', 'team', name='_team_per_game_'),)

    id = Column(Integer, primary_key=True, unique=True)
    GAME_DATE = Column(Date)
    team = Column(String(32))
    ou  = Column(Integer)
    odds = Column(Integer)
    GAME_ID = Column(Integer, ForeignKey(Game.id))

    def __repr__(self):
        return'<Vegas DT: {0} FAV: {1} ODDS:{2} OU:{3}>'.format(self.GAME_DATE,self.FAV,self.ODDS,self.OU)


class PlayerLog(MysqlBase,object):
    __tablename__ ='playerlogs'
    __columns__ = ['SEASON_ID' 'Player_ID' 'Game_ID' 'MATCHUP' 'WL' 'MIN' 'FGM' 'FGA'
 'FG_PCT' 'FG3M' 'FG3A' 'FG3_PCT' 'FTM' 'FTA' 'FT_PCT' 'OREB' 'DREB' 'REB'
 'AST' 'STL' 'BLK' 'TOV' 'PF' 'PTS' 'PLUS_MINUS' 'VIDEO_AVAILABLE',"DKFPS"]
    __table_args__ = (UniqueConstraint('Player_ID', 'Game_ID','SEASON_ID', name='_player_per_game_per_season'), )

    id = Column(Integer, primary_key=True)
    SEASON_ID = Column(Integer, ForeignKey(Season.SEASON_ID))
    Player_ID = Column(Integer, ForeignKey(Player.PERSON_ID))
    Game_ID = Column(Integer, ForeignKey(Game.id))
    GAME_DATE = Column(Date)
    MATCHUP = Column(String(32))
    WL = Column(String(32))
    MIN = Column(Integer)
    FGM = Column(Integer)
    FGA = Column(Integer)
    FG_PCT = Column(Float)
    FG3M = Column(Integer)
    FG3A = Column(Integer)
    FG3_PCT = Column(Float)
    FTM = Column(Integer)
    FTA = Column(Integer)
    FT_PCT = Column(Float)
    OREB = Column(Integer)
    DREB = Column(Integer)
    REB = Column(Integer)
    AST = Column(Integer)
    STL = Column(Integer)
    BLK = Column(Integer)
    TOV = Column(Integer)
    PF = Column(Integer)
    PTS = Column(Integer)
    PLUS_MINUS = Column(String(32))
    VIDEO_AVAILABLE = Column(String(32))
    DKFPS = Column(Float)
    valid = 1

    def __init__(self,**row):
        row["GAME_DATE"] = parser.parse(row["GAME_DATE"]).date()
        if row is not None:
            super().__init__(**row)
        self.DKFPS = self.calculateDKFPS()
        return

    def calculateDKFPS(self):
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

        if self.valid == 0:
            return 0

        try:
            keys = ['PTS', 'BLK', 'STL', 'AST', 'REB', 'FG3M', 'TOV']
            try:
                values = [getattr(self, x) for x in ['PTS', 'BLK', 'STL', 'AST', 'REB', 'FG3M', 'TOV']]
            except Exception as e:
                print("Failed to get attributed")
                print(e)
                pass

            p = pd.DataFrame(data=[values], columns=keys)
            p = p.apply(pd.to_numeric)
            p["Bonus"] = p[p >= 10].count(axis=1, numeric_only=True)
            p.loc[p["Bonus"] < 2, "Bonus"] = 0.0
            p.loc[p["Bonus"] == 2, "Bonus"] = 1.5
            p.loc[p["Bonus"] > 2, "Bonus"] = 4.5
            p["DKFPS"] = 1 * (p.PTS) + 0.5 * (p.FG3M) + 1.25 * (p.REB) + 1.5 * (p.AST) + 2 * (p.STL) + 2 * (
            p.BLK) - 0.5 * (p.TOV) + p.Bonus
            return p["DKFPS"].values[0]
        except Exception as ee:
            print("There was an exception")
            print(ee)
            pass

        return

    def __repr__(self):
        return'<PlayerLog {0} {1}: {2}>'.format(self.Player_ID,
                                               self.GAME_DATE,
                                               self.PTS)




class PlayerNews(MysqlBase):
    __tablename__ ='playernews'
    __table_args__ = (UniqueConstraint('RotoId', 'UpdateId', name='_roto_id_per_update_id'),)

    id=Column(Integer, primary_key=True, unique=True)
    ListItemCaption = Column(String(600))
    ListItemDescription = Column(String(3000))
    ListItemPubDate = Column(DateTime)
    lastUpdate = Column(DateTime)
    UpdateId = Column(String(32))
    RotoId = Column(String(32))
    PlayerID = Column(Integer, ForeignKey(Player.PERSON_ID))
    FirstName = Column(String(32))
    LastName = Column(String(32))
    Position = Column(String(32))
    Team = Column(String(32))
    TeamCode = Column(String(32))
    Date = Column(String(32))
    Priority= Column(Integer)
    Headline= Column(String(500))
    Injured= Column(String(32))
    Injured_Status= Column(String(32))
    Injury_Location= Column(String(32))
    Injury_Type= Column(String(32))
    Injury_Detail= Column(String(32))
    Injury_Side=Column(String(32))

    def __init__(self,**row):
        row["ListItemPubDate"] = parser.parse(row["ListItemPubDate"])
        row["lastUpdate"] = parser.parse(row["lastUpdate"])
        if row is not None:
            super().__init__(**row)
        # self.DKFPS = self.calculateDKFPS()
        return

    def __repr__(self):
        return'<PlayerNews {0} {1}: {2}>'.format(self.ListItemCaption,
                                               self.ListItemPubDate,
                                               self.LastName)


_session = None

def get_session():
    global _session

    mysql_user = settings['mysql_user']
    mysql_pwd = settings['mysql_pwd']
    mysql_host = settings['mysql_host']
    mysql_db = settings['mysql_db']
    if not _session:
        uri = 'mysql+mysqldb://%s:%s@%s:3306/%s?charset=utf8' % (
            mysql_user, mysql_pwd, mysql_host, mysql_db)
        engine = create_engine(
            uri,
            encoding="utf8",
            echo=False,
            pool_size=5,
            pool_recycle=10)
        MysqlBase.metadata.create_all(engine)
        Session = sessionmaker()
        Session.configure(bind=engine)
        _session = Session()
    return _session