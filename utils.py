# -*- coding: utf-8 -*-

import datetime

import pandas as pd
from sqlalchemy.orm import raiseload
from sqlalchemy.sql import select

import mysql as sql


def get_all_players():
    session = sql.get_session()

    _players = session.execute(select([sql.Player]).where(sql.Player.TO_YEAR == 2017))
    players = pd.DataFrame(_players.fetchall())
    players.columns = _players.keys()
    session.close()

    return players


# players = get_all_players()
# misses=[]

def get_all_logs(players):
    session = sql.get_session()

    hit = 0
    miss = 0
    logs = dict()
    misses = []
    for person_id in players.PERSON_ID:
        _logs2 = session.query(sql.PlayerLog).filter(sql.PlayerLog.Player_ID == person_id).all()
        if len(_logs2) == 0:
            miss += 1
            misses.append(person_id)
        else:
            hit += 1
        logs[person_id] = pd.DataFrame([getattr(x, "__dict__") for x in _logs2])

    print("Hit %d \t Miss %d" % (hit, miss))
    session.close()
    return logs, misses


def get_player_logs(player_id):
    session = sql.get_session()

    logs = session.query(sql.PlayerLog).filter(sql.PlayerLog.Player_ID == player_id).all()
    logs = pd.DataFrame([getattr(x, "__dict__") for x in logs])
    session.close()
    return logs


# q = session.query(User).filter(User.name.like('e%')).\
#     limit(5).from_self().\
#     join(User.addresses).filter(Address.email.like('q%'))

def get_player_logs_season(season):
    session = sql.get_session()

    logs = session.query(sql.PlayerLog).join(sql.Season).filter(sql.Season.SEASON_IDS.like(season)).all()
    logs = pd.DataFrame([getattr(x, "__dict__") for x in logs])
    session.close()
    return logs


def toNBA(name):
    try:
        name = str.strip(name)
    except Exception as e:
        print("exception:%s " % e)

    if name == "J.R. Smith":
        name = "JR Smith"
    if name == "A.J. Hammons":
        name = "AJ Hammons"

    if name == "Jose Juan Barea":
        name = "J.J. Barea"

    if name == "Taurean Waller-Prince":
        name = "Taurean Prince"

    if name == "Brad Beal":
        name = "Bradley Beal"

    if name == "Domas Sabonis":
        name = "Domantas Sabonis"

    if name == "Ishmael Smith":
        name = "Ish Smith"

    if name == "Wayne Selden Jr.":
        name = "Wayne Selden"

    if name == "Vince Hunter":
        name = "Vincent Hunter"

    if name == "C.J. Miles":
        name = "CJ Miles"
    if name == "T.J. Warren":
        name = "TJ Warren"

    if name == "C.J. Wilcox":
        name = "CJ Wilcox"

    if name == "R.J. Hunter":
        name = "RJ Hunter"

    if name == "Andrew White III":
        name = "Andrew White"

    if name == "Juancho Hernangomez":
        name = "Juan Hernangomez"

    if name == "Dennis Smith, Jr.":
        name = "Dennis Smith Jr."

    if name == "Matt Williams":
        name = "Matt Williams Jr."

    if name == "K.J. McDaniels":
        name = "KJ McDaniels"

    if name == "Wesley Iwundu":
        name = "Wes Iwundu"

    if name == "Frank Mason III":
        name = "Frank Mason"

    if name == "C.J. McCollum":
        name = "CJ McCollum"
    if name == "Nene Hilario":
        name = "Nene"
    if name == "Luc Richard Mbah a Moute":
        name = "Luc Mbah a Moute"
    if name == "J.J. Redick":
        name = "JJ Redick"
    if name == "Otto Porter":
        name = "Otto Porter Jr."
    if name == "P.J. Tucker":
        name = "PJ Tucker"
    return name


def toDraftKings(name):
    if name == "C.J. McCollum":
        name = "CJ McCollum"
    if name == "Nene Hilario":
        name = "Nene"
    if name == "Luc Richard Mbah a Moute":
        name = "Luc Mbah a Moute"
    if name == "J.J. Redick":
        name = "JJ Redick"
    if name == "Otto Porter":
        name = "Otto Porter Jr."
    if name == "P.J. Tucker":
        name = "PJ Tucker"
    return name

