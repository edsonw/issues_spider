# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy
from scrapy.item import Item, Field

class IssueSpiderItem(Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass

class GitHubIssues(Item):

    issue_id = Field()
    title = Field()
    body = Field()
    created_at = Field()
    id = Field()
    author_association = Field()
    closed_at = Field()
    comments = Field()
    comments_url = Field()
    number = Field()
    user_login = Field()
    state = Field()
    url = Field()
    repository_url = Field()
    events_url = Field()
    user_id = Field()
    updated_at = Field()
    project = Field()
    type = Field()



class GitHubComments(Item):
    body = Field()
    issue_id = Field()
    created_at = Field()
    updated_at = Field()
    issue_url = Field()
    author_association = Field()
    user_login = Field()
    user_type = Field()
    user_id = Field()
    comment_url = Field()
    comment_html_url = Field()
    comment_id = Field()
    project = Field()
    type = Field()