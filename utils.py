# -*- coding: utf-8 -*-

import json
import pandas as pd
import datetime
from scipy.stats import zscore
import os.path
import scipy.stats as st
import mysql as sql
from sqlalchemy.sql import select
from nba_py.player import get_player


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


def get_player(id=None, name=None, firstName = None, lastName = None):
    session = sql.get_session()

    q = session.query(sql.Player)

    if id is not None:
        q = q.filter(sql.Player.PERSON_ID == id)
    elif name is not None:
        import re
        p = re.compile('([A-Z])\.([A-Z])\. (.+)')
        res = p.match(name)
        if res != None:
            name = "%s%s %s" % (res.group(1),res.group(2),res.group(3))
        # name = name.replace("J.J.","JJ").replace("J.R.","JR")
        q = q.filter(sql.Player.DISPLAY_FIRST_LAST == name)
    elif firstName is not None and lastName is not None:
        q = q.filter(sql.Player.DISPLAY_FIRST_LAST == "%s %s" %(firstName,lastName))

    session.close()
    return q.first()

def get_games(season=None, beforeToday=True):
    session = sql.get_session()
    q = session.query(sql.Game)
    if season is not None:
        s = session.query(sql.Season).filter(sql.Season.SEASON_IDS.like(season)).first()
        q = q.filter(sql.Game.id >= s.start).filter(sql.Game.id <= s.end)
    if beforeToday:
        now = datetime.datetime.now()
        q = q.filter(sql.Game.dt < now)
    session.close()

    return pd.DataFrame([getattr(x, "__dict__") for x in q.all()])


def get_dates(season=None, beforeToday=True):
    games = get_games(season,beforeToday)
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
        q = q.filter(or_(sql.Game.h_abrv == team, sql.Game.v_abrv == team))
    game = q.all()
    session.close()
    return game
