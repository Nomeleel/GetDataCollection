import json
import scrapy
import urllib.parse as url_parse
from GetDataCollection.items import AppItem

class WangCardSpider(scrapy.Spider):
    name = "wang_card"
    allowed_domains = ["pngweb.3g.qq.com", ""]
    url_format = "https://pngweb.3g.qq.com/KingSimCardFreeFlowAppListGet?imei=&guid=&classId=0&startIndex={0}&pageSize={1}"
    start_urls = [url_format.format(0, 50)]

    def parse(self, response):

        response_map = json.loads(response.body)

        if not response_map['isLastBatch'] :
            arg_map = url_parse.parse_qs(response.url)
            start_index = int(arg_map['startIndex'][0])
            page_size = int(arg_map['pageSize'][0])
            
            yield scrapy.Request(self.url_format.format(start_index + page_size, page_size), callback = self.parse)

        app_list = response_map['appList']
        for app in app_list:
            item = AppItem()
            item['id'] = app['appId']
            item['name'] = app['appName']
            item['description'] = app['editorIntro']
            item['packageName'] = app['packageName']
            item['iconUrl'] = app['iconUrl']

            yield item
