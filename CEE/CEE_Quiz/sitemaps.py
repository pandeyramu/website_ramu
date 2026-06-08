from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from CEE_Quiz.models import Subject, Chapter

class StaticViewSitemap(Sitemap):
    priority = 1.0
    changefreq = 'weekly'

    def items(self):
        return ['home', 'about', 'contact', 
                'privacy_policy', 'disclaimer', 'blog']

    def location(self, item):
        return reverse(item)

class SubjectSitemap(Sitemap):
    priority = 0.8
    changefreq = 'weekly'

    def items(self):
        return Subject.objects.all()

    def location(self, obj):
        return f'/subject/{obj.slug}/'

class BlogSitemap(Sitemap):
    priority = 0.7
    changefreq = 'monthly'

    def items(self):
        from CEE_Quiz.views import BLOG_POSTS
        class BlogPostMock:
            def __init__(self, slug):
                self.slug = slug
        return [BlogPostMock(slug) for slug in BLOG_POSTS.keys()]

    def location(self, obj):
        return f'/blog/{obj.slug}/'
sitemaps = {
    "static": StaticViewSitemap,
    "subjects": SubjectSitemap,
    "blog": BlogSitemap,
}