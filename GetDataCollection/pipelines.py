# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
import json
import urllib.request as request
from datetime import datetime
import sqlite3
from scrapy.exceptions import DropItem

class GetdatacollectionPipeline(object):
    app_ids = set()
    output_fileName = 'wangcard'
    bundleId_urlScheme_map = {}

    def get_bundle_id(self, package_name):
        url_format = 'https://a.app.qq.com/o/ajax/micro/MicroDownAppInfo?pkgname={0}'
        
        response = request.urlopen(url_format.format(package_name))
        response_map = json.loads(response.read())
        
        iosUrl = response_map['data']['appExt']['iosUrl']
        if iosUrl:
            bundle_id_index = iosUrl.index('id') + len('id')
            # 9 = len(bundleId)
            return iosUrl[bundle_id_index : bundle_id_index + 9]

    def get_url_scheme(self, bundle_id):
        if bundle_id :
            return self.bundleId_urlScheme_map[bundle_id] if bundle_id in self.bundleId_urlScheme_map else ''

    def process_item(self, item, spider):
        if item['id'] in self.app_ids:
            raise DropItem("Duplicate item found: %s" % item)
        else:
            item['bundleId'] = self.get_bundle_id(item['packageName'])
            item['urlScheme'] = self.get_url_scheme(item['bundleId'])

            item_line = ('' if len(self.app_ids) == 0 else ',\n') + '        ' + json.dumps(dict(item))
            self.file.write(item_line)

            self.app_ids.add(item['id'])

            return item

    def init_bundle_id_url_scheme_map(self):
        map_file = open('input/BundleId_UrlScheme_Map.json', 'r')
        self.bundleId_urlScheme_map = json.loads(map_file.read())
        map_file.close()

    def open_spider(self, spider):
        self.output_fileName += datetime.now().strftime('_%Y%m%d_%H_%M_%S')
        self.file = open('output/wangcard' + self.output_fileName + '.json', 'w')
        self.file.write('{\n')
        self.file.write('    "appList": [\n')
        self.init_bundle_id_url_scheme_map()

    def close_spider(self, spider):
        self.file.write('\n    ],\n')
        self.file.write('    "appCount": ' + str(len(self.app_ids)) + '\n')
        self.file.write('}')
        self.file.close()
        self.save_to_db()

    def save_to_db(self):
        conn = sqlite3.connect('output/' + self.output_fileName + '.db')
        conn.execute('CREATE TABLE app (id VARCHAR(30) PRIMARY KEY, name VARCHAR(30), description VARCHAR(256), icon_url VARCHAR(30), package_name VARCHAR(30), bundle_id VARCHAR(30), url_scheme VARCHAR(30))')
        file = open('output/wangcard' + self.output_fileName + '.json', 'r')
        data_map = json.loads(file.read())
        for item in data_map['appList']:
            conn.execute("INSERT INTO app VALUES('%s', '%s', '%s', '%s', '%s', '%s', '%s')" % (item['id'], item['name'], item['description'], item['iconUrl'], item['packageName'], item['bundleId'], item['urlScheme']))
        conn.commit()
        conn.close()

        file.close()


            


