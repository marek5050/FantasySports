import glob

from calculate import *

today = str(date.today())
end_date = today


def appendLSTM(_file):
    df = pd.read_csv(_file)
    for x in range(0,11):
        df["Game" + str(x)] = 0

    _date = _file.split("/")[2].split(".csv")[0]
    if "_" in _date:
        _date = _date.split("_")[0]

    for idx,row in df.iterrows():
        player = Player(data = row)
        player.setEndDate(_date)
        df.loc[idx, "penalty"] = 0
        if player is not None and player.team != '' and player.getSeasonStats() is not None:
            games = player.getSeasonStats(endDate=_date)
            if games is not None and len(games) >= 11:
                _vals = games.iloc[:11,:]["DKFPS"].values
                df.iloc[idx,-11:] = _vals

    df.to_csv(_file.replace("final","LSTM"), sep=',', encoding='utf-8', index=False, float_format='%.3f')


if __name__ == "__main__":
    print("Calculating penalties for data")

    # appendLSTM('data/final/2017-02-01.csv')
    # calculatePenalties('data/output/'+today+'.csv')

    path = r'data/final/'  # use your path
    allFiles = glob.glob(path + "/*.csv")
    for _file in allFiles:
        try:
           print("Starting penalties for " + _file)
           appendLSTM(_file)
           print("Finished penalties for " + _file)
        except Exception as e:
              print("Failed to update penalties for: " + _file)
              print("Reason: " + str(e))
              raise
