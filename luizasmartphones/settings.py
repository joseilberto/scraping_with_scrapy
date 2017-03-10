# -*- coding: utf-8 -*-

BOT_NAME = 'luizasmartphones' #spidername

SPIDER_MODULES = ['luizasmartphones.spiders']
NEWSPIDER_MODULE = 'luizasmartphones.spiders'

ITEM_PIPELINES = {'luizasmartphones.pipelines.MongoDBPipeline': 300}

MONGODB_SERVER = 'localhost'
MONGODB_PORT = 27017
MONGODB_DB = "luizasmartphonesdb" #mongodb database name
MONGODB_COLLECTION = "smartphones" #mongodb collection used

ROBOTSTXT_OBEY = True

DOWNLOAD_DELAY = 0.5 #a delay is introduced to politely scrapy pages
