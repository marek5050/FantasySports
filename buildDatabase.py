import json
import urllib
import urllib.request

import _mysql_exceptions
from nba_py.constants import *
from _mysql_exceptions import DataError
from nba_py import player

from mysql import *

team_abbrev = "SAC,DAL,LAC,MIL,LAL,SAS,DEN,MIN,PHX,UTA,,ATL,HOU,GSW,CLE,OKC,MIA,CHA,IND,NOP,NYK,DET,BOS,WAS,TOR,PHI,BKN,MEM,ORL,CHI,POR".split(
    ",")
team_names = "Kings,Mavericks,Clippers,Bucks,Lakers,Spurs,Nuggets,Timberwolves,Suns,Jazz,,Hawks,Rockets,Warriors,Cavaliers,Thunder,Heat,Hornets,Pacers,Pelicans,Knicks,Pistons,Celtics,Wizards,Raptors,76ers,Nets,Grizzlies,Magic,Bulls,Trail Blazers".split(
    ",")

import datetime
now = datetime.datetime.now()

def get_abbrev(team_name):
    for i, item in enumerate(team_names):
        if item == team_name:
            return team_abbrev[i]


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


def create_game_table_2(seasons):
    from dateutil.parser import parse
    session = get_session()
    for year in seasons:
        year = year.split("-")[0]
        url = "http://data.nba.net/data/10s/prod/v1/%s/schedule.json" % (year)
        with urllib.request.urlopen(url) as req:
            _schedule = json.loads(req.read().decode())
            for item in _schedule["league"]["standard"]:
                try:
                    # {"h_abrv": "MIA", "v_abrv": "CHA", "id": 1421700001, "dt": "2017-07-01 11:00:00.0", "r_reg": "", "is_lp": true, "sg": true}
                    send = dict()
                    send["id"] = item["gameId"]
                    send["v_abrv"] = item["gameUrlCode"].split("/")[1][0:3]
                    send["h_abrv"] = item["gameUrlCode"].split("/")[1][3:]
                    send["dt"] = parse(item["startTimeUTC"])
                    send["r_reg"] = None
                    send["is_lp"] = None
                    send["sg"] = None
                    session.merge(Game(**send))
                    session.commit()
                except Exception as e:
                    print(e)
                    session.rollback()
    session.close()


## Need Teams

def create_player_logs(seasons, verbose=True):
    session = get_session()
    _players = session.execute(select([Player]))
    _players = _players.fetchall()
    if verbose:
        print("players: %d" % (len(_players)))
    created = 0
    errors = []
    for _player in _players:
        if verbose:
            print(_player["DISPLAY_FIRST_LAST"])
        for season in seasons:
            try:
                logs = player.PlayerGameLogs(_player.PERSON_ID, season=season, season_type=SeasonType.Playoffs).info()
                for idx, item in logs.iterrows():
                    try:
                        # seasonid=22016
                        # playoffs = 42016
                        session.add(PlayerLog(**item))
                        session.commit()
                        created = created + 1
                    except Exception as e:
                        print(e)
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
    allFiles = glob.glob("%s/dk_%s.csv" % (path, _date))
    print("Number of files: %d" % (len(allFiles)))
    for _file in allFiles:
        try:
            _date = _file.split("/")[3].replace(".csv", "").replace("dk_", "")
            table = pd.read_csv(_file)
            table["GAME_DATE"] = _date
            main = main.append(table)
        except Exception as e:
            print("Error with date: " + _date)
            print(e)

    if len(allFiles) > 0:
        main["GAME_DATE"] = pd.to_datetime(main["GAME_DATE"])
        main["date"] = pd.to_datetime(main["date"])

    return main


def build_vegas(date_list):
    import glob
    import pandas as pd
    print("build_vegas")
    _vegas = pd.DataFrame()
    found = 0
    notfound = 0
    path = r'./data/vegas'  # use your path
    allFiles = []
    for _date in date_list:
        allFiles.append(glob.glob("%s/%s.csv" % (path, _date)))

    print("Number of files: %d" % (len(allFiles)))
    for _file_set in allFiles:
        for _file in _file_set:
            try:
                _date = _file.split("/")[3].replace(".csv", "")
                vegas1 = pd.read_csv(_file)
                vegas1["GAME_DATE"] = _date
                _vegas = _vegas.append(vegas1)
            except Exception as e:
                print("Error with date: " + _file)
                print(e)
    if len(allFiles) > 0:
        _vegas["GAME_DATE"] = pd.to_datetime(_vegas["GAME_DATE"])

    return _vegas


