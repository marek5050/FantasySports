# -*- coding: utf-8 -*-

import datetime

import pandas as pd
import scrapy
from scrapy.crawler import CrawlerProcess

import utils

now = datetime.datetime.now()

ordinal = lambda n: "%d%s" % (n,"tsnrhtdd"[(n/10%10!=1)*(n%10<4)*n%10::4])

base = datetime.datetime.today()
date_list = [base - datetime.timedelta(days=x) for x in range(0, 2)]

import re
import json
import buildDatabase

#  Only to 2016-10-25
class SalaryScraper(scrapy.Spider):
    name = "SalaryScraper"

    def parse(self, response):
        items = []
        text =response.body.decode(response.encoding)

        # find = re.search('\[\{.+\}\]', text, re.MULTILINE)
        finder = re.compile('\[\{.+\}\]') ## Grab the DK, FD, and YAH salaries
        _find1 = finder.search(text)
        now = response.url.split("=")[1]
        if _find1 :
            dic = json.loads(_find1.group())
            df = pd.DataFrame(dic)
            df.to_csv("data/old_salaries/dk_"+now+'.csv', sep=',', encoding='utf-8', index=False,
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

    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--date", help="whats the date or * for all")
    args = parser.parse_args()

    date_list = [now.date()]
    date_search = now.date()

    if args.date == "*":
        date_list = utils.get_dates("2017-18")
        date_search = "*"

    start_urls = [
        "https://swishanalytics.com/optimus/nba/daily-fantasy-salary-changes?date=" + x.strftime("%Y-%m-%d") for x
        in date_list]

    SalaryScraper.start_urls = start_urls

    injuryProcess.crawl(SalaryScraper)
    injuryProcess.start()

    for date in date_list:
        # print(date)
        df = buildDatabase.build_salary(date_search)
        if len(df)>0:
            buildDatabase.create_salary_table(df)
