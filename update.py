# -*- coding: utf-8 -*-

import scrapy
import time

from datetime import date
from twisted.internet import reactor
from scrapy.crawler import CrawlerProcess
from ReferenceSpider import ReferenceSpider as rs
from ReferenceSpider import InjurySpider
from ReferenceSpider import NBATargets as targets
from ReferenceSpider import GoldStats

'''
process = CrawlerProcess({
    'USER_AGENT': 'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1)',
    'FEED_FORMAT': 'json',
    'FEED_URI': 'data/teams/'+str(date.today())+'.json'
})

process.crawl(rs)
process.start()

'''
'''
injuryProcess = CrawlerProcess({
    'USER_AGENT': 'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1)',
    'FEED_FORMAT': 'json',
    'FEED_URI': 'data/injuries/'+str(date.today())+'.json'
})

injuryProcess.crawl(InjurySpider)
injuryProcess.start()
'''

targetsProcess = CrawlerProcess({
    'USER_AGENT': 'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1)',
    'FEED_FORMAT': 'json',
    'FEED_URI': 'data/targets/'+str(date.today())+'.json'
})

targetsProcess.crawl(targets)
targetsProcess.start()

'''
targetsProcess = CrawlerProcess({
    'USER_AGENT': 'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1)',
    'FEED_FORMAT': 'json',
    'FEED_URI': 'data/goldstats/'+str(date.today())+'.json'
})

targetsProcess.crawl(GoldStats)
targetsProcess.start()
'''

print("Done")