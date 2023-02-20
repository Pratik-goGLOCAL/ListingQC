import json
import scrapy
from urllib.parse import urljoin
import re
from ..items import AmazonsearchproductspiderItem
import random
from random_user_agent.params import SoftwareName, OperatingSystem
from random_user_agent.user_agent import UserAgent
from scrapy.utils.response import open_in_browser
import numpy as np
import subprocess
from scrapy.utils.project import get_project_settings
import pandas as pd
from loguru import logger
from fake_headers import Headers
import pickle

def get_useragent():
    software_names = [SoftwareName.FIREFOX.value]
    operating_systems = [OperatingSystem.WINDOWS.value]
    user_agent_rotator = UserAgent(software_names=software_names, operating_systems=operating_systems)
    return user_agent_rotator.get_random_user_agent()

class AmazonSearchProductSpider(scrapy.Spider):
    name = "amazon_search_product"
    def start_requests(self):
        self.count = 1
        referer = ['https://www.amazon.in/','https://www.google.com/'] 
        headers_list =[ {
                     #'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/109.0',
                     'User-Agent':str(get_useragent()),
                     'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
                     'Accept-Language': 'en-US,en;q=0.5',
                     # 'Accept-Encoding': 'gzip, deflate, br',
                     'Referer':str(random.choice(referer)),
                     'Connection': 'keep-alive',
                     # 'Cookie': 'csm-hit=tb:s-CVCTDANP0CKXCSY9NDXE^|1676547049593&t:1676547053266&adb:adblk_no; session-id=262-2212382-0804152; session-id-time=2082787201l; i18n-prefs=INR; ubid-acbin=261-4314748-8549618; session-token=k4trh6fRrQZghhoHckc0RTdcLzlQM+l2ILP8166Lb5Baq0XNwl6SkocgFcAxJ4+L3PPs0x6ph6/GeazIfcLdEovbwg+xS73feZ4SAISjWD1cp88d1qx6/2IafpbZERh+FWFJEgIbM6G9LXEbyEmCyW+OILdQSAWbdgKI629fSzpa0+O9lkFZpfRjsTKTnfLBrsmmggwxEyWzQ6lyNHIpmZ38vFP0tOVpcN+G8950wMA=; lc-acbin=en_IN; x-amz-captcha-1=1675593858520175; x-amz-captcha-2=cQ6u/sOJP8l6xoAR904v0w==',
                     'Upgrade-Insecure-Requests': '1',
                     'Sec-Fetch-Dest': 'document',
                     'Sec-Fetch-Mode': 'navigate',
                     'Sec-Fetch-Site': 'same-origin',
                     'Sec-Fetch-User': '?1'
                     # Requests doesn't support trailers
                     # 'TE': 'trailers',
                  } ,
                  Headers(headers=True).generate()
                ]          

        with open('DataStore/keyword_list.pickle', 'rb') as handle:
            keyword_list = pickle.load(handle)
        logger.info('Keyword List before is {}'.format(keyword_list.values()))
        logger.info('Keyword List contains "," {}'.format(',' in list(keyword_list.values())[0]))
        if ',' in list(keyword_list.values())[0]:
            logger.info(keyword_list.values())
            search_text =  [x.strip() for x in list(keyword_list.values())[0].split(',')]
        else:
            logger.info(list(keyword_list.values()))
            search_text = list(keyword_list.values())
        if 'ASIN' in keyword_list.keys():
            for asin in search_text:
                amazon_search_url = f'https://www.amazon.in/dp/'+str(asin)
                yield scrapy.Request(url=amazon_search_url, 
                                    callback=self.parse_product_data,
                                    headers=random.choice(headers_list))
        else:
            for keyword in search_text:
                logger.info('Keyword is {}'.format(keyword))
                amazon_search_url = f'https://www.amazon.in/s?k={keyword}&page=1'
                yield scrapy.Request(url=amazon_search_url, 
                                    callback=self.discover_product_urls, 
                                    meta={'keyword': keyword, 'page': 1,},
                                    headers=random.choice(headers_list))

    def discover_product_urls(self, response):
        page = response.meta['page']
        keyword = response.meta['keyword'] 

        ## Discover Product URLs
        #search_products = response.css("div.s-result-item[data-component-type=s-search-result]")
        #
        #for product in search_products[:5]:
        #    relative_url = product.css("h2>a::attr(href)").get()
        #    print("relative_url :",relative_url)
        #    product_url = urljoin('https://www.amazon.in/', relative_url)#.split("?")[0]
        #    print("product_url : ",product_url)
        #    yield scrapy.Request(url=product_url, callback=self.parse_product_data, meta={'keyword': keyword, 'page': page})
            
        all_asins =[i for i in response.xpath('//*[@data-asin]').xpath('@data-asin').extract() if i!='']

        for asin in all_asins:
             product_url = f'https://www.amazon.in/dp/{asin}'#.split("?")[0]
             print("product_url : ",product_url)
             yield scrapy.Request(url=product_url, callback=self.parse_product_data, meta={'keyword': keyword, 'page': page})
        ## Get All Pages
        if page == 1:
            total_pages =int(response.css(".s-pagination-item.s-pagination-disabled::text").getall()[-1])
            available_pages = [pg for pg in range(2,total_pages+1)]
            print(available_pages)
            #available_pages = response.xpath(
            #).getall()
            print("tp_:",available_pages)
