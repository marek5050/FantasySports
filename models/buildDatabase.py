from mysql import *
from nba_py import player
from sqlalchemy.sql import select


session = get_session()

_players = session.execute(select([Player]).where(Player.TO_YEAR == 2017))
_players = _players.fetchall()
#
for _player in _players:
    print(_player.PERSON_ID)
    for season in ["2015-16","2016-17","2017-18"]:
        print(season)
        try:
           logs = player.PlayerGameLogs(_player.PERSON_ID, season=season).info()
           for item in logs:
               try:
                   session.merge(PlayerLog(**item))
                   session.commit()
               except Exception as e:
                   session.rollback()

        except Exception as e:
            print("failed ")
            print(e)


#     except Exception as e:
#         print(e)
#     session.commit()
#
#
# for _player in _players:
#     print(_player.PERSON_ID)
#     try:
#        logs = player.PlayerGameLogs(_player.PERSON_ID, season="2016-17").info()
#        session.bulk_save_objects([
#                                    PlayerLog(**row1)
#                                    for idx,row1 in logs.iterrows()
#                                  ], return_defaults=True)
#     except Exception as e:
#         print(e)
# session.commit()
#
# for _player in _players:
#     print(_player.PERSON_ID)
#     try:
#        logs = player.PlayerGameLogs(_player.PERSON_ID).info()
#        # for idx,row1 in logs.iterrows():
#        #     instance = get_or_create(session=session,model=PlayerLog, **row1)
#        for item in logs:
#            try:
#                session.merge(PlayerLog(**item))
#                session.commit()
#            except Exception as e:
#                session.rollback()
#
#     except Exception as e:
#         pass

#
#
# from mysql import *
#
# from nba_py import player
# from nba_py.player import get_player

# session = get_session()
# pl = player.PlayerList().info()
# # array_of_players = []
# # for idx, row1 in pl.iterrows():
# #     try:
# #         array_of_players.append(Player(**row1.to_dict()))
# #     except Exception as e:
# #         print(e)
#
# session.bulk_save_objects([
#                             PlayerLog(**row1.to_dict())
#                             for idx,row1 in pl.iterrows()
#                           ], return_defaults=True)
#
# session.commit()