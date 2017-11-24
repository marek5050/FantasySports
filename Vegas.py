# -*- coding: utf-8 -*-

import datetime
from datetime import date

import scrapy
from scrapy.crawler import CrawlerProcess

import utils
from calculate import fixTeam

now = datetime.datetime.now()

date_list = utils.get_dates("2017-18")

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
            text = items[1].css("::text").extract()
            if "EVEN" in text:
                home["odds"] = 1
                away["odds"] = 1
            elif len(text) == 4:
                home["odds"] = text[0]
                away["odds"] = text[1]
                home["team"] = fixTeam((text[2].split(":")[0])[0:3])
                away["team"] = fixTeam((text[3].split(":")[0])[0:3])

            text = items[5].css("::text").extract()
            if len(text) == 1:
                home["overUnder"] = text[0]
                away["overUnder"] = text[0]
            yield home
            yield away


import pandas as pd


today = str(date.today())

base = datetime.datetime.today()
# date_list = [base - datetime.timedelta(days=x) for x in range(0, 10)]
# date_list = [datetime.datetime.today()]

class VegasInsiderOdds(scrapy.Spider):
    name = "VegasInsiderOdds"
    start_urls = ["http://www.vegasinsider.com/nba/scoreboard/scores.cfm/game_date/"+x.strftime("%Y-%m-%d") for x in date_list]

    def parse(self, response):
        try:
           import os.path
           tod = response.url.split("game_date/")[1]
           _check = "data/vegas/"+tod+'.csv'
           if os.path.isfile(_check):
               return
        except:
            pass

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

            away["team"] = fixTeam(cells[0])
            away["odds"] = -1*odds if oddsIdx == 3 else odds
            away["overUnder"] = overUnder
            arr.append([away["team"],away["odds"],away["overUnder"]])
            home["team"] = fixTeam(cells[2])
            home["odds"] = odds if oddsIdx == 3 else -1*odds
            home["overUnder"] = overUnder
            # yield(home)
            # yield(away)
            arr.append([home["team"], home["odds"], home["overUnder"]])

        df = pd.DataFrame(arr, columns=["team","odds","overUnder"])
        try:
            tod = response.url.split("game_date/")[1]
        except:
            tod = today
        df.to_csv("data/vegas/"+tod+'.csv', sep=',', encoding='utf-8', index=False,
                          float_format='%.3f')
        return


# http://m.espn.com/nba/dailyline?date=20171118&casinoId=25
class ESPNDailyLine(scrapy.Spider):
    name = "ESPNDailyLine"
    start_urls = ["http://m.espn.com/nba/dailyline?date=%s&casinoId=25" % (x.strftime("%Y%m%d")) for x
                  in date_list]

    def parse(self, response):
        try:
            import os.path
            tod = response.url.split("date=")[1]
            _check = "data/vegas2/" + tod + '.csv'
            if os.path.isfile(_check):
                return
        except:
            pass

        arr = []
        gamesPlayed = response.css("td.sportPicksBorder table")
        for game in gamesPlayed:
            rows = game.css("tr.tanBg")
            cells = rows.css("td>b>a::text, td[align='middle']::text").extract()
            home = VegasItem()
            away = VegasItem()

            overUnder = max(cells[1], cells[3])
            odds = min(cells[1], cells[3])
            oddsIdx = cells.index(odds)
            if "PK" in overUnder:
                odds = "1"
                overUnder = odds
            odds = float(odds.replace("\xa0", ""))
            overUnder = float(overUnder.replace("\xa0", ""))

            away["team"] = fixTeam(cells[0])
            away["odds"] = -1 * odds if oddsIdx == 3 else odds
            away["overUnder"] = overUnder
            arr.append([away["team"], away["odds"], away["overUnder"]])
            home["team"] = fixTeam(cells[2])
            home["odds"] = odds if oddsIdx == 3 else -1 * odds
            home["overUnder"] = overUnder
            # yield(home)
            # yield(away)
            arr.append([home["team"], home["odds"], home["overUnder"]])

        df = pd.DataFrame(arr, columns=["team", "odds", "overUnder"])
        try:
            tod = response.url.split("game_date/")[1]
        except:
            tod = today
        df.to_csv("data/vegas2/" + tod + '.csv', sep=',', encoding='utf-8', index=False,
                  float_format='%.3f')
        return


# https://rotogrinders.com/schedules/nba

if __name__ == "__main__":
    print("Starting Vegas extraction.")
    injuryProcess = CrawlerProcess({
        'USER_AGENT': '"Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1)',
        'FEED_FORMAT': 'csv'
    })

    injuryProcess.crawl(VegasInsiderOdds)
    injuryProcess.start()