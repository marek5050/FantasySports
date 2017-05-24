import json
import pandas as pd
import numpy as np

from datetime import date
import glob

#today = str(date.yesterday())
today = "2017-01-11"

salariescsv = 'data/uploadRosters/'+today+'.csv'
rosterscsv = 'data/generatedRosters/' + today+'.csv'

rosters = pd.read_csv(rosterscsv)
salaries = pd.read_csv(salariescsv, skiprows=7,index_col=False)
salaries = salaries.dropna(axis=1)
playerId = salaries.loc[:,(" Name"," ID","Name + ID")]

rrosters = []
for idx, roster in rosters.iterrows():
    r = []
    for player in roster:

        p = salaries[salaries[" Name"] == player]
        if p.size != 0:
            r.append(p["Name + ID"].values[0])

    rrosters.append(r)

pd.DataFrame(rrosters).to_csv("data/uploadRosters/"+str(date.today())+'upload.csv',header=False, sep=',', encoding='utf-8', index=False, float_format='%.3f')
