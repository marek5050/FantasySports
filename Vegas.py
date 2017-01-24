# -*- coding: utf-8 -*-

import scrapy
from datetime import date

import datetime

from scrapy.crawler import CrawlerProcess
from scrapy.http import FormRequest, Request

now = datetime.datetime.now()

ordinal = lambda n: "%d%s" % (n,"tsnrhtdd"[(n/10%10!=1)*(n%10<4)*n%10::4])

class VegasItem(scrapy.Item):
    team = scrapy.Field()
    odds = scrapy.Field()
    overUnder = scrapy.Field()

class VegasOdds(scrapy.Spider):
    name = 'VegasOdds'

    start_urls = ['http://www.espn.com/nba/lines']

    def parse(self, response):

        heads = response.css("table.tablehead").css("tr.stathead")
        for match in heads:
            home = VegasItem()
            away = VegasItem()
            items = match.xpath("following-sibling::tr[2]").css("td")
            #items[0] # Name
            #items[1] # Odds + -
            text = items[1].css("::text").extract()
            if "EVEN" in text:
                home["odds"] = 1
                away["odds"] = 1
            elif len(text) == 4:
                home["odds"] = text[0]
                away["odds"] = text[1]
                home["team"] = (text[2].split(":")[0])[0:3].replace("PHX","PHO").replace("WSH","WAS")
                away["team"] = (text[3].split(":")[0])[0:3].replace("PHX","PHO").replace("WSH","WAS")

            text = items[5].css("::text").extract()
            if len(text) == 1:
                home["overUnder"] = text[0]
                away["overUnder"] = text[0]
            yield home
            yield away


import pandas as pd

class VegasInsiderOdds(scrapy.Spider):
    name = "VegasInsiderOdds"
    start_urls = ["http://www.vegasinsider.com/nba/scoreboard/scores.cfm/game_date/01-" + str(x) + "-2017" for x in
     range(1, 15)]
    def parse(self, response):
        arr = []
        gamesPlayed = response.css("td.sportPicksBorder table")
        for game in gamesPlayed:
            rows = game.css("tr.tanBg")
            cells = rows.css("td>b>a::text, td[align='middle']::text").extract()
            home = VegasItem()
            away = VegasItem()

            overUnder = max(cells[1],cells[3])
            odds = min(cells[1],cells[3])
            oddsIdx = cells.index(odds)
            if "PK" in overUnder:
                odds = "1"
                overUnder = odds
            odds = float(odds.replace("\xa0",""))
            overUnder = float(overUnder.replace("\xa0",""))

            away["odds"] = -1*odds if oddsIdx == 3 else odds
            away["team"] = cells[0]
            away["overUnder"] = overUnder
            arr.append(away.values())
            home["odds"] = odds if oddsIdx == 3 else -1*odds
            home["team"] = cells[2]
            home["overUnder"] = overUnder
            arr.append(home.values())

        df = pd.DataFrame(arr)
        df.to_csv("data/vegas/2017-01-" + response.url.split("game_date/")[1].split("-")[1] + '.csv', sep=',', encoding='utf-8', index=False,
                          float_format='%.3f')
        return


if __name__ == "__main__":
    print("Starting DvP extraction.")
    injuryProcess = CrawlerProcess({
        'USER_AGENT': '"Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1)',
        'FEED_FORMAT': 'csv',
        'FEED_URI': 'data/vegas/' + str(date.today()) + '.csv'
    })

    injuryProcess.crawl(VegasInsiderOdds)
    injuryProcess.start()