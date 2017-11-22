news_link="https://stats-prod.nba.com/wp-json/statscms/v1/rotowire/player/"
import urllib.request, json
from datetime import date
from models.mysql import *
import pandas as pd
injuries = None

session = get_session()

with urllib.request.urlopen(news_link) as url:
    data = json.loads(url.read().decode())
    injuries = pd.DataFrame(data["ListItems"])
    today = str(date.today())
    injuries.to_csv("./data/injuries/"+today+".csv")

    recent_news = injuries.groupby("player_code").first()
    # recent_news = recent_news.sort_values(by='lastUpdate', ascending=True)
    # recent_news["Questionable"] = recent_news["Headline"].str.contains("Questionable", case=False)
    # recent_news["Probable"] = recent_news["Headline"].str.contains("Probable", case=False)
    # recent_news["Out"] = recent_news["Injured_Status"].str.contains("Out", case=False)
    # recent_news["GTD"] = recent_news["Injured_Status"].str.contains("GTD", case=False)
    # recent_news["skip"] = recent_news["Out"] | recent_news["Probable"] | recent_news["Questionable"] | recent_news[
    #     "GTD"]

    for idx,update in recent_news.iterrows():
           try:
               session.add(PlayerNews(**update))
               session.commit()
           except Exception as e:
               session.rollback()
