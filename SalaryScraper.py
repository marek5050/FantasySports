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
# date_list = [base - datetime.timedelta(days=x) for x in range(0, 90)]
#date_list = pd.date_range(pd.datetime.today(), periods=1200).tolist()
date_list = [base - datetime.timedelta(days=x) for x in range(0, 2000)]

import collections
import re
import json


#  Only to 2016-10-25
class SalaryScraper(scrapy.Spider):
    name = "SalaryScraper"
    start_urls = ["https://swishanalytics.com/optimus/nba/daily-fantasy-salary-changes?date="+x.strftime("%Y-%m-%d") for x in date_list]

    def parse(self, response):
        items = []
        text =response.body.decode(response.encoding)

        # find = re.search('\[\{.+\}\]', text, re.MULTILINE)
        finder = re.compile('\[\{.+\}\]')
        _find1 = finder.search(text)
        if _find1 :
            dic = json.loads(_find1.group())
            df = pd.DataFrame(dic)
            df.to_csv("data/old_salaries/dk_"+response.url.split("=")[1]+'.csv', sep=',', encoding='utf-8', index=False,
                          float_format='%.3f')
            _find2 = finder.search(text, _find1.end())
            if _find2:
                dic = json.loads(_find2.group())
                df = pd.DataFrame(dic)
                df.to_csv("data/old_salaries/fd_" + response.url.split("=")[1] + '.csv', sep=',', encoding='utf-8',
                          index=False,
                          float_format='%.3f')

                _find3 = finder.search(text, _find2.end())
                if _find3:
                    dic = json.loads(_find3.group())
                    df = pd.DataFrame(dic)
                    df.to_csv("data/old_salaries/yah_" + response.url.split("=")[1] + '.csv', sep=',', encoding='utf-8',
                              index=False,
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