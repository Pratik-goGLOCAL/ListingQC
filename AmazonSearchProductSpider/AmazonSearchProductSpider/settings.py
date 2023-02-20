# Scrapy settings for AmazonSearchProductSpider project
#
# For simplicity, this file contains only settings considered important or
# commonly used. You can find more settings consulting the documentation:
#
#     https://docs.scrapy.org/en/latest/topics/settings.html
#     https://docs.scrapy.org/en/latest/topics/downloader-middleware.html
#     https://docs.scrapy.org/en/latest/topics/spider-middleware.html

BOT_NAME = 'AmazonSearchProductSpider'
SPIDER_MODULES = ['AmazonSearchProductSpider.spiders']
NEWSPIDER_MODULE = 'AmazonSearchProductSpider.spiders'


# Crawl responsibly by identifying yourself (and your website) on the user-agent
#USER_AGENT = 'AmazonSearchProductSpider (+http://www.yourdomain.com)'

# Obey robots.txt rules
ROBOTSTXT_OBEY = True

#HTTPCACHE_ENABLED = True
DOWNLOAD_DELAY =5
#AUTOTHROTTLE_ENABLED = True
#PROXY_POOL_ENABLED = True
#USER_AGENT ="https://developers.whatismybrowser.com/useragents/parse/79-googlebot"
DUPEFILTER_CLASS = 'scrapy.dupefilters.BaseDupeFilter'
RETRY_HTTP_CODES=[503]
DOWNLOADER_MIDDLEWARES = {
    # ...
    #'scrapy_proxy_pool.middlewares.ProxyPoolMiddleware': 610,
    #'scrapy_proxy_pool.middlewares.BanDetectionMiddleware': 620,
    'rotating_proxies.middlewares.RotatingProxyMiddleware': 610,
    'rotating_proxies.middlewares.BanDetectionMiddleware': 620,
    #'scrapy.downloadermiddlewares.useragent.UserAgentMiddleware': None,
    #'scrapy.downloadermiddlewares.retry.RetryMiddleware': None,
    #'AmazonSearchProductSpider.middlewares.AmazonSearchProductSpiderDownloaderMiddleware': 543,

    # ...
}

PROXIES=["https://116.202.165.119:3124",
         "https://139.59.60.46:3128",
         "http://103.215.207.38:83",
         "http://139.59.1.14:8080",
         "http://45.114.78.140:3128",
         "http://103.48.68.107:83",
         "http://164.100.131.37:80",
         "http://164.100.131.37:8080",
         "http://103.215.207.85:82",
         "http://14.140.131.82:3128",
         "http://139.59.33.166:80",
         "http://115.241.197.126:80",
         "http://157.119.211.133:8080",
         "http://150.129.201.30:6666",
         "http://45.248.138.150:8080",
         "http://49.249.155.3:80",
         "http://103.24.20.208:80",#WORKING
         "http://115.96.208.124:8080",
        ]

SPIDER_MIDDLEWARES = {
        'scrapy.spidermiddlewares.httperror.HttpErrorMiddleware': None,
        'AmazonSearchProductSpider.middlewares.MyHttpErrorMiddleware': 540,
}
# Configure maximum concurrent requests performed by Scrapy (default: 16)
CONCURRENT_REQUESTS = 1

# Configure a delay for requests for the same website (default: 0)
# See https://docs.scrapy.org/en/latest/topics/settings.html#download-delay
# See also autothrottle settings and docs
#DOWNLOAD_DELAY = 3
# The download delay setting will honor only one of:
#CONCURRENT_REQUESTS_PER_DOMAIN = 16
#CONCURRENT_REQUESTS_PER_IP = 16

# Disable cookies (enabled by default)
#COOKIES_ENABLED = False

# Disable Telnet Console (enabled by default)
#TELNETCONSOLE_ENABLED = False

# Override the default request headers:
#DEFAULT_REQUEST_HEADERS = {
#   'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
#   'Accept-Language': 'en',
#}

# Enable or disable spider middlewares
# See https://docs.scrapy.org/en/latest/topics/spider-middleware.html
#SPIDER_MIDDLEWARES = {
#    'AmazonSearchProductSpider.middlewares.AmazonsearchproductspiderSpiderMiddleware': 543,
#}

# Enable or disable downloader middlewares
# See https://docs.scrapy.org/en/latest/topics/downloader-middleware.html
#DOWNLOADER_MIDDLEWARES = {
#    'AmazonSearchProductSpider.middlewares.AmazonsearchproductspiderDownloaderMiddleware': 543,
#}

# Enable or disable extensions
# See https://docs.scrapy.org/en/latest/topics/extensions.html
#EXTENSIONS = {
#    'scrapy.extensions.telnet.TelnetConsole': None,
#}

# Configure item pipelines
# See https://docs.scrapy.org/en/latest/topics/item-pipeline.html
#ITEM_PIPELINES = {
#    'AmazonSearchProductSpider.pipelines.AmazonsearchproductspiderPipeline': 300,
#}

# Enable and configure the AutoThrottle extension (disabled by default)
# See https://docs.scrapy.org/en/latest/topics/autothrottle.html
#AUTOTHROTTLE_ENABLED = True
# The initial download delay
#AUTOTHROTTLE_START_DELAY = 5
# The maximum download delay to be set in case of high latencies
#AUTOTHROTTLE_MAX_DELAY = 60
# The average number of requests Scrapy should be sending in parallel to
# each remote server
#AUTOTHROTTLE_TARGET_CONCURRENCY = 1.0
# Enable showing throttling stats for every response received:
#AUTOTHROTTLE_DEBUG = False

# Enable and configure HTTP caching (disabled by default)
# See https://docs.scrapy.org/en/latest/topics/downloader-middleware.html#httpcache-middleware-settings
#HTTPCACHE_ENABLED = True
#HTTPCACHE_EXPIRATION_SECS = 0
#HTTPCACHE_DIR = 'httpcache'
#HTTPCACHE_IGNORE_HTTP_CODES = []
#HTTPCACHE_STORAGE = 'scrapy.extensions.httpcache.FilesystemCacheStorage'