def create_vegas_table(df):
    import datetime
    session = get_session()
    for idx, item in df.iterrows():
        item["team"] = utils.fixTeam(item["team"])
        try:
            game = utils.get_game(date=item["GAME_DATE"], team=item["team"])
            if len(game) == 0:
                game = utils.get_game(date=item["GAME_DATE"] - datetime.timedelta(days=1),
                                      to_date=item["GAME_DATE"] + datetime.timedelta(days=1),
                                      team=item["team"])
            if len(game) > 0:
                _line = dict()
                _line["GAME_DATE"] = item["GAME_DATE"]
                _line["GAME_ID"] = game[0].id
                _line["team"] = item["team"]
                _line["odds"] = item["odds"]
                _line["ou"] = item["overUnder"]
                session.add(Vegas(**_line))
                session.commit()
            else:
                print("Vegas: could not locate game: %s with %s , len(%d) " % (
                    item["GAME_DATE"], item["team"], len(game)))

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
    hit = 0
    # df[df["avg_pts"]=='-']["avg_pts"]=0
    # df[df["fpts_diff"] == '-']["fpts_diff"] = 0

    for idx, item in df.iterrows():
        if item["player_name"] in player_miss:
            continue

        player = utils.get_player(name=item["player_name"])
        if player is not None:
            game = utils.get_game(date=item["GAME_DATE"], to_date=item["GAME_DATE"] + datetime.timedelta(days=1),
                                  team=get_abbrev(item["nickname"]))
            if game is None:
                game = utils.get_game(date=item["GAME_DATE"] + datetime.timedelta(days=-1),
                                      to_date=item["GAME_DATE"] + datetime.timedelta(days=1),
                                      team=get_abbrev(item["nickname"]))

            if len(game) > 0:
                item["GAME_ID"] = game[0].id
            else:
                print("Could not locate game between(%s, %s) %s for %s" % (
                item["date"], item["GAME_DATE"], player.TEAM_ABBREVIATION, player.PLAYERCODE))
                game_miss.append(item)

            if item["avg_pts"] == "-":
                item["avg_pts"] = 0
            if item["fpts_diff"] == "-":
                item["fpts_diff"] = 0

            del item["pos_main"]
            del item["salary_change_html"]
            del item["nickname"]
            del item["player_id"]
            try:
                # _line["avg_pts"]= item["avg_pts"]
                item["salary"] = item["salary"].replace(",", "")
                # item["salary_diff"] = item["salary_diff"].replace(",", "")
                # _line["fantasy_pts"] = item["fantasy_pts"]
                item["Player_ID"] = player.PERSON_ID
                session.add(Salary(**item))
                session.commit()
                hit += 1
            except Exception as e:
                # print("Failed creating salary:%s: %s - %s" %(item["GAME_DATE"], item["player_name"], item["salary"]))
                # print("Error: %s"%(e))
                failed.append(item)
                session.rollback()

        else:
            print("(%s) no player %s" % (item["GAME_DATE"], item["player_name"]))
            if item["player_name"] not in player_miss:
                player_miss[item["player_name"]] = item

    print("Hit: %d\tPlayer_miss: %d\t game_miss: %d\tfailed: %d" % (hit, len(player_miss), len(game_miss), len(failed)))
    session.close()


def build_game_stats(seasons, id_filter=0, last_n=0):
    from nba_py import game
    session = get_session()
    failed = []
    good = 0
    for season in seasons:
        games = utils.get_all_games(season,beforeToday=True,includeToday=False)
        _exists = utils.get_all_boxscore_ids(season)
        newgames = pd.concat([_exists, games,_exists]).drop_duplicates(keep=False)
        for idx, grow in newgames[(newgames["id"]>=id_filter) & (newgames["dt"] >= (now - datetime.timedelta(days=last_n)))].iterrows():
            print("Game: %s" % grow["id"])
            game_id = str(grow["id"]).zfill(10)
            boxscore = game.Boxscore(game_id).player_stats()
            advboxscore = game.BoxscoreAdvanced(game_id).sql_players_advanced()
            fourfactors = game.BoxscoreFourFactors(game_id).sql_players_four_factors()
            boxmisc = game.BoxscoreMisc(game_id).sql_players_misc()
            for idx, row in boxscore.iterrows():
                try:
                    box = Boxscore(**row)
                    adv = BoxscoreAdvanced(**advboxscore.iloc[idx])
                    ff = BoxscoreFourFactors(**fourfactors.iloc[idx])
                    misc = BoxscoreMisc(**boxmisc.iloc[idx])
                    session.add(box)
                    session.add(adv)
                    session.add(ff)
                    session.add(misc)
                    session.commit()
                    good+=1
                except DataError as e:
                    print("Data error: %s " %e)
                    failed.append(row)
                    session.rollback()
                except Exception as e:
                    # print("Failed creating salary:%s: %s - %s" %(item["GAME_DATE"], item["player_name"], item["salary"]))
                    print("Other Error: %s" % e)
                    failed.append(row)
                    session.rollback()
    print("Done.")

