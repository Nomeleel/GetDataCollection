# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
import json
import urllib.request as request
from datetime import datetime
import sqlite3

class GetdatacollectionPipeline(object):
    appCount = 0
    outputFileName = 'wangcard'

    def get_bundle_id(self, package_name):
        url_format = 'https://a.app.qq.com/o/ajax/micro/MicroDownAppInfo?pkgname={0}'
        
        response = request.urlopen(url_format.format(package_name))
        response_map = json.loads(response.read())
        
        iosUrl = response_map['data']['appExt']['iosUrl']
        bundleIdIndex = iosUrl.index('id') + len('id')
        # 9 = len(bundleId)
        return iosUrl[bundleIdIndex : bundleIdIndex + 9]

    def process_item(self, item, spider):
        # TODO Deduplication
        item['bundleId'] = self.get_bundle_id(item['packageName'])

        itemLine = ('' if self.appCount == 0 else ',\n') + '        ' + json.dumps(dict(item))
        self.file.write(itemLine)
        self.appCount += 1
        return item

    def open_spider(self, spider):
        self.outputFileName += datetime.now().strftime('_%Y%m%d_%H_%M_%S')
        self.file = open('output/wangcard' + self.outputFileName + '.json', 'w')
        self.file.write('{\n')
        self.file.write('    "appList": [\n')

    def close_spider(self, spider):
        self.file.write('\n    ],\n')
        self.file.write('    "appCount": ' + str(self.appCount) + '\n')
        self.file.write('}')
        self.file.close()
        self.save_to_db()

    def save_to_db(self):
        conn = sqlite3.connect('output/' + self.outputFileName + '.db')
        conn.execute('CREATE TABLE app (id VARCHAR(30) PRIMARY KEY, name VARCHAR(30), description VARCHAR(256), icon_url VARCHAR(30), package_name VARCHAR(30), bundle_id VARCHAR(30))')
        file = open('output/wangcard' + self.outputFileName + '.json', 'r')
        data_map = json.loads(file.read())
        for item in data_map['appList']:
            conn.execute("INSERT INTO app VALUES('%s', '%s', '%s', '%s', '%s', '%s')" % (item['id'], item['name'], item['description'], item['iconUrl'], item['packageName'], item['bundleId']))
        conn.commit()
        conn.close()

        file.close()


            


