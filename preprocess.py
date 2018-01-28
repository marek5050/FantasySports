import pandas as pd

players = pd.read_csv("/Users/marek5050/machinelearning/NBA/180106Players.csv")
teams = pd.read_csv("/Users/marek5050/machinelearning/NBA/180106Teams.csv")
print(players.columns)
gr = None

all_columns= ['id', 'fantasy_pts', 'avg_pts', 'fpts_diff', 'Name', 'date',
       'salary', 'salary_change', 'salary_diff', 'salary_diff_percentage',
       'GAME_ID', 'GAME_DATE', 'Player_ID', 'odds', 'ou', 'Position', 'pos1',
       'pos2', 'Name', 'Player_ID.1', 'id.1', 'SEASON_ID', 'Player_ID.2',
       'Game_ID', 'GAME_DATE.1', 'MATCHUP', 'WL', 'MIN', 'FGM', 'FGA',
       'FG_PCT', 'FG3M', 'FG3A', 'FG3_PCT', 'FTM', 'FTA', 'FT_PCT', 'OREB',
       'DREB', 'REB', 'AST', 'STL', 'BLK', 'TOV', 'PF', 'PTS', 'PLUS_MINUS',
       'VIDEO_AVAILABLE', 'DKFPS', 'TEAM']

features = ['id', 'fantasy_pts', 'avg_pts', 'fpts_diff', 'Name', 'date',
       'salary', 'salary_change', 'salary_diff', 'salary_diff_percentage']

numeric = ['MIN', 'FGM', 'FGA','FG_PCT', 'FG3M', 'FG3A', 'FG3_PCT', 'FTM', 'FTA', 'FT_PCT', 'OREB',
       'DREB', 'REB', 'AST', 'STL', 'BLK', 'TOV', 'PF', 'PTS', 'PLUS_MINUS', 'DKFPS','ou', 'odds']

rolling_avg_cols=["MIN","salary","DKFPS","NET_RATING","DEF_RATING","OFF_RATING"]
rolling_mean_cols=["MINavg","salaryavg","DKFPSavg","NET_RATINGavg","DEF_RATINGavg","OFF_RATINGavg"]
rolling_std_cols=["MINstd","salarystd","DKFPSstd","NET_RATINGstd","DEF_RATINGstd","OFF_RATINGstd"]
shifted_cols = ["shiftedDKFPS","shiftedsalaryavg","shiftedsalarystd",
                "shiftedDEF_RAT","shiftedOFF_RAT","shiftedNET_RAT",
                "shiftedDKFPSavg", "shiftedMIN","shiftedMINavg", "shiftedMINstd",
                "shiftedDKFPSstd","shiftedOFF_RATINGavg","shiftedDEF_RATINGavg","shiftedNET_RATINGavg"]
save_csv = ["Name","TEAM","ou","odds","Position","GAME_DATE","diff_dates","Game_ID",
            "Home","OPP","PACE","AST","TO","ORR","DRR","REBR","EFF FG%","TS%",
            "OFF EFF","DEF EFF","DKFPS","salary"]+shifted_cols
           # +rolling_avg_cols++rolling_mean_cols+rolling_std_cols
players[rolling_avg_cols]=players[rolling_avg_cols].fillna(0)
# def avg_vs_team(x):
#     return x[0:-1].mean()
# averaged_team = players.groupby(["Player_ID","TEAM"])["DKFPS"].apply(avg_vs_team)
# players["oppavg"] = 0

# for rowidx, row in players.iterrows():
#     pastData = players[0:rowidx][(players[0:rowidx]["OPP"] == row["OPP"]) & (players[0:rowidx]["Name"]==row["Name"])]
#     players[rowidx,"oppavg"]=pastData["DKFPS"].mean()
#
# #players[0:1000][(players[0:1000]["OPP"]==row["OPP"]) & (players[0:1000]["Name"]==row["Name"])]
# print("Blah")
#
#
# text_features = ["Player_ID","GAME_ID"]
# players[text_features] = players[text_features].astype('str')
# ## Single player
# gr = players.loc[players["Player_ID"]==2544,numeric].rolling(window=10).mean()
# tr = players.loc[players["Player_ID"]==2544,numeric]
#
# gr[["GAME_ID","Player_ID"]]=players.loc[players["Player_ID"]==2544,["GAME_ID","Player_ID"]]
# gr2= gr.dropna(axis=0, how='any')

# tr = players[["GAME_DATE","GAME_ID"]]+gr
# print("hmmm")

