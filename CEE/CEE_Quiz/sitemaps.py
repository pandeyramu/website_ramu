from django.contrib.sitemaps import Sitemap
from django.urls import reverse

from CEE_Quiz.models import Subject, Chapter, SubChapter


class StaticViewSitemap(Sitemap):
    priority = 0.9
    changefreq = "weekly"

    def items(self):
        return [
            "home",
            "full_test",
            "all_subjects",
            "all_mcq",
            "about",
            "contact",
            "privacy_policy",
            "disclaimer",
            "blog_index",
            "blog_how_to_prepare_for_cee",
            "blog_human_biology_cee_questions",
            "blog_organic_chemistry_cee_tips",
            "blog_physics_high_weightage_topics",
            "blog_mat_section_tips",
            "blog_cee_exam_day_strategy",
            "blog_chapter_wise_marks_distribution",
            "blog_last_30_days_cee_prep_plan",
            "blog_how_to_remember_organic_reactions",
        ]

    def location(self, item):
        return reverse(item)


class SubjectSitemap(Sitemap):
    priority = 0.8
    changefreq = "weekly"

    def items(self):
        return Subject.objects.order_by("id")

    def location(self, item):
        return reverse("chapters", args=[item.slug])


class ChapterSitemap(Sitemap):
    priority = 0.7
    changefreq = "weekly"

    def items(self):
        return Chapter.objects.order_by("id")

    def location(self, item):
        return reverse("quiz", args=[item.slug])


class SubChapterSitemap(Sitemap):
    priority = 0.6
    changefreq = "weekly"

    def items(self):
        return SubChapter.objects.order_by("id")

    def location(self, item):
        return reverse("subchapter_quiz", args=[item.slug])


class SubjectAliasSitemap(Sitemap):
    priority = 0.9
    changefreq = "weekly"

    def items(self):
        return Subject.objects.order_by("id")

    def location(self, item):
        return reverse("dynamic_page", args=[f"{item.slug}-mcq"])


sitemaps = {
    "static": StaticViewSitemap,
    "subjects": SubjectSitemap,
    "subject_aliases": SubjectAliasSitemap,
    "chapters": ChapterSitemap,
    "subchapters": SubChapterSitemap,
}