#
               #print(f"$$$$$==={page_num}===$$$$$")
            for page_num in available_pages:
                amazon_search_url = f'https://www.amazon.in/s?k={keyword}&page={page_num}'
                yield scrapy.Request(url=amazon_search_url, callback=self.discover_product_urls, meta={'keyword': keyword, 'page': page_num})


    def parse_product_data(self, response):
        print(10*"==")
        print(f"Parsing product {self.count}")
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
                
        #image_data = json.loads(re.findall(r"colorImages':.*'initial':\s*(\[.+?\])},\n", response.text)[0])
        #variant_data = re.findall(r'dimensionValuesDisplayData"\s*:\s* ({.+?}),\n', response.text)
        
        feature_bullets = [bullet+'\n' for bullet in response.css("#feature-bullets li ::text").getall()]
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

        # BASIC
        items["url"]= response.request.url
        items['ASIN']=str(response.request.url).split('/')[-1]
        items["title"]= response.css("#productTitle::text").get("").strip()
        items["ratings"]= str(response.css("i[data-hook=average-star-rating] ::text").get("").strip()).split(" ")[0]
        items['image_links'],items['video_links'] = media_link_cls(img_links)
        items["bullets"]= feature_bullets
        items["ratings_count"] = response.css("div[data-hook=total-review-count] ::text").get("").strip()
        items['product_path'] =[i.strip() for i in response.css(f"#wayfinding-breadcrumbs_feature_div li span a").css("::text").getall()]
        items["price"]= response.css("#corePriceDisplay_desktop_feature_div .a-price-whole::text").get()
        items['MRP'] = response.css('#corePriceDisplay_desktop_feature_div .a-size-small .a-offscreen::text').get("")[1:]
        items['discount'] = response.css('#corePriceDisplay_desktop_feature_div div span::text').get("")[1:]
     
        # GET DIMENSIONS
        items['item_height'],items['item_height_unit'] = get_height()
        items['item_length'],items['item_length_unit'] = get_length()
        items['item_width'],items['item_width_unit'] = get_width()

        # A+ AND DESCRIPTION
        items['aplus_images'] = response.css("#aplus img::attr(src)").getall()
        items['aplus_text'] = ''.join([i.replace("\n"," ").strip() for i in response.css('#aplus p::text').getall()])
        items['description'] = response.css("#productDescription span::text").getall()

        # PROD SPECS SECTION        
        items['metal']  = get_prod_specs("Metal")
        items['collection']  = get_prod_specs("Collection")
        items['stone']  = get_prod_specs("Stone")
        items['packaging']  = get_prod_specs("Packaging")
        items['warranty_type']  = get_prod_specs("Warranty Type")

        #items['stone']  = get_prod_specs("Stone")
        items['model_number']  = get_prod_specs("Model Number")
        items['brand']=get_prod_specs('Brand')
        items['material']  = get_prod_specs("Material")

        # PROD DETAILS SECTION        
        items["country_of_origin"] = get_prod_details("Country of Origin")
        items['weight'] = get_prod_details("Item Weight")
        items['importer']  = get_prod_details("Importer")
        items['packer'] = get_prod_details("Packer")
        items['department'] = get_prod_details("Department")
        items['date_first_available'] = get_prod_details("Date First Available")
        items['is_discontinued_by_manufacturer'] = get_prod_details("Is Discontinued By Manufacturer")
        items['best_sellers_rank'] = get_prod_details("Best Sellers Rank")
        items['net_quantity'] = get_prod_details("Net Quantity")          

        # OFFERS AND INFO
        items['special_offers']="".join([i.strip()  for i in response.css('#quickPromoBucketContent li span::text').getall()])
        items['important_info'] = " ".join(response.css("#important-information p::text").getall())
        items['type_of_offers'] =response.css(".a-carousel-card h6::text").getall()
        items['offers'] =response.css(".a-carousel-card .a-section.a-spacing-none.offers-items-content span::text").getall()            
        yield items
