from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from CEE_Quiz.models import Subject, Chapter, SubChapter, SolutionSet

class StaticViewSitemap(Sitemap):
    priority = 1.0
    changefreq = 'weekly'

    def items(self):
        return ['home', 'about', 'contact',
                'privacy_policy', 'disclaimer', 'terms_of_service', 'blog']

    def location(self, item):
        return reverse(item)

class SubjectSitemap(Sitemap):
    priority = 0.8
    changefreq = 'weekly'

    def items(self):
        return Subject.objects.order_by('id')

    def location(self, obj):
        return f'/subject/{obj.slug}/'

class ChapterSitemap(Sitemap):
    priority = 0.7
    changefreq = 'weekly'

    def items(self):
        return Chapter.objects.order_by('id')

    def location(self, obj):
        return f'/chapter/{obj.slug}/'

class SubChapterSitemap(Sitemap):
    priority = 0.6
    changefreq = 'weekly'

    def items(self):
        return SubChapter.objects.order_by('id')

    def location(self, obj):
        return f'/mcq/{obj.slug}/'

class SolutionSetSitemap(Sitemap):
    priority = 0.6
    changefreq = 'monthly'

    def items(self):
        return SolutionSet.objects.select_related('chapter').order_by('id')

    def location(self, obj):
        return f'/chapter/{obj.chapter.slug}/solved-set/{obj.set_number}/'


class BlogSitemap(Sitemap):
    priority = 0.7
    changefreq = 'monthly'

    def items(self):
        from CEE_Quiz.views import BLOG_POST_ORDER
        return BLOG_POST_ORDER

    def location(self, obj):
        return f'/blog/{obj}/'

    def lastmod(self, obj):
        import datetime

        from CEE_Quiz.views import BLOG_PUBLISH_DATES
        raw = BLOG_PUBLISH_DATES.get(obj)
        if not raw:
            return None
        return datetime.date(*raw)
sitemaps = {
    "static": StaticViewSitemap,
    "subjects": SubjectSitemap,
    "chapters": ChapterSitemap,
    "subchapters": SubChapterSitemap,
    "solution_sets": SolutionSetSitemap,
    "blog": BlogSitemap,
}