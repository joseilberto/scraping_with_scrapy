# -*- coding: utf-8 -*-
from scrapy.item import Item, Field

#creates the LuizaItem class which has the items that will be stored in database
class LuizaItem(Item):
    url = Field()
    title = Field()
    price = Field()
    system = Field()
