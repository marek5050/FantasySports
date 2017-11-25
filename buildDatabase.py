import json
import urllib
import urllib.request

from nba_py import player

import utils
from mysql import *


def create_players_table(seasons):
    session = get_session()
    for season in seasons:
        pl = player.PlayerList(season=season, only_current=1).info()
        for idx, row1 in pl.iterrows():
            try:
               session.add(Player(**row1.to_dict()))
               session.commit()
            except Exception as e:
                print(e)
                session.rollback()
    session.close()


def create_game_table(seasons):
    session = get_session()
    for year in seasons:
        year = year.split("-")[0]
        url = "http://data.nba.net/json/cms/%s/league/nba_games.json" % (year)
        with urllib.request.urlopen(url) as req:
            _schedule = json.loads(req.read().decode())
            for item in _schedule["sports_content"]["schedule"]["game"]:
                           try:
                               session.merge(Game(**item))
                               session.commit()
                           except Exception as e:
                               session.rollback()
    session.close()

## Need Teams

def create_player_logs(seasons):
    session = get_session()
    _players = session.execute(select([Player]))
    _players = _players.fetchall()
    created = 0
    errors = []
    for _player in _players:
        for season in seasons:
            try:
               logs = player.PlayerGameLogs(_player.PERSON_ID, season=season).info()
               for idx, item in logs.iterrows():
                   try:
                       session.add(PlayerLog(**item))
                       session.commit()
                       created = created + 1
                   except Exception as e:
                       errors.append(e)
                       session.rollback()

            except Exception as e:
                print("failed ")
                print(e)
    session.close()
    return created, errors

def create_seasons_table(seasons):
    session = get_session()

    for item in seasons:
        try:
            session.merge(Season(item))
            session.commit()
        except Exception as e:
            print(e)
            session.rollback()
    session.close()


def get_player(id=None, name=None):
    session = get_session()
    if id is not None:
        return session.query(Player).filter(Player.PERSON_ID == id).first()
    if name is not None:
        return session.query(Player).filter(Player.DISPLAY_FIRST_LAST == name).first()
    session.close()

# player = get_player(name="LeBron James")
# print(player)



# "2016-17" = 21701143
# "SELECT * FROM fantasy.game where id > 21700000 AND id <= 21701000;"



#
#
# #     except Exception as e:
# #         print(e)
# #     session.commit()
# #
# #
# # for _player in _players:
# #     print(_player.PERSON_ID)
# #     try:
# #        logs = player.PlayerGameLogs(_player.PERSON_ID, season="2016-17").info()
# #        session.bulk_save_objects([
# #                                    PlayerLog(**row1)
# #                                    for idx,row1 in logs.iterrows()
# #                                  ], return_defaults=True)
# #     except Exception as e:
# #         print(e)
# # session.commit()
# #
# # for _player in _players:
# #     print(_player.PERSON_ID)
# #     try:
# #        logs = player.PlayerGameLogs(_player.PERSON_ID).info()
# #        # for idx,row1 in logs.iterrows():
# #        #     instance = get_or_create(session=session,model=PlayerLog, **row1)
# #        for item in logs:
# #            try:
# #                session.merge(PlayerLog(**item))
# #                session.commit()
# #            except Exception as e:
# #                session.rollback()
# #
# #     except Exception as e:
# #         pass
#
# #
# #
# # from mysql import *
# #
# # from nba_py import player
# # from nba_py.player import get_player
#

def build_salary(_date):
    import glob
    import pandas as pd
    print("build_salary: %s" % (_date))
    main = pd.DataFrame()
    path = r'./data/old_salaries'  # use your path
    allFiles = glob.glob("%s/dk_%s.csv" %(path,_date))
    print("Number of files: %d" % (len(allFiles)))
    for _file in allFiles:
        try:
            _date = _file.split("/")[3].replace(".csv", "").replace("dk_","")
            table = pd.read_csv(_file)
            table["GAME_DATE"] = _date
            main = main.append(table)
        except Exception as e:
            print("Error with date: " + _date)
            print(e)

    if len(allFiles) > 0:
        main["GAME_DATE"] = pd.to_datetime(main["GAME_DATE"])
        main["date"]= pd.to_datetime(main["date"])

    return main


