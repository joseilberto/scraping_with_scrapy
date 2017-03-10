Usando o Scrapy para extração de dados
===========================================================

O código abaixo foi desenvoldido no Ubuntu 16.04 e possui 3 requerimentos:

1. Instalação do mongodb que pode ser feita clicando [aqui](https://docs.mongodb.com/manual/tutorial/install-mongodb-on-ubuntu/).

2. Presença do pacote pymongo que pode ser obtido através:```shell sudo pip3 install pymongo```.

3. Instalação do scrapy: ```shell sudo pip3 install scrapy```.

Para as 3 instalações, todas as configurações padrões foram mantidas.

##Ativando mongodb
Para que o scrapy seja capaz de acessar o banco de dados, precisamos ativá-lo fazendo:
```shell
sudo service mongod start
```

##Utilizando esse projeto do scrapy
Na pasta de sua preferência, faça uma cópia do diretório no github:
```shell
git clone https://github.com/joseilberto/scraping_with_scrapy
```
E execute:
```shell
scrapy crawl luizasmartphones
```

##Funcionalidade
Essa rotina é capaz de extrair url, título, preço e OS dos smartphones encontrados [aqui](http://www.magazineluiza.com.br/smartphone/celulares-e-smartphones/s/te/tcsp/), executando a paginação necessária.

##Objetivos da chamada
* Utilização de xpath nas buscas por links --> Ok
* Persistência das informações --> Ok
* PostgreSQL --> Não testado
* MongoDB --> Testado e utilizado nesta documentação
* RethinkDB --> Testado
* Submissão de formulários --> Em construção
* Tratamento de paginação --> Ok
* Manipulação de Querystrings --> Em construção
* Autenticação --> Em construção
* Utilizar logs para sinalizar ocorrências durante o scraping --> Ok (os logs foram comentados no código)

##Tempo necessário para elaboração
Tempo de estudo: 12h (2h voltadas ao estudo básico do scrapy ([aqui](https://realpython.com/blog/python/web-scraping-with-scrapy-and-mongodb/) e [aqui](https://realpython.com/blog/python/web-scraping-and-crawling-with-scrapy-and-mongodb/)) e 10h para adequação dos exemplos no olx ([aqui](http://www.gilenofilho.com.br/usando-o-scrapy-e-o-rethinkdb-para-capturar-e-armazenar-dados-imobiliarios-parte-i/) e [aqui](http://www.gilenofilho.com.br/usando-o-scrapy-e-o-rethinkdb-para-capturar-e-armazenar-dados-imobiliarios-parte-ii/)) utilizando RethinkDB).

Escrevendo o programa: 2h (Perceber que os valores dos preços estavam no conteúdo meta do site consumiu 1:30h)

##Arquivo /luizasmartphones/spiders/luiza_spider.py
```python
import scrapy as sc
from luizasmartphones.items import LuizaItem

class LuizaSmartphonesSpider(sc.Spider):
    name = 'luizasmartphones' #spider name
    allowed_domains = ['magazineluiza.com.br']
    start_urls = ['http://www.magazineluiza.com.br/smartphone/celulares-e-smartphones/s/te/tcsp/']

    def parse(self, response):
        #find all smartphone items in page
        items = response.xpath('//ul[contains(@class, "productShowCase big")]//li[contains(@class, "product")]')
        for item in items:
            item_url = item.xpath('.//a[contains(@itemprop, "url")]/@href').extract_first()
            #determines its url
            if item_url: url = 'http://www.magazineluiza.com.br' + item_url
            yield sc.Request(url = url, callback = self.parse_detail)
        next_page_url = response.xpath('//div[contains(@class, "center")]//a[contains(@class, "forward")]/@href').extract_first()
        if next_page_url:
            next_page = 'http://www.magazineluiza.com.br' + next_page_url
            #self.log('Next page: {0}'.format(next_page))
            yield sc.Request(url = next_page, callback = self.parse)

    def parse_detail(self, response):
        #self.log(u'smartphone: {0}'.format(response.url))
        #creates the item type which will be stored in database
        item = LuizaItem()
        item['url'] = response.url #gets its url
        #finds its title and price which is always contained in the 8th position in meta content
        item['title'] = response.xpath('//h1[contains(@itemprop, "name")]/text()').extract_first()
        item['price'] = response.xpath('//meta/@content').extract()[7]
        #finds where the details boxes matches OS specs and retrieve OS name
        details = response.xpath('//div[contains(@class, "fs-row")]')
        for detail in details:
            #import ipdb; ipdb.set_trace()
            if detail.xpath('.//strong/text()').extract_first() == 'Sistema Operacional':
                item['system'] = detail.xpath('.//div[contains(@class, "row-fs-right")]//p/text()').extract_first()
        yield item #yields item to be stored in database
```
##Arquivo /luizasmartphones/pipelines.py
```python
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
```

##Arquivo /luizasmartphones/settings.py
```python
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
```

##Arquivo /luizasmartphones/items.py
```python
# -*- coding: utf-8 -*-
from scrapy.item import Item, Field

#creates the LuizaItem class which has the items that will be stored in database
class LuizaItem(Item):
    url = Field()
    title = Field()
    price = Field()
    system = Field()
```


 
