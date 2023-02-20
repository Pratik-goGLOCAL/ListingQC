# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class AmazonsearchproductspiderItem(scrapy.Item):
    product_url = scrapy.Field()
    product_title = scrapy.Field()
    product_asin = scrapy.Field()
    product_brand=scrapy.Field()
    product_price = scrapy.Field()
    product_stars= scrapy.Field()
    product_rating_count = scrapy.Field()
    product_bullets = scrapy.Field()
    product_images = scrapy.Field()
    country_of_origin = scrapy.Field()
    product_weight= scrapy.Field()
    product_material= scrapy.Field()
    product_category= scrapy.Field()
    item_height = scrapy.Field()
    item_height_unit= scrapy.Field()
    item_length= scrapy.Field()
    item_length_unit= scrapy.Field()
    item_width= scrapy.Field()
    item_width_unit= scrapy.Field()
    aplus= scrapy.Field()
    description= scrapy.Field()
    product_videos= scrapy.Field()


    
