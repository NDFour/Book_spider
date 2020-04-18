# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class ByspiderItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    title = scrapy.Field()
    author = scrapy.Field()
    rating = scrapy.Field()
    category = scrapy.Field()
    infos = scrapy.Field()
    description = scrapy.Field()
    pic = scrapy.Field()
    pan_1 = scrapy.Field()
    pan_2 = scrapy.Field()
    pan_3 = scrapy.Field()
    pan_pass = scrapy.Field()
    origin = scrapy.Field()
