import argparse
from sqlalchemy import Column, ForeignKey, Integer, String, Date
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine

Base = declarative_base()
from sqlalchemy import Column, DateTime, String, Integer, ForeignKey, func
from sqlalchemy.orm import relationship, backref
from sqlalchemy.ext.declarative import declarative_base

MysqlBase = declarative_base()


class PlayerLog(MysqlBase):
    __tablename__ ='playerlogs'

    id = Column(Integer, primary_key=True)
    SEASON_ID = Column(String(32))
    Player_ID = Column(String(32))
    Game_ID = Column(String(32))
    GAME_DATE = Column(String(32))
    MATCHUP = Column(String(32))
    WL = Column(String(32))
    MIN = Column(String(32))
    FGM = Column(String(32))
    FGA = Column(String(32))
    FG_PCT = Column(String(32))
    FG3M = Column(String(32))
    FG3A = Column(String(32))
    FG3_PCT = Column(String(32))
    FTM = Column(String(32))
    FTA = Column(String(32))
    FT_PCT = Column(String(32))
    OREB = Column(String(32))
    DREB = Column(String(32))
    REB = Column(String(32))
    AST = Column(String(32))
    STL = Column(String(32))
    BLK = Column(String(32))
    TOV = Column(String(32))
    PF = Column(String(32))
    PTS = Column(String(32))
    PLUS_MINUS = Column(String(32))
    VIDEO_AVAILABLE = Column(String(32))

    # def __init__(self, data):
    #     self.data = data
    #     for k in data:
    #         self[k] = data[k]

    def __repr__(self):
        return'<PlayerLog {0} {1}: {2}>'.format(self.Player_ID,
                                               self.GAME_DATE,
                                               self.PTS)

def create_model(db_addr):
  engine = create_engine(db_addr)
  Base.metadata.create_all(engine)

def main(args):
  name = args.name
  #db_addr = 'sqlite:///twitter_'+name+'.db'
  #create_model(db_addr)

#if __name__ == '__main__':
  #parser = argparse.ArgumentParser(description='Twitter ORM database creator')
  #parser.add_argument('name', type=str, help='The model name used to create the ORM database')
  #args = parser.parse_args()
  #main(args)
