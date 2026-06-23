from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from CEE_Quiz.models import Subject, Chapter, SubChapter

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

class ChapterSitemap(Sitemap):
    priority = 0.7
    changefreq = 'weekly'

    def items(self):
        return Chapter.objects.all()

    def location(self, obj):
        return f'/chapter/{obj.slug}/'

class SubChapterSitemap(Sitemap):
    priority = 0.6
    changefreq = 'weekly'

    def items(self):
        return SubChapter.objects.all()

    def location(self, obj):
        return f'/mcq/{obj.slug}/'

class BlogSitemap(Sitemap):
    priority = 0.7
    changefreq = 'monthly'

    def items(self):
        from CEE_Quiz.views import BLOG_POST_ORDER
        return BLOG_POST_ORDER  

    def location(self, obj):
        return f'/blog/{obj}/'  

sitemaps = {
    "static": StaticViewSitemap,
    "subjects": SubjectSitemap,
    "chapters": ChapterSitemap,
    "subchapters": SubChapterSitemap,
    "blog": BlogSitemap,
}