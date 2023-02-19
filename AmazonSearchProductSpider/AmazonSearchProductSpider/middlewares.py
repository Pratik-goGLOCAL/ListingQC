# Define here the models for your spider middleware
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/spider-middleware.html

from scrapy import signals
from itemadapter import is_item, ItemAdapter
import logging
from scrapy.downloadermiddlewares.retry import RetryMiddleware
from scrapy.spidermiddlewares.httperror import HttpErrorMiddleware
from random_user_agent.params import SoftwareName, OperatingSystem
from random_user_agent.user_agent import UserAgent
import random
from .settings import PROXIES
import time
import scrapy
from fake_headers import Headers

class MyHttpErrorMiddleware(HttpErrorMiddleware):
    
    def get_useragent(self):
        software_names = [SoftwareName.FIREFOX.value , SoftwareName.CHROME.value]
        operating_systems = [OperatingSystem.WINDOWS.value,OperatingSystem.MAC.value,OperatingSystem.LINUX.value]
        user_agent_rotator = UserAgent(software_names=software_names, operating_systems=operating_systems)
        return user_agent_rotator.get_random_user_agent()

    def process_spider_exception(self, response, exception, spider):
        print("Inside exception ",response.status)
        if response.status==503:
            headers = [{
                         #'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36",
                         #'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/109.0',
                        'User-Agent': str(random.choice(self.get_useragent())),
                        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
                        'Accept-Language': 'en-US,en;q=0.5',
                        # 'Accept-Encoding': 'gzip, deflate, br',
                        'Connection': 'keep-alive',
                        #'Cookie': 'session-id=141-6675835-7022205; session-id-time=2082787201l; i18n-prefs=USD; csm-hit=tb:s-2PVYXTQSG8BWC8XKENV6^|1676267737649&t:1676267739585&adb:adblk_no; ubid-main=130-7501307-7489137; session-token=GZvAIDLjtYL2dns7dP5bqlhPtdy6h+MpzY4Rf4a7NB8LBIo4k3uYpzZLOKzG3BxmuR6HIdkRCEj/2T2qU/j7CKnwqaa/uhQqrMzMPt0+zox8f9tXgEG8SnugYXf4uQ7r4/JOBVgn5cKQdJQw2aVow8NgcQpoMh4tpl678AyJiqJ+Qi7qfS4yfUAZs2hxJfilwtktFsvHij5CDJZ/X2bmfWjng3J0Ko4OEIILRpMbuWM=; lc-main=en_US; x-amz-captcha-1=1675843545355343; x-amz-captcha-2=o1Tv/YwZfmSCEtZ1VzUVkQ==; aws-ubid-main=421-0416387-0055608; aws-account-alias=525363637819; remember-account=true; aws-userInfo=^%^7B^%^22arn^%^22^%^3A^%^22arn^%^3Aaws^%^3Aiam^%^3A^%^3A525363637819^%^3Auser^%^2Fayush-p^%^22^%^2C^%^22alias^%^22^%^3A^%^22525363637819^%^22^%^2C^%^22username^%^22^%^3A^%^22ayush-p^%^22^%^2C^%^22keybase^%^22^%^3A^%^22PJPJw5BAK3VXtx^%^2BddvGG1RHe3ItA^%^2F9fwv2F8MDptuL4^%^5Cu003d^%^22^%^2C^%^22issuer^%^22^%^3A^%^22http^%^3A^%^2F^%^2Fsignin.aws.amazon.com^%^2Fsignin^%^22^%^2C^%^22signinType^%^22^%^3A^%^22PUBLIC^%^22^%^7D; regStatus=registered; noflush_awsccs_sid=c37e720e43c6c33ca8dd6949f816e133d00452dbead9dde7227c0ce0a1ab8f73; AMCV_7742037254C95E840A4C98A6^%^40AdobeOrg=1585540135^%^7CMCIDTS^%^7C19398^%^7CvVersion^%^7C4.4.0^%^7CMCMID^%^7C48446461477515895770141661042213689321^%^7CMCAAMLH-1676563160^%^7C12^%^7CMCAAMB-1676563160^%^7C6G1ynYcLPuiQxYZrsz_pkqfLG9yMXBpb2zX5dvJdYQJzPXImdj0y^%^7CMCOPTOUT-1675965560s^%^7CNONE^%^7CMCAID^%^7CNONE^%^7CMCSYNCSOP^%^7C411-19403; aws-target-visitor-id=1675793084249-357767.31_0; aws-target-data=^%^7B^%^22support^%^22^%^3A^%^221^%^22^%^7D; s_nr=1675840668721-New; s_vnum=2107840657861^%^26vn^%^3D1; s_dslv=1675840668722; aws-search-rs-dismissed=1; awsc-color-theme=light; awsc-uh-opt-in=; aws-userInfo-signed=eyJ0eXAiOiJKV1MiLCJrZXlSZWdpb24iOiJ1cy1lYXN0LTEiLCJhbGciOiJFUzM4NCIsImtpZCI6IjA5ZDVmMGY5LWEzZWQtNDRkYS04Mzk3LWZmMTk5OTg5NGZkMyJ9.eyJzdWIiOiI1MjUzNjM2Mzc4MTkiLCJzaWduaW5UeXBlIjoiUFVCTElDIiwiaXNzIjoiaHR0cDpcL1wvc2lnbmluLmF3cy5hbWF6b24uY29tXC9zaWduaW4iLCJrZXliYXNlIjoiUEpQSnc1QkFLM1ZYdHgrZGR2R0cxUkhlM0l0QVwvOWZ3djJGOE1EcHR1TDQ9IiwiYXJuIjoiYXJuOmF3czppYW06OjUyNTM2MzYzNzgxOTp1c2VyXC9heXVzaC1wIiwidXNlcm5hbWUiOiJheXVzaC1wIn0.GbwcP-opMd5FavAR026jFB1TtB1o0Z5vbeFRrMB_KENzf48-EuVQaYzA2we9D62vNI4N1b0xiVAhD1O-KLE3A5_ny5RDQBlh6QHMLRYEjGjF6KJdEaaiAIxK65nF9J_d; aws-signer-token_us-east-1=eyJrZXlWZXJzaW9uIjoib0lWaXJid0VNMktHYzJxdnRnN0hqc3d3NWNvb1lsVy4iLCJ2YWx1ZSI6ImduNHBuaGJJMFJYaHl3cWpKUkRudlVCaDJsTW1xT2JPZ0pCclN5ZTZFN009IiwidmVyc2lvbiI6MX0=; skin=noskin',
                        #'Upgrade-Insecure-Requests': '1',
                        'Sec-Fetch-Dest': 'document',
                        'Sec-Fetch-Mode': 'navigate',
                        'Sec-Fetch-Site': 'none',
                        'Sec-Fetch-User': '?1',
                        # Requests doesn't support trailers
                        # 'TE': 'trailers',
                        }, Headers(headers=True).generate() 
                    ] 
            proxy =random.choice(PROXIES)
            print(f"Using PROXY : {proxy} for {response.request.url}")
            time.sleep(60)  
            logging.info(f'TRYING WITH DIFF. PROXY {response.request.url}')
            yield scrapy.Request(response.request.url ,
                                headers= random.choice(headers),
                                 meta={'retry': True ,'proxy':proxy})
    


