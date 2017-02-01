import json
import pandas as pd
import numpy as np

from datetime import date
from calculate import Player
from calculate import *

today = str(date.today())
end_date = today

def calculatePenalties(_file):
    vegas = pd.read_csv(_file.replace("output","vegas"))
    vegas = vegas.set_index("team")

    df = pd.read_csv(_file)

    _date = _file.split("/")[2].split(".csv")[0]
    if "_" in _date:
        _date = _date.split("_")[0]

    for idx,row in df.iterrows():
        player = Player(data = row)
        player.setEndDate(_date)
        df.loc[idx, "penalty"] = 0
        if player is not None and player.team != '' and player.seasonStats is not None:
            penalty = 0
            if player.injury:
                penalty = 9999.0
            elif player.salary < 4500 and player.dvp <= 5:
                penalty = 9000.0
            elif player.salary < 6500 and player.dvp <= 5:
                penalty = (10 + 10 / row["dvp"])
            elif player.salary > 4500 and player.dvp <= 5:
                penalty = (10 + 10 / row["dvp"])

            overUnder = row["O/U"]
            odds = row["odds"]

            s = ""
            overUnderMean = vegas["overUnder"].mean()
            oddsMean = vegas[(vegas["odds"] >= 0)]["odds"].mean()
            '''
                Bonus to ppl in high scoring games (215)    (220)/(220+205(mean)) (230-215)/(237-215)...
                Blowout definition : 4% = odds/overUnder ratio
                Penalize losing team in blowouts especially bench ...
                Penalize bench in tight games....
            '''
            penalty += 150 * (overUnderMean - overUnder) / overUnderMean
            s += " o/u: " + str((150 * (overUnderMean - overUnder) / overUnderMean))

            # blowout
            if odds / overUnder > 0.3 or odds > oddsMean:
                penalty += 2  # (odds-oddsMean)/oddsMean
            # cheap players on losing team penalty
            # if + and < 4500 -10%
            if player.salary < 4500 and odds > oddsMean:
                penalty += 2
                s += " low player: " + str(10)

            lastGame = player.getLastGame()
            try:
                std = player.seasonStats.loc[:, "DKFPS"].std()
                # if last game sucked
                if len(lastGame["DKFPS"]) > 0 and (lastGame["DKFPS"][0] < (player.fantasyPointAverage - std)):
                    penalty += std
                    s += " bad last game: " + str((std))
            except Exception as e:
                penalty = penalty
                print("Failed to get LastGame")
                print(e)
                pass

            df.loc[idx, "penalty"] = -1*penalty or 0.0

    df.to_csv(_file.replace("output","final"), sep=',', encoding='utf-8', index=False, float_format='%.3f')

import glob

if __name__ == "__main__":
    print("Calculating penalties for data")
    calculatePenalties('data/output/'+today+'.csv')

    # path = r'data/output/'  # use your path
    # allFiles = glob.glob(path + "/*.csv")
    # for _file in allFiles:
    #     try:
    #        print("Starting penalties for " + _file)
    #        calculatePenalties(_file)
    #        print("Finished penalties for " + _file)
    #     except Exception as e:
    #           print("Failed to update penalties for: " + _file)
    #           print("Reason: " + str(e))
    #           raise
