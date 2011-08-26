import re

from django import template
from django.conf import settings
from django.db import models
from django.contrib.auth.models import User
from django.db.models import Count

Post = models.get_model('blog', 'post')
Category = models.get_model('blog', 'category')
BlogRoll = models.get_model('blog', 'blogroll')

register = template.Library()


class LatestPosts(template.Node):
    def __init__(self, limit, var_name):
        self.limit = int(limit)
        self.var_name = var_name

    def render(self, context):
        posts = Post.objects.published()[:self.limit]
        if posts and (self.limit == 1):
            context[self.var_name] = posts[0]
        else:
            context[self.var_name] = posts
        return ''


@register.tag
def get_latest_posts(parser, token):
    """
    Gets any number of latest posts and stores them in a varable.

    Syntax::

        {% get_latest_posts [limit] as [var_name] %}

    Example usage::

        {% get_latest_posts 10 as latest_post_list %}
    """
    try:
        tag_name, arg = token.contents.split(None, 1)
    except ValueError:
        raise template.TemplateSyntaxError, "%s tag requires arguments" % token.contents.split()[0]
    m = re.search(r'(.*?) as (\w+)', arg)
    if not m:
        raise template.TemplateSyntaxError, "%s tag had invalid arguments" % tag_name
    format_string, var_name = m.groups()
    return LatestPosts(format_string, var_name)


class BlogAuthors(template.Node):
    def __init__(self, var_name, show_unused=True):
        self.var_name = var_name
        self.show_unused = show_unused

    def render(self, context):
        authors = User.objects.all()
        if not self.show_unused:
            authors = authors.annotate(post_count=Count('post'))\
                .filter(post_count__gt=0).order_by('first_name', 'last_name')
        context[self.var_name] = authors
        return ''


@register.tag
def get_blog_authors(parser, token):
    try:
        tag_name, arg = token.contents.split(None, 1)
    except ValueError:
        raise template.TemplateSyntaxError, "%s tag requires arguments" % token.contents.split()[0]
    m = re.search(r'as (\w+)', arg)
    if not m:
        raise template.TemplateSyntaxError, "%s tag had invalid arguments" % tag_name
    var_name = m.groups()[0]
    return BlogAuthors(var_name)


@register.tag
def get_blog_authors_used(parser, token):
    try:
        tag_name, arg = token.contents.split(None, 1)
    except ValueError:
        raise template.TemplateSyntaxError, "%s tag requires arguments" % token.contents.split()[0]
    m = re.search(r'as (\w+)', arg)
    if not m:
        raise template.TemplateSyntaxError, "%s tag had invalid arguments" % tag_name
    var_name = m.groups()[0]
    return BlogAuthors(var_name, False)


class BlogCategories(template.Node):
    def __init__(self, var_name, show_unused=True):
        self.var_name = var_name
        self.show_unused = show_unused

    def render(self, context):
        categories = Category.objects.all()
        if not self.show_unused:
            categories = categories.annotate(post_count=Count('post'))\
                .filter(post_count__gt=0)
        context[self.var_name] = categories
        return ''


@register.tag
def get_blog_categories(parser, token):
    """
    Gets all blog categories.
    """
    try:
        tag_name, arg = token.contents.split(None, 1)
    except ValueError:
        raise template.TemplateSyntaxError, "%s tag requires arguments" % token.contents.split()[0]
    m = re.search(r'as (\w+)', arg)
    if not m:
        raise template.TemplateSyntaxError, "%s tag had invalid arguments" % tag_name
    var_name = m.groups()[0]
    return BlogCategories(var_name)


@register.tag
def get_blog_categories_used(parser, token):
    """
    Gets only the blog categories that contain posts.
    """
    try:
        tag_name, arg = token.contents.split(None, 1)
    except ValueError:
        raise template.TemplateSyntaxError, "%s tag requires arguments" % token.contents.split()[0]
    m = re.search(r'as (\w+)', arg)
    if not m:
        raise template.TemplateSyntaxError, "%s tag had invalid arguments" % tag_name
    var_name = m.groups()[0]
    return BlogCategories(var_name, False)


@register.filter
def get_links(value):
    """
    Extracts links from a ``Post`` body and returns a list.

    Template Syntax::

        {{ post.body|markdown:"safe"|get_links }}

    """
    try:
        try:
            from BeautifulSoup import BeautifulSoup
        except ImportError:
            from beautifulsoup import BeautifulSoup
        soup = BeautifulSoup(value)
        return soup.findAll('a')
    except ImportError:
        if settings.DEBUG:
            raise template.TemplateSyntaxError, "Error in 'get_links' filter: BeautifulSoup isn't installed."
    return value


class BlogRolls(template.Node):
    def __init__(self, var_name):
        self.var_name = var_name

    def render(self, context):
        blogrolls = BlogRoll.objects.all()
        context[self.var_name] = blogrolls
        return ''


@register.tag
def get_blogroll(parser, token):
    """
    Gets all blogroll links.

    Syntax::

        {% get_blogroll as [var_name] %}

    Example usage::

        {% get_blogroll as blogroll_list %}
    """
    try:
        tag_name, arg = token.contents.split(None, 1)
    except ValueError:
        raise template.TemplateSyntaxError, "%s tag requires arguments" % token.contents.split()[0]
    m = re.search(r'as (\w+)', arg)
    if not m:
        raise template.TemplateSyntaxError, "%s tag had invalid arguments" % tag_name
    var_name = m.groups()[0]
    return BlogRolls(var_name)