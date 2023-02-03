
import json
import scrapy
from scrapy.crawler import CrawlerProcess,CrawlerRunner
from urllib.parse import urljoin
import re
import sys
sys.path.append(r'C:\Users\prati\Documents\Projects\QClisting')
from AmazonSearchProductSpider.items import AmazonsearchproductspiderItem
import pandas as pd
from loguru import  logger

class AmazonSearchProductSpider(scrapy.Spider):
    name = "amazon_search_product"
    # custom_settings = {
    #     'FEEDS': { 'C:/Users/prati/Documents/Projects/QClisting/DataStore/items.csv': { 'format': 'csv',}}
    #     }
    def start_requests(self):
        keyword_list = [pd.read_csv(r'C:\Users\prati\Documents\Projects\LisitingQC\DataStore\keyword_list.csv')['keyword_list'][0]]
        logger.info('The Search Keywords are {}'.format(keyword_list))
        for keyword in keyword_list:
            amazon_search_url = f'https://www.amazon.in/s?k={keyword}&page=1'
            yield scrapy.Request(url=amazon_search_url, callback=self.discover_product_urls, meta={'keyword': keyword, 'page': 1})

    def discover_product_urls(self, response):
        page = response.meta['page']
        keyword = response.meta['keyword'] 

        ## Discover Product URLs
        search_products = response.css("div.s-result-item[data-component-type=s-search-result]")
        for product in search_products[:10]:
            relative_url = product.css("h2>a::attr(href)").get()
            product_url = urljoin('https://www.amazon.in/', relative_url).split("?")[0]
            yield scrapy.Request(url=product_url, callback=self.parse_product_data, meta={'keyword': keyword, 'page': page})
            
        ## Get All Pages
        if page == 1:
            available_pages = response.xpath(
                '//a[has-class("s-pagination-item")][not(has-class("s-pagination-separator"))]/text()'
            ).getall()

            # for page_num in available_pages:
            #   amazon_search_url = f'https://www.amazon.com/s?k={keyword}&page={page_num}'
            #    yield scrapy.Request(url=amazon_search_url, callback=self.discover_product_urls, meta={'keyword': keyword, 'page': page_num})


    def parse_product_data(self, response):
        items= AmazonsearchproductspiderItem()
        #Link = response.css('.a-text-normal').css('a::attr(href)').extract()
        def media_link_cls(img_links):
            images,gif,vid=[],[],[]
            for a in img_links:
                string =a.replace(a.split(".")[-2],"")
                clean_link = string[:-4] + string[-3:]
                ext =clean_link.split('.')[-1]
                if ext in ["jpg", "jpeg", "png","bmp", "tif", "tiff", "svg"]:
                    images.append(clean_link)
                elif ext in ["gif"]:
                    gif.append(clean_link)
                elif ext in ["mp4", "mkv", "flv", "avi", "mov", "wmv", "mpeg", "mpg", "webm"]:
                    vid.append(clean_link)
            return images ,vid 
                

            return 
        image_data = json.loads(re.findall(r"colorImages':.*'initial':\s*(\[.+?\])},\n", response.text)[0])
        variant_data = re.findall(r'dimensionValuesDisplayData"\s*:\s* ({.+?}),\n', response.text)
        feature_bullets = [bullet.strip() for bullet in response.css("#feature-bullets li ::text").getall()]
        price = response.css('.a-price-whole::text').get("")
        img_links =response.css("#altImages img::attr(src)").getall()
        def get_prod_details(col):
            try:
                res =response.css(f"#detailBullets_feature_div li:contains('{col}')").css("::text").extract()[-2]
                return res
            except:
                print(f"[INFO] :{col} NOT FOUND")
                return None 
        def get_prod_specs(col):
            try:
                res= response.css(f"#technicalSpecifications_section_1 tr th:contains('{col}') + td::text").getall()[0]
                return res
            except:
                print(f"[INFO] :{col} NOT FOUND")
                return None 
        def get_height():
            try:
                if response.css(f"#technicalSpecifications_section_1 tr th:contains('Item Height') + td::text").getall()[0]:
                    res = response.css(f"#technicalSpecifications_section_1 tr th:contains('Item Height') + td::text").getall()[0]
                    return res.strip().split(" ")[0],res.strip().split(" ")[1]
                elif response.css(f"#detailBullets_feature_div li:contains('Item Dimensions LxWxH')").css("::text").extract():
                    res = response.css(f"#detailBullets_feature_div li:contains('Item Dimensions LxWxH')").css("::text").extract()[-2]
                    return res.strip().split("x")[2],res.strip().split("x")[2].strip().split(" ")[1]

            except:
                print(f"[INFO] :Item Height NOT FOUND")
                return None ,None 
        def get_width():
            try:
                res= response.css(f"#technicalSpecifications_section_1 tr th:contains('Item Width') + td::text").getall()[0]
                return res.strip().split(" ")[0],res.strip().split(" ")[1]
            except:
                print(f"[INFO] :Item Width NOT FOUND")
                return None ,None 
        def get_length():
            try:
                res= response.css(f"#technicalSpecifications_section_1 tr th:contains('Item Length') + td::text").getall()[0]
                return res.strip().split(" ")[0],res.strip().split(" ")[1]
            except:
                print(f"[INFO] :Item Length NOT FOUND")
                return None ,None 

        #Country of Origin
        items["product_url"]= response.request.url
        items['product_asin']=str(response.request.url).split('/')[-1]
        items['product_brand']=get_prod_specs('Brand')
        items["product_title"]= response.css("#productTitle::text").get("").strip()
        items["product_price"]= price
        items["product_stars"]= str(response.css("i[data-hook=average-star-rating] ::text").get("").strip()).split(" ")[0]
        items['product_images'],items['product_videos'] = media_link_cls(img_links)
        items["product_bullets"]= feature_bullets
        items["product_rating_count"] = response.css("div[data-hook=total-review-count] ::text").get("").strip()
        items["country_of_origin"] = get_prod_details("Country of Origin")
        items['product_weight'] = get_prod_details("Item Weight")
        items['product_material']  = get_prod_specs("Material")
        items['product_category'] =[i.strip() for i in response.css(f"#wayfinding-breadcrumbs_feature_div li span a").css("::text").getall()]
        items['item_height'],items['item_height_unit'] = get_height()
        items['item_length'],items['item_length_unit'] = get_length()
        items['item_width'],items['item_width_unit'] = get_width()
        items['aplus'] = response.css("#aplus img::attr(src)").getall()
        items['description'] = response.css("#productDescription span::text").getall()
        

        yield items

# if __name__=='__main__':
#     import subprocess
#     import os
#     os.chdir(r'C:\Users\prati\Documents\Projects\QClisting\AmazonSearchProductSpider\AmazonSearchProductSpider')
#     subprocess.call('scrapy crawl amazon_search_product -o items.csv')
    # cmd ='scrapy crawl amazon_search_product -o emails.json'
    # os.system(cmd)

# def start_crawling():
if __name__=='__main__':
    process = CrawlerProcess(settings={
    "FEEDS": {
        "DataStore/Scrapy_Res.csv": {"format": "csv","overwrite":True},
    }
    })
    #,"overwrite":True
    process.crawl(AmazonSearchProductSpider)
    process.start()
