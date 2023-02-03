import pandas as pd
import json
import scrapy
from scrapy.crawler import CrawlerProcess,CrawlerRunner
from urllib.parse import urljoin
import re
import sys
from AmazonSearchProductSpider.spiders import AmazonSearchProductSpider

def run_spider():
    process = CrawlerProcess(settings={
    "FEEDS": {
        "DataStore/Scrapy_Res.csv": {"format": "csv","overwrite":True},
    }
    })
    #,"overwrite":True
    process.crawl(AmazonSearchProductSpider)
    process.start()