class ShowStatus(RetryMiddleware):
      def process_response(self, request, response, spider):
        print("inside retry mw ",response.status)
        if response.status==503:
            proxy =random.choice(PROXIES)
            print(f"Using PROXY : {proxy}")
            return scrapy.Request(response.request.url , headers=self.headers ,dont_filter=True,
                                  meta={'retry': True ,'proxy':proxy})
        else:
            print("RMW NOT 503")
            return response


class AmazonsearchproductspiderSpiderMiddleware:
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the spider middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_spider_input(self, response, spider):
        # Called for each response that goes through the spider
        # middleware and into the spider.

        # Should return None or raise an exception.
        return None

    def process_spider_output(self, response, result, spider):
        # Called with the results returned from the Spider, after
        # it has processed the response.

        # Must return an iterable of Request, or item objects.
        for i in result:
            yield i

    def process_spider_exception(self, response, exception, spider):
        # Called when a spider or process_spider_input() method
        # (from other spider middleware) raises an exception.

        # Should return either None or an iterable of Request or item objects.
        pass

    def process_start_requests(self, start_requests, spider):
        # Called with the start requests of the spider, and works
        # similarly to the process_spider_output() method, except
        # that it doesn’t have a response associated.

        # Must return only requests (not items).
        for r in start_requests:
            yield r

    def spider_opened(self, spider):
        spider.logger.info('Spider opened: %s' % spider.name)


class AmazonsearchproductspiderDownloaderMiddleware:
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the downloader middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_request(self, request, spider):
        # Called for each request that goes through the downloader
        # middleware.

        # Must either:
        # - return None: continue processing this request
        # - or return a Response object
        # - or return a Request object
        # - or raise IgnoreRequest: process_exception() methods of
        #   installed downloader middleware will be called
        return None

    def process_response(self, request, response, spider):
        # Called with the response returned from the downloader.

        # Must either;
        # - return a Response object
        # - return a Request object
        # - or raise IgnoreRequest
        return response

    def process_exception(self, request, exception, spider):
        # Called when a download handler or a process_request()
        # (from other downloader middleware) raises an exception.

        # Must either:
        # - return None: continue processing this exception
        # - return a Response object: stops process_exception() chain
        # - return a Request object: stops process_exception() chain
        pass

    def spider_opened(self, spider):
        spider.logger.info('Spider opened: %s' % spider.name)
