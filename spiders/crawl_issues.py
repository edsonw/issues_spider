#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2018/1/19 20:04
# @Author  : sunday
# @Site    : 
# @File    : crawl_issues.py
# @Software: PyCharm

import scrapy
from scrapy.http import Request
import json
import itertools
from issues_spider.items import GitHubIssues
from issues_spider.items import GitHubComments
from scrapy.conf import settings
import re


class CrawlIssues(scrapy.Spider):
    handle_httpstatus_list = [403, 401, 404]
    name = 'crawl_issues'
    allowed_domains = ['api.github.com']
    start_urls = ['https://api.github.com']
    tokens = ["34d9931d22c5ba2c48bd93cc3e6e1b5b2bc7620d", "237b3763792474c3e3c94b6fb47fbed2f93bef14",
              "098b89fffb0a9d51f9c6e32520438461d4381cb1", "b2200a1d9afed61322a1a5e0332ba63edece6f09",
              "f71f3953a533f2638b2041c9420af3406e697b9d", "c05088d8fbf49fec5e52d01c5faf171e6af7a139",
              '34f6ded60da1f41641bfdb80377fa26ede35ed1e',
              'c72b8e1b9f65deb45fd4327cff09ededec4a463c',
              '5797dbb74e6fe2a1f6e3e73b0d1c7ee2f7497e76',
              '132e61200f189b7f5f32616e3ce7f15319f6c164',
              '8a7a5ee845b1bc461aa724990af41512b9c2e03d',
              '368538619ef48db84dafcb5109bb88216b5566f3',
              "35fd72bd13a7dcdd0eb3eeca30da6d58d9305e12",
              "29ec7f1e8d8e24e590f7e720e436f59ff41b904f",
              "1de182a2c30734e335241559449b0e4422f5c503"
              ]

    token_list = [
        '293a06ac6ed5a746f7314be5a25f3df2948fa501',
        '66de084042a7d3311544c656ad9273927dc73408',
        'a513f61368e16c2da229e38e139a8e5e25848a5c',
        '9055150c8fd031468af71cbb4e12c550e8d2ec2b',
        'ba119dc83af804327fa9dad8e07718729490c925',
        'c9c13e5c14d6876c76919520c9b05d0c65faf18a',
        '3e41cbfc0c8878aec935fba68a0d3c778f557a32',
        '402ff55399ca08ca7c886a2031f49f16be6c2331',
        '7cb6e20a24000968983b79b5de705c400f400588',
        'd147a86290a1828205ec287d0c722ffbd66cd4f9',
        '6b6956dbbc7a3249ce985e40226ed4ff793aa1df',
        'de6ec0e027d89147a111d2be266bf35e45afd067'

    ]

    it = itertools.cycle(tokens)

    agent = "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/49.0.2623.75 Safari/537.36 LBBROWSER"

    projects = [('bitcoin', 'bitcoin')
                ,('Baystation12', 'Baystation12')
                ,('twbs', 'bootstrap'),
                ('adobe', 'brackets'),
                ('cakephp', 'cakephp'),
                ('cdnjs', 'cdnjs'),
                ('cocos2d', 'cocos2d-x'),
                ('owncloud', 'core'),
                ('dlang', 'dmd'),
                ('caskroom', 'homebrew-cask'),
                ('ipython', 'ipython'),
                ('joomla', 'joomla-cms'),
                ('Katello', 'katello'),
                ('rapid7', 'metasploit-framework'),
                ('openmicroscopy', 'openmicroscopy'),
                ('hrydgard', 'ppsspp'),
                ('puppetlabs', 'puppet'),
                ('rails', 'rails'),
                ('scala', 'scala'),
                ('symfony', 'symfony'),
                ('sympy', 'sympy'),
                ('tgstation', 'tgstation'),
                ('zendframework', 'zendframework')
                ]
    def start_requests(self):
        for project in self.projects:
            headers = {
                "HOST": "api.github.com",
                "Referer": "https://api.github.com",
                'User-Agent': self.agent,
                'Authorization': 'token ' + self.it.__next__()

            }
            url = "https://api.github.com/repos/"+project[0]+"/"+project[1]+"/issues?state=closed"
            yield scrapy.Request(url, meta={"project":project}, headers=headers)




    def parse(self, response):
        headers = {
            "HOST": "api.github.com",
            "Referer": "https://api.github.com",
            'User-Agent': self.agent,
            'Authorization': 'token ' + self.it.__next__()
        }

        # 如果获取成功则对获取到的每一条记录进行处理，获取每一条issue的comments
        if response.status == 200:
            json_result = json.loads(response.text)
            for issue in json_result:
                item = GitHubIssues()
                item['title'] = issue['title']
                item['body'] = issue['body']
                item['created_at'] = issue['created_at']
                item['author_association'] = issue['author_association']
                item['closed_at'] = issue['closed_at']
                item['comments'] = issue['comments']
                item['comments_url'] = issue['comments_url']
                item['number'] = issue['number']
                item['user_login'] = issue['user']['login']
                item['state'] = issue['state']
                item['url'] = issue['url']
                item['repository_url'] = issue['repository_url']
                item['events_url'] = issue['events_url']
                item['user_id'] = issue['user']['id']
                item['updated_at'] = issue['updated_at']
                item['project'] = response.meta.get("project", {})[1]
                item['type'] = 'Issues'

                yield item

                #处理每一条记录的comment
                yield scrapy.Request(issue["comments_url"],meta={"project":response.meta.get("project",{}),
                                                             "issue_id":issue['number']}, headers=headers,callback=self.parse_comments)

            # 如果返回結果中有包含下一页的信息那么循环获取下一页的记录
            links = response.headers.get("Link")
            if links:
                links = response.headers.get("Link").decode()
                link_list = links.split(',')
                for link in link_list:
                    match_obj = re.match(' ?<{1}(.*)>; rel="next', link)
                    if match_obj:
                        next_url = match_obj.group(1)
                        yield scrapy.Request(next_url, meta=response.meta, headers=headers)



    # 处理comments
    def parse_comments(self,response):
        headers = {
            "HOST": "api.github.com",
            "Referer": "https://api.github.com",
            'User-Agent': self.agent,
            'Authorization': 'token ' + self.it.__next__()
        }

        if response.status == 200:
            json_result = json.loads(response.text)
            for comment in json_result:
                item = GitHubComments()
                item['body'] = comment['body']
                item['issue_id'] = response.meta.get("issue_id",{})
                item['created_at'] = comment['created_at']
                item['issue_url'] = comment['issue_url']
                item['author_association'] = comment['author_association']
                item['user_login'] = comment['user']['login']
                item['user_type'] = comment['user']['type']
                item['user_id'] = comment['user']['id']
                item['comment_url'] = comment['url']
                item['comment_html_url'] = comment['html_url']
                item['comment_id'] = comment['id']
                item['updated_at'] = comment['updated_at']
                item['project'] = response.meta.get("project",{})[1]
                item['type'] = 'Comments'

                yield item

            # 如果返回結果中有包含下一页的信息那么循环获取下一页的记录
            links = response.headers.get("Link")
            if links:
                links = response.headers.get("Link").decode()
                link_list = links.split(',')
                for link in link_list:
                    match_obj = re.match(' ?<{1}(.*)>; rel="next', link)
                    if match_obj:
                        next_url = match_obj.group(1)
                        yield scrapy.Request(next_url, meta=response.meta, headers=headers,callback=self.parse_comments)