def build_vegas(_date):
    import glob
    import pandas as pd
    print("build_vegas")
    _vegas = pd.DataFrame()
    found = 0
    notfound = 0
    path = r'./data/vegas'  # use your path
    allFiles = glob.glob("%s/%s.csv" % (path, _date))
    print("Number of files: %d" % (len(allFiles)))
    for _file in allFiles:
        try:
            _date = _file.split("/")[3].replace(".csv", "")
            vegas1 = pd.read_csv(_file)
            vegas1["GAME_DATE"] = _date
            _vegas = _vegas.append(vegas1)
        except Exception as e:
            print("Error with date: " + _date)
            print(e)
    if len(allFiles) > 0:
        _vegas["GAME_DATE"] = pd.to_datetime(_vegas["GAME_DATE"])

    return _vegas

def create_vegas_table(_date):
    import datetime
    df = build_vegas(_date)
    session = get_session()
    for idx,item in df.iterrows():
        item["team"] = utils.fixTeam(item["team"])
        try:
           game = utils.get_game(date=item["GAME_DATE"],team=item["team"])
           if len(game) == 0:
               game = utils.get_game(date=item["GAME_DATE"]-datetime.timedelta(days=1),
                                     to_date=item["GAME_DATE"]+datetime.timedelta(days=1),
                                     team=item["team"])
           if len(game) > 0:
               _line = dict()
               _line["GAME_DATE"]= item["GAME_DATE"]
               _line["GAME_ID"] = game[0].id
               _line["team"] = item["team"]
               _line["odds"] = item["odds"]
               _line["ou"] = item["overUnder"]
               session.add(Vegas(**_line))
               session.commit()
           else:
               print("Vegas: could not locate game: %s with %s , len(%d) " % (
               _line["GAME_DATE"], _line["team"], len(game)))

        except Exception as e:
            print(e)
            session.rollback()
    session.close()


import datetime
import pandas as pd

def create_all_salaries():
    df = build_salary("*")
    df["GAME_DATE"] = pd.to_datetime(df["GAME_DATE"])
    create_salary_table(df)

def create_salary_table(df):
    # df = df.ix[df["date"]>='2016-10-25']
    session = get_session()
    player_miss = dict()
    game_miss = []
    failed = []
    # df[df["avg_pts"]=='-']["avg_pts"]=0
    # df[df["fpts_diff"] == '-']["fpts_diff"] = 0

    for idx,item in df.iterrows():
            if item["player_name"] in player_miss:
                continue

            player = utils.get_player(name = item["player_name"])
            if player is not None:
                game = utils.get_game(date=item["GAME_DATE"], to_date=item["GAME_DATE"] + datetime.timedelta(days=1),
                                      team=player.TEAM_ABBREVIATION)
                if game is None:
                    game = utils.get_game(date=item["date"],to_date=item["GAME_DATE"]+datetime.timedelta(days=1), team=player.TEAM_ABBREVIATION)

                if len(game) > 0:
                       item["GAME_ID"] = game[0].id
                else:
                    print("Could not locate game between(%s, %s) %s for %s" % (item["date"], item["GAME_DATE"],player.TEAM_ABBREVIATION, player.PLAYERCODE))
                    game_miss.append(item)

                if item["avg_pts"] == "-":
                    item["avg_pts"]=0
                if item["fpts_diff"] == "-":
                    item["fpts_diff"]=0


                del item["pos_main"]
                del item["salary_change_html"]
                del item["nickname"]
                del item["player_id"]
                try:
                   # _line["avg_pts"]= item["avg_pts"]
                   item["salary"] = item["salary"].replace(",","")
                   # item["salary_diff"] = item["salary_diff"].replace(",", "")
                   # _line["fantasy_pts"] = item["fantasy_pts"]
                   item["Player_ID"] = player.PERSON_ID
                   session.add(Salary(**item))
                   session.commit()
                except Exception as e:
                   print("Failed creating salary:%s: %s - %s" %(item["GAME_DATE"], item["player_name"], item["salary"]))
                   print("Error: %s" % (e))
                   failed.append(item)
                   session.rollback()

            else:
                print("(%s) no player %s" %(item["GAME_DATE"],item["player_name"]))
                if item["player_name"] not in player_miss:
                    player_miss[item["player_name"]] = item

    print("Player_miss: %d , game_miss: %d, failed: %d"%(len(player_miss),len(game_miss), len(failed)))
    session.close()


# https://data.nba.com/data/10s/v2015/json/mobile_teams/nba/2017/league/00_full_schedule_week.json
seasons = ["2016-17", "2017-18"]
# create_seasons_table(seasons)
# create_game_table(seasons)
# create_players_table(seasons)
# create_player_logs(seasons)
# create_dk_player_map()

    # create_vegas_table("*")
# create_game_table()
# create_all_salaries()
