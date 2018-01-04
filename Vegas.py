# -*- coding: utf-8 -*-

import datetime
from datetime import date

import scrapy
from scrapy.crawler import CrawlerProcess

import buildDatabase
import utils

now = datetime.datetime.now()

date_list = []

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
                home["team"] = utils.fixTeam((text[2].split(":")[0])[0:3])
                away["team"] = utils.fixTeam((text[3].split(":")[0])[0:3])

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

            away["team"] = utils.fixTeam(cells[0])
            away["odds"] = -1*odds if oddsIdx == 3 else odds
            away["overUnder"] = overUnder
            arr.append([away["team"],away["odds"],away["overUnder"]])
            home["team"] = utils.fixTeam(cells[2])
            home["odds"] = odds if oddsIdx == 3 else -1*odds
            home["overUnder"] = overUnder
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

            away["team"] = utils.fixTeam(cells[0])
            away["odds"] = -1 * odds if oddsIdx == 3 else odds
            away["overUnder"] = overUnder
            arr.append([away["team"], away["odds"], away["overUnder"]])
            home["team"] = utils.fixTeam(cells[2])
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

    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--date", help="whats the date or * for all")
    parser.add_argument("--last", help="last x games")
    args = parser.parse_args()

    date_list = [now.date()]
    date_search = now.date()

    if args.date == "*":
        date_list = utils.get_dates("2017-18")
        date_search = "*"
    elif args.date != "":
        date_list = utils.get_dates("2017-18")
        date_search = args.date

    if args.last != "":
            date_list = utils.get_dates("2017-18", beforeToday=True, includeToday=True)
            date_list = date_list[int(args.last)*-1:]
            date_search = date_list

    VegasInsiderOdds.start_urls = [
        "http://www.vegasinsider.com/nba/scoreboard/scores.cfm/game_date/" + x.strftime("%Y-%m-%d") for x in date_list]
       #"http://www.vegasinsider.com/nba/scoreboard/scores.cfm/game_date/12-21-2017"

    injuryProcess.crawl(VegasInsiderOdds)

    injuryProcess.start()

    df = buildDatabase.build_vegas(date_list)

    buildDatabase.create_vegas_table(df)

    # import urllib
    # import urllib.request, json
    # import unicodedata
    #
    # import json
    #
    #
    # def json_load_byteified(file_handle):
    #     return _byteify(
    #         json.load(file_handle, object_hook=_byteify),
    #         ignore_dicts=True
    #     )
    #
    #
    # def json_loads_byteified(json_text):
    #     return _byteify(
    #         json.loads(json_text, object_hook=_byteify),
    #         ignore_dicts=True
    #     )
    #
    #
    # def _byteify(data, ignore_dicts=False):
    #     # if this is a unicode string, return its string representation
    #     if isinstance(data, unicode):
    #         return data.encode('utf-8')
    #     # if this is a list of values, return list of byteified values
    #     if isinstance(data, list):
    #         return [_byteify(item, ignore_dicts=True) for item in data]
    #     # if this is a dictionary, return dictionary of byteified keys and values
    #     # but only if we haven't already byteified it
    #     if isinstance(data, dict) and not ignore_dicts:
    #         return {
    #             _byteify(key, ignore_dicts=True): _byteify(value, ignore_dicts=True)
    #             for key, value in data.iteritems()
    #         }
    #     # if it's anything else, return it in its original form
    #     return data
    #
    # req = urllib.request.Request(
    #     'http://cdn.espn.com/core/api/v0/nav/index?&device=desktop&country=us&lang=en&region=us&site=espn&edition-host=espn.com&one-site=true&site-type=full')
    # req.add_header('Origin', 'http://www.espn.com')
    # req.add_header('Referer', 'http://www.espn.com/nba/scoreboard/_/date/20171122')
    # req.add_header('Accept', '*/*')
    # req.add_header('Accept-Encoding', 'deflate')
    # req.add_header('Connection', 'keep-alive')
    # req.add_header('User-Agent',
    #                'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.94 Safari/537.36')
    # req.add_header('Accept-Language', 'en-US,en;q=0.9,cs;q=0.8')
    # with urllib.request.urlopen(req) as url:
    #     #    print(url)
    #     #    respp = unicode(url.read(), errors='replace')
    #     #    str_response = .decode('utf-8')
    #     print(url.read().decode())
    #     _recap = json_loads_byteified(url.read())