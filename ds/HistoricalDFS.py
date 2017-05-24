# -*- coding: utf-8 -*-

import scrapy
from datetime import date

import datetime

from scrapy.crawler import CrawlerProcess
from scrapy.http import FormRequest, Request

from nba_py import player as players
from nba_py.player import get_player
from bs4 import BeautifulSoup


now = datetime.datetime.now()

ordinal = lambda n: "%d%s" % (n,"tsnrhtdd"[(n/10%10!=1)*(n%10<4)*n%10::4])

class TableItem(scrapy.Item):
    rank = scrapy.Field()
    price= scrapy.Field()
    ratio=scrapy.Field()
    value = scrapy.Field()
    name = scrapy.Field()
    team = scrapy.Field()
    game = scrapy.Field()
    pos = scrapy.Field()
    opp = scrapy.Field()
    min = scrapy.Field()
    pts = scrapy.Field()
    pt3 = scrapy.Field()
    reb = scrapy.Field()
    ast = scrapy.Field()
    stl = scrapy.Field()
    blk = scrapy.Field()
    fg = scrapy.Field()
    fga = scrapy.Field()
    ft = scrapy.Field()
    fta = scrapy.Field()
    to = scrapy.Field()
    pf = scrapy.Field()
    start = scrapy.Field()
    USG = scrapy.Field()
    date = scrapy.Field()


class DefenseVsPosition(scrapy.Spider):
    name = 'HistoricalDFS'

    # start_urls = ['https://basketballmonster.com/dfsdailysummary.aspx?date=2016-10-25',
    #              'https://basketballmonster.com/dfsdailysummary.aspx?date=2016-11-25',
    #              'https://basketballmonster.com/dfsdailysummary.aspx?date=2017-01-02']

    def parse(self, response):

        keys = "rank,price,ratio,value,name,team,game,pos,opp,min,pts,pt3,reb,ast,stl,blk,fg,fga,ft,fta,to,pf,start,USG"
        arr = keys.split(",")
        rows = response.css("table.data-font").css("tr")
        date = response.url.split("=")[1]

        for row in rows:
            soup = BeautifulSoup(row.extract(), 'lxml').find_all("td")
            item = TableItem()
            for i in range(0,len(soup)):
                if i < len(soup):
                    item[arr[i]] = soup[i].get_text().strip()
            item["date"] = date

            yield item

    def start_requests(self):
        import json

        calendar = "data/calendar/full_schedule.json"
        with open(calendar) as json_data:
            d = json.load(json_data)
        dates1 = {}
        months = d["lscd"]
        for month in months:
            games  = month["mscd"]["g"]
            for game in games:
                dates1[game["gdte"]]=1
        import pandas as pd
        from datetime import date

        today = str(date.today())
        dlist = list(dates1.keys())
      #  dates1 = {'DATE':dates1}
        df = pd.DataFrame(dlist, columns=["DATE"])
        df["DATE"] = pd.to_datetime(df["DATE"])
        df.set_index(df["DATE"],inplace=True)
        df = df["2016-11-1":today]
        for date in df.index.tolist():
            yield Request('https://basketballmonster.com/dfsdailysummary.aspx?date='+date._date_repr, self.parse)

        return

if __name__ == "__main__":
    print("Starting HistoricalDFS extraction.")
    injuryProcess = CrawlerProcess({
        'USER_AGENT': 'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1)',
        'FEED_FORMAT': 'csv',
        'FEED_URI': 'data/historicalDFS/' + str(date.today()) + '.csv'
    })

    injuryProcess.crawl(DefenseVsPosition)
    injuryProcess.start()