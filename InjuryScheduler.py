from crontab import CronTab

import pandas as pd
import json

from datetime import datetime
from dateutil import tz

today = datetime.now()

from pytz import reference
localtime = reference.LocalTimezone()

print("Scheduling injury reports for today's games.")

calendar_file = "./GoldenState_2017_calendar.json"

try:
    with open(calendar_file) as json_data:
        calendar = json.load(json_data)
except:
    print("Failed to load calendar file.")
    calendar = []

df = pd.DataFrame.from_dict(calendar["games"])
df['dateTime'] = pd.to_datetime(df['dateTimeUTC'])

games = df[df["complete"]==False]

my_cron = CronTab(user='marek5050')
for idx,current_game in games.iterrows():
    team = 'gsw'
    opp = current_game['opponent']['abbrev']
    home = current_game['home']
    name = opp+"@"+team

    if not home:
        name = team+"@"+opp

    from_zone = tz.tzutc()
    to_zone = tz.tzlocal()

    edt = current_game['dateTime'].replace(tzinfo=from_zone).astimezone(to_zone)
    alert = edt- datetime.timedelta(minutes=15)

    job = my_cron.new(command='cd /Users/marek5050/machinelearning/NBA; python ./GameInjurySpider.py '+team+" " + opp,comment=name)
    job.month.on(alert.month)
    job.day.on(alert.day)
    job.hour.on(alert.hour)
    job.minute.on(alert.minute)

my_cron.write()

for job in my_cron:
    print(job)
