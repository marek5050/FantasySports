from mysql import *

from nba_py import player
from nba_py.player import get_player

session = get_session()

pl = player.PlayerList().info()
for idx, row1 in pl.iterrows():
    pid = row1["PERSON_ID"]
    log = player.PlayerGameLogs(pid).info()
    session.add(Player(**row1.to_dict()))
    for idx, row2 in log.iterrows():
        k = PlayerLog(row2)
        session.add(k)

session.commit()