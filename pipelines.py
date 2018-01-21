# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

import pymongo
from scrapy.conf import settings
from scrapy.exceptions import DropItem
from scrapy import log
from pymongo import MongoClient

class IssueSpiderPipeline(object):
    def __init__(self):
        client = MongoClient(settings['MONGODB_SERVER'],
            settings['MONGODB_PORT'])

        self.db = client[settings['MONGODB_DB']]


    def process_item(self, item, spider):
        valid = True
        for data in item:
            if not data:
                valid = False
                raise DropItem("Missing {0}!".format(data))
        if valid:
            if item['type'] == 'Issues':
                collection = self.db[item['project']+'Issues']
                collection.insert(dict(item))
            elif item['type'] == 'Comments':
                collection = self.db[item['project'] + 'Comments']
                collection.insert(dict(item))

            log.msg("Issue added to MongoDB database!",
                    level=log.DEBUG, spider=spider)

        return item
