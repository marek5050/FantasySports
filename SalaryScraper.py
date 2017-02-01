# -*- coding: utf-8 -*-

import scrapy
from datetime import date
from calculate import fixTeam

import datetime

from scrapy.crawler import CrawlerProcess
from scrapy.http import FormRequest, Request
import pandas as pd

now = datetime.datetime.now()

ordinal = lambda n: "%d%s" % (n,"tsnrhtdd"[(n/10%10!=1)*(n%10<4)*n%10::4])

base = datetime.datetime.today()
date_list = [base - datetime.timedelta(days=x) for x in range(0, 90)]
datelist = pd.date_range(pd.datetime.today(), periods=100).tolist()

class SalaryScraper(scrapy.Spider):
    name = "SalaryScraper"
    start_urls = ["https://swishanalytics.com/optimus/nba/daily-fantasy-salary-changes?date="+x.strftime("%Y-%m-%d") for x in date_list]

    def parse(self, response):
        items = []
        df = pd.DataFrame()
        rows = response.css("tr.salary-row")
        for row in rows:
            cols = row.css("td")
            item = PlayerItem()
            item["pos"] = cols[0]
            item["name"]=cols[1]
            item["price"]=cols[2]
            item["change"]=cols[3]
            item["projected"]=cols[4]
            item["avg"]=cols[5]
            item["diff"]=cols[6]
            items.append(item)

        df.to_csv("data/newSalaries/"+response.url.split("=")[1]+'.csv', sep=',', encoding='utf-8', index=False,
                          float_format='%.3f')
        return

if __name__ == "__main__":
    print("Starting Salary extraction.")
    injuryProcess = CrawlerProcess({
        'USER_AGENT': '"Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1)',
        'FEED_FORMAT': 'csv'
    })

    injuryProcess.crawl(SalaryScraper)
    injuryProcess.start()