def build_team_stats(seasons):
    from nba_py import team
    from nba_py import constants
    session = get_session()

    errors=[]
    teams = team.TeamList().info()

    created = 0
    for season in seasons:
        for idx,tm in teams[pd.to_numeric(teams["MAX_YEAR"])>=2017].iterrows():
            atm = Team(**tm)
            try:
                session.add(atm)
                session.commit()
            except Exception as e:
                session.rollback()
                print("Team exists %s" % e)

            normal_tm = team.TeamGameLogs(tm["TEAM_ID"], season=season).info()
            playoffs_tm = team.TeamGameLogs(tm["TEAM_ID"], season=season, season_type=constants.SeasonType.Playoffs).info()
            games = normal_tm.append(playoffs_tm)
            for idx,log in games.iterrows():
                try:
                    session.add(TeamLogs(**log))
                    session.commit()
                    created = created + 1
                except _mysql_exceptions.IntegrityError:
                    print("Integrity error: %s" % e )
                    session.rollback()
                    pass
                except Exception as e:
                    print(e)
                    errors.append(e)
                    session.rollback()

    print("Created: %d, Errored: %d" % (created, len(errors)))
    if len(errors) > 0:
        print(errors[0])

def build_postseason_game_stats(seasons, id_filter=0):
    session = get_session()
    failed = []
    good = 0
    for season in seasons:
        from nba_py import game
        # games = utils.get_all_games(season,beforeToday=True,includeToday=False)
        games = utils.get_playoff_games(season)
        for idx, grow in games[games["id"]>=id_filter].iterrows():
            print("Game: %s" % grow["id"])
            game_id = str(grow["id"]).zfill(10)
            boxscore = game.Boxscore(game_id,season_type=SeasonType.Playoffs).player_stats()
            advboxscore = game.BoxscoreAdvanced(game_id,season_type=SeasonType.Playoffs).sql_players_advanced()
            fourfactors = game.BoxscoreFourFactors(game_id,season_type=SeasonType.Playoffs).sql_players_four_factors()
            boxmisc = game.BoxscoreMisc(game_id,season_type=SeasonType.Playoffs).sql_players_misc()
            for idx, row in boxscore.iterrows():
                try:
                    box = Boxscore(**row)
                    adv = BoxscoreAdvanced(**advboxscore.iloc[idx])
                    ff = BoxscoreFourFactors(**fourfactors.iloc[idx])
                    misc = BoxscoreMisc(**boxmisc.iloc[idx])
                    session.add(box)
                    session.add(adv)
                    session.add(ff)
                    session.add(misc)
                    session.commit()
                    good+=1
                except DataError as e:
                    print("Data error: %s " %e)
                    failed.append(row)
                    session.rollback()
                except Exception as e:
                    # print("Failed creating salary:%s: %s - %s" %(item["GAME_DATE"], item["player_name"], item["salary"]))
                    print("Error: %s" % e)
                    failed.append(row)
                    session.rollback()
    print("Done.")


if __name__ == "__main__":
    import datetime
    import argparse


    print("Starting DatabaseBuild")

    # https://data.nba.com/data/10s/v2015/json/mobile_teams/nba/2017/league/00_full_schedule_week.json
    # seasons = ["2016-17", "2017-18"]
    seasons = ["2016-17","2017-18"]

    parser = argparse.ArgumentParser()
    parser.add_argument("--date", help="whats the date or * for all")
    parser.add_argument("--last", help="last x games")

    args = parser.parse_args()

    # create_seasons_table(seasons)
    # create_game_table(seasons)
    # create_players_table(seasons)
    # create_player_logs(seasons)
    # build_salary()
    # create_vegas_table()
    # create_game_table()
    # create_all_salaries()
    build_game_stats(seasons,0,int(args.last))
    # build_team_stats(seasons)
    #
    # kk = player.PlayerLastNGamesSplits(team_id=1610612742)
    # kkk = kk.last10()
    # kkk = kk.last15()
    # kkk = kk.last20()
    # create_game_table_2(seasons) # Playoffs
    # create_player_logs(seasons)
