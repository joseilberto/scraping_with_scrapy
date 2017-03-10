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
