# import numpy as np
# import pandas as pd
# from sklearn.preprocessing import StandardScaler
# from time import time
#
# np.random.seed(1337)
#
#
# from datetime import date
#
# today = str(date.today())
# end_date = today
#
# import glob
#
# path = r'data/output/'  # use your path
# allFiles = glob.glob(path + "/2*.csv")
#
# dftrain = pd.DataFrame()
#
# for _file in allFiles:
#         try:
#             dftrain = pd.concat([dftrain,pd.read_csv(_file,header=0)])
#         except:
#             pass
#
# dvp = pd.read_csv('data/Defense/'+today+'.csv')
# dvp = dvp.set_index("team")
# dvp.sort_values(by="all",inplace=True)
#
# for idx,row in dftrain.iterrows():
#     try:
#         if "opponent" in row and isinstance(row["opponent"], str):
#             positions = row["Position"].lower().split("/")
#             _dvp = dvp.loc[:, positions].rank().loc[row["opponent"].upper(), positions].mean()
#         elif "GameInfo" in row:
#             positions = row["Position"].lower().split("/")
#             atHome = row["atHome"]
#             game = row["GameInfo"].split(" ")[0]
#
#             home, away = game.upper().split("@")
#
#             opponent = away if atHome else home
#
#             _dvp = dvp.loc[:, positions].rank().loc[opponent, positions].mean()
#
#         dftrain.loc[idx, "dvp"] = _dvp
#     except Exception as e:
#         print(e)
#         print("Somethng broke")
#         pass
#
# #dftrain = pd.read_csv('data/extras/train.csv', header=0)
# dftest = pd.read_csv('data/output/3017-01-24.csv', header=0)
# dfPredict1 = pd.read_csv('data/output/3017-01-24.csv', header=0)

from nba_py import game
from nba_py import team
from nba_py.player import get_player

pid = get_player("LeBron","James")
#sc = Scoreboard(month=1, year=2017, day=27)
#sc.available()
#sc.line_score()

g = game.BoxscoreSummary("0021600696")
g.inactive_players()

k = team.TeamGameLogs(team.TEAMS["CHA"]["id"])
k = team.TeamSummary(team.TEAMS["CHA"]["id"])
k.info()
#team(team.TEAMS["CHA"]["id"])
