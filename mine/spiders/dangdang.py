# -*- coding: utf-8 -*-
import scrapy
from scrapy_redis.spiders import RedisSpider
import urllib
from copy import deepcopy

class DanddangSpider(RedisSpider):
    name = 'dangdang'
    allowed_domains = ['dangdang.com']
    # start_urls = ['http://book.dangdang.com/']
    redis_key = 'dangdang:start_urls'

    def parse(self, response):
        # 大分类
        div_list = response.xpath('//div[@class="con flq_body"]/div')
        # print(div_list)
        for div in div_list:
            item = {}
            item['B_cate'] = div.xpath('./dl/dt//text()').extract()
            item['B_cate'] = [i.strip() for i in item['B_cate'] if len(i.strip())>0]
            # print(item)
            # 二级分类cl
            dl_list = div.xpath('./div/div/div/dl')
            for dl in dl_list:
                # print(dl)
                item['M_cate'] = dl.xpath('./dt//text()').extract()
                item['M_cate'] = [i.strip() for i in item['M_cate'] if len(i.strip()) > 0]
                # print(item)
                # 小分类
                a_list = dl.xpath('./dd/a')
                for a in a_list:
                    item['S_href'] = a.xpath('./@href').extract_first()
                    item['S_cate'] = a.xpath('.//text()').extract_first()
                    # print(item)

                    if item['S_href'] is not None:
                        yield scrapy.Request(
                            item['S_href'],
                            callback=self.parse_book_list,
                            meta={'item':deepcopy(item)}
                        )

    def parse_book_list(self,response):
        item = response.meta['item']
        li_list = response.xpath('//div[@id="search_nature_rg"]/ul/li')
        for li in li_list:
            item['name'] = li.xpath('./p[@class="name"]/a/text()').extract_first()
            item['price'] = li.xpath('./p[@class="price"]/span[1]/text()').extract_first()
            item['bg'] = li.xpath('./a/img/@src').extract_first()
            if item['bg'] == 'images/model/guan/url_none.png':
                item['bg'] = li.xpath('./a/img/@data-original').extract_first()

            print(item)

        next_url = response.xpath('//div[@class="paging"]/ul/li[@class="next"]/a/@href').extract_first()
        if next_url is not None:
            next_url = urllib.parse.urljoin(response.url,next_url)
            yield scrapy.Request(
                next_url,
                callback=self.parse_book_list,
                meta={'item':item}
            )
