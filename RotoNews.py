news_link="https://stats-prod.nba.com/wp-json/statscms/v1/rotowire/player/"
import json
import urllib.request
from datetime import date

from mysql import *

injuries = None

import utils

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
    news = []
    for idx,update in recent_news.iterrows():
           try:
               pn = PlayerNews(**update)
               if pn.PlayerID == "":
                   find = utils.get_player(firstName = pn.FirstName,lastName = pn.LastName)
                   if find is not None:
                       pn.PlayerID = find.PERSON_ID

               session.add(pn)
               session.commit()
               news.append(pn)
           except Exception as e:
               session.rollback()
               print(e)

    print("New: %d" % (len(news)))
    print(news)

session.close()