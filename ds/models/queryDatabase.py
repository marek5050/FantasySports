from mysql import *

from sqlalchemy.sql import select

from nba_py import player
from nba_py.player import get_player
import pandas as pd


session = get_session()

logs = session.execute(select([PlayerLog]).where(PlayerLog.Player_ID=="203518"))
df = pd.DataFrame(data = logs.fetchall(), columns=logs.keys())

print(df.head())