## Multiple players.
#kk = players.groupby(["Player_ID"]).rolling(window=10).mean().describe()

# allrolling= gr_mean
# allrolling[rolling_std_cols] = gr_std
# # allrolling[["GAME_DATE","GAME_ID","Player_ID"]]
# len(gr_mean)
# grm2 = gr_mean.dropna(axis=0, how='any')
# len(grm2)
# groupedplayers = players.groupby(["Player_ID"])


# This is like an identity will just give us a grouped dataframe
c = players.groupby(["Player_ID"]).rolling(window=1).sum()
# Calculate the rolling mean and std
gr_mean = players.groupby(["Player_ID"])[rolling_avg_cols].rolling(window=10).mean()
gr_std = players.groupby(["Player_ID"])[rolling_avg_cols].rolling(window=10).std()
# Assign them
c[rolling_mean_cols]= gr_mean
c[rolling_std_cols] = gr_std

#shift by 1
c[["shiftedPACE","shiftedAST","shiftedTO","shiftedORR","shiftedDRR","shiftedREBR","shiftedEFF FG%","shiftedTS%","shiftedOFF EFF","shiftedDEF EFF"]] \
       = c.groupby(["Player_ID"])[["PACE","AST","TO","ORR","DRR","REBR","EFF FG%","TS%","OFF EFF","DEF EFF"]].shift(1)

# rolling_mean_cols=["MINavg","salaryavg","DKFPSavg","NET_RATINGavg","DEF_RATINGavg","OFF_RATINGavg"]

c["shiftedNET_RAT"] = c.groupby(["Player_ID"])["NET_RATING"].shift(1)
c["shiftedOFF_RAT"] = c.groupby(["Player_ID"])["OFF_RATING"].shift(1)
c["shiftedDEF_RAT"] = c.groupby(["Player_ID"])["DEF_RATING"].shift(1)
c["shiftedDKFPS"] = c.groupby(["Player_ID"])["DKFPS"].shift(1)
c["shiftedMIN"] = c.groupby(["Player_ID"])["MIN"].shift(1)
# c[["shiftedMINavg","shiftedsalaryavg","shiftedMINstd","shiftedsalarystd","shiftedDKFPSstd"]] \
#     = c.groupby(["Player_ID"])[["MINavg","salaryavg","DKFPSavg","MINstd","salarystd","DKFPSstd"]].shift(1)
c["shiftedMINavg"] =  c.groupby(["Player_ID"])["MINavg"].shift(1)
c["shiftedsalaryavg"] = c.groupby(["Player_ID"])["salaryavg"].shift(1)
c["shiftedDKFPSavg"] = c.groupby(["Player_ID"])["DKFPSavg"].shift(1)
c["shiftedMINstd"] = c.groupby(["Player_ID"])["MINstd"].shift(1)
c["shiftedsalarystd"] = c.groupby(["Player_ID"])["salarystd"].shift(1)
c["shiftedDKFPSstd"] = c.groupby(["Player_ID"])["DKFPSstd"].shift(1)
c[["shiftedOFF_RATINGavg","shiftedDEF_RATINGavg","shiftedNET_RATINGavg"]]=c.groupby(["Player_ID"])[["OFF_RATINGavg","DEF_RATINGavg","NET_RATINGavg"]].shift(1)
len(c)

c["WLStreak"] = "-"

for id, player_rows in c.groupby(["Player_ID"]):
    last = None
    count = 0
    for idx in reversed(range(len(player_rows))):
        if last is None:
            last = player_rows.iloc[idx]["WL"]

        if player_rows.iloc[idx]["WL"] == last:
            count = count + 1
        else:
            break
    print("Streak: %d" % count)

# Days since rest
c["GAME_DATE"] = pd.to_datetime(c["GAME_DATE"])
grp2 = c.groupby(["Player_ID"])["GAME_DATE"]

c["diff_dates"] = grp2.diff()
print(c[["Player_ID","diff_dates","GAME_DATE"]].head())

kk = c.dropna()
# for rowidx, row in c[1:].iterrows():
#     pastData = c[rowidx-1].dt - row.dt
#     players[rowidx,"oppavg"]=pastData["DKFPS"].mean()





predict = c[c["GAME_DATE"] == "2017-12-30"]
train = c[c["GAME_DATE"] != "2017-12-30"]

predict[save_csv].to_csv("171230Predict.csv")
train[save_csv].to_csv("171230Train.csv")

len(c)
c[save_csv].to_csv("171230Shifted.csv")
