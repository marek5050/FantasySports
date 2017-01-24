import glob
import pandas as pd

path = r'data/output/'  # use your path
allFiles = glob.glob(path + "/2*.csv")
dfTemp = pd.DataFrame()
features = ["Name", "Final", "AvgPointsPerGame", "O/U", "odds"]

for file_ in allFiles:
    try:
        df1 = pd.read_csv(file_, index_col=None, header=0)
        dfTemp = pd.concat([dfTemp, df1[features]])
    except:
        pass

df = dfTemp[features]
df.loc[:, ("Name", "Final")]