# -*- coding: utf-8 -*-
import pymongo

from scrapy.conf import settings
from scrapy.exceptions import DropItem
from scrapy import log


class MongoDBPipeline(object):

    def __init__(self):
        connection = pymongo.MongoClient(
            settings['MONGODB_SERVER'],
            settings['MONGODB_PORT']
        )
        db = connection[settings['MONGODB_DB']]
        self.collection = db[settings['MONGODB_COLLECTION']]

    def process_item(self, item, spider):
        for data in item:
            if not data:
                raise DropItem("Missing data!") #if data is missing, item is not added to database
        self.collection.update({'url': item['url']}, dict(item), upsert=True)
        log.msg("Value added to MongoDB database!", #if data is okay it adds it
                level=log.DEBUG, spider=spider)
        return item
