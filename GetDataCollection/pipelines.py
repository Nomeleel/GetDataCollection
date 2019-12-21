# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
import json
import urllib.request as request

class GetdatacollectionPipeline(object):
    appCount = 0

    def get_bundle_id(self, package_name):
        url_format = 'https://a.app.qq.com/o/ajax/micro/MicroDownAppInfo?pkgname={0}'
        
        response = request.urlopen(url_format.format(package_name))
        response_map = json.loads(response.read())
        
        return response_map['data']['appExt']['iosUrl']

    def process_item(self, item, spider):
        item['bundleId'] = self.get_bundle_id(item['packageName'])

        itemLine = ('' if self.appCount == 0 else ',') + '\n' + '        ' + json.dumps(dict(item))
        self.file.write(itemLine)
        self.appCount += 1
        return item

    def open_spider(self, spider):
        self.file = open('items.json', 'w')
        self.file.write('{\n')
        self.file.write('    "appList": [\n')

    def close_spider(self, spider):
        self.file.write('\n    ]\n')
        self.file.write('}')
        self.file.close()


            


