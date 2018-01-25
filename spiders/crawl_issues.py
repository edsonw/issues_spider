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












