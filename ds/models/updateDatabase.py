from mysql import *

from nba_py import player
from nba_py.player import get_player

session = get_session()
session.query(PlayerLog).delete()

#pl = player.PlayerList().info()
pl = session.query(Player).all()
for row in pl:
    log = player.PlayerGameLogs(row.PERSON_ID).info()
    for idx, row2 in log.iterrows():
        k  = PlayerLog(row2)
        session.add(k)

session.commit()