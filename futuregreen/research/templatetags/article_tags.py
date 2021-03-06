# research/templatetags/article_tags.py

import re

from django import template
from django.conf import settings
from django.db import models

Article = models.get_model('research', 'article')

register = template.Library()


class LatestArticles(template.Node):
    def __init__(self, limit, var_name):
        self.limit = int(limit)
        self.var_name = var_name

    def render(self, context):
        articles = Article._default_manager.live()[:self.limit]
        if articles and (self.limit == 1):
            context[self.var_name] = articles[0]
        else:
            context[self.var_name] = articles
        return ''


@register.tag
def get_latest_articles(parser, token):
    """
Gets any number of latest articles and stores them in a variable.

Syntax::

{% get_latest_articles [limit] as [var_name] %}

Example usage::

{% get_latest_articles 10 as latest_article_list %}
"""
    try:
        tag_name, arg = token.contents.split(None, 1)
    except ValueError:
        raise template.TemplateSyntaxError, "%s tag requires arguments" % token.contents.split()[0]
    m = re.search(r'(.*?) as (\w+)', arg)
    if not m:
        raise template.TemplateSyntaxError, "%s tag had invalid arguments" % tag_name
    format_string, var_name = m.groups()
    return LatestArticles(format_string, var_name)