def get_player(id=None, name=None, firstName = None, lastName = None):
    session = sql.get_session()

    q = session.query(sql.Player)

    if id is not None:
        q = q.filter(sql.Player.PERSON_ID == id)
    elif name is not None:
        name = toNBA(name)

        q = q.filter(sql.Player.DISPLAY_FIRST_LAST == name)
    elif firstName is not None and lastName is not None:
        q = q.filter(sql.Player.DISPLAY_FIRST_LAST == "%s %s" %(firstName,lastName))

    player = q.first()
    session.close()
    return player

def get_boxscores(season=None, beforeToday=True, includeToday=True):
    session = sql.get_session()
    q = session.query(sql.Boxscore).options(raiseload('*'))
    if season is not None:
        s = session.query(sql.Season).filter(sql.Season.SEASON_IDS.like(season)).first()
        q = q.filter(sql.Boxscore.GAME_ID >= s.start).filter(sql.Boxscore.GAME_ID <= s.end)

    session.close()
    return pd.read_sql_query(q.statement, session.bind)


def get_games(season=None, beforeToday=True, includeToday=True):
    session = sql.get_session()
    q = session.query(sql.Game).options(raiseload('*'))
    if season is not None:
        s = session.query(sql.Season).filter(sql.Season.SEASON_IDS.like(season)).first()
        q = q.filter(sql.Game.id >= s.start).filter(sql.Game.id <= s.end)
    if beforeToday:
        if includeToday:
            now = datetime.datetime.now()+datetime.timedelta(1)
            q = q.filter(sql.Game.dt <= now)
        else:
            now = datetime.datetime.now()
            q = q.filter(sql.Game.dt < now)

    session.close()

    return pd.read_sql_query(q.statement, session.bind)

def get_playoff_games(season=None, beforeToday=True, includeToday=False):
    session = sql.get_session()
    q = session.query(sql.Game)
    if season is not None:
        s = session.query(sql.Season).filter(sql.Season.SEASON_IDS.like(season)).all()
        if len(s) > 1 and s[1].end is not None and s[1].start is not None:
            q = q.filter(sql.Game.id >= s[1].start).filter(sql.Game.id <= s[1].end)

    if beforeToday:
        if includeToday:
            now = datetime.datetime.now()+datetime.timedelta(1)
            q = q.filter(sql.Game.dt <= now)
        else:
            now = datetime.datetime.now()
            q = q.filter(sql.Game.dt < now)

    session.close()

    return pd.DataFrame([getattr(x, "__dict__") for x in q.all()])


def get_all_playerlist():
    session = sql.get_session()
    q = session.query(sql.Player).options(raiseload('*'))
    session.close()

    return pd.read_sql(q.statement, session.bind)

def get_all_games(season=None, beforeToday=True,includeToday=True):
    games = get_games(season,beforeToday, includeToday=includeToday)
    return games


def get_all_boxscores(season=None):
    games = get_boxscores(season)
    return games


def get_playoff_dates(season=None, beforeToday=True, includeToday=True):
    games = get_playoff_games(season, beforeToday, includeToday=includeToday)
    date_list = games["dt"].dt.date.unique()
    return date_list

def get_dates(season=None, beforeToday=True,includeToday=True):
    games = get_games(season,beforeToday, includeToday=includeToday)
    date_list = games["dt"].dt.date.unique()
    return date_list


def get_game(date=None, team=None, to_date=None):
    session = sql.get_session()
    from sqlalchemy import cast, DATE
    from sqlalchemy import or_

    q = session.query(sql.Game)

    if date is not None and to_date is not None:
        q = q.filter(cast(sql.Game.dt, DATE).between(date,to_date))
    elif date is not None:
        q = q.filter(cast(sql.Game.dt, DATE) == date)

    if team is not None:
        # team = team.lower()
        team = fixTeam(team)
        q = q.filter(or_(sql.Game.h_abrv == team, sql.Game.v_abrv == team))
    game = q.all()
    session.close()
    return game


def fixTeam(abb):
    if abb == "SA":
        return "SAS"
    if abb == "NOR":
        return "NOP"
    if abb == "NO":
        return "NOP"
    if abb == "NY":
        return "NYK"
    if abb == "GS":
        return "GSW"
    if abb == "PHO":
        return "PHX"
    if abb == "UTH":
        return "UTA"
    return abb


def truncate(f, n):
    '''Truncates/pads a float f to n decimal places without rounding'''
    s = '{}'.format(f)
    if 'e' in s or 'E' in s:
        return '{0:.{1}f}'.format(f, n)
    i, p, d = s.partition('.')
    return '.'.join([i, (d+'0'*n)[:n]])
