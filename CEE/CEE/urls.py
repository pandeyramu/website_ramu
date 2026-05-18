"""
URL configuration for CEE project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.contrib.sitemaps.views import sitemap
from django.views.generic import TemplateView
from django.urls import path
from CEE_Quiz import views
from CEE_Quiz.sitemaps import sitemaps

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # Keepalive endpoint for Render free tier
    path('keepalive/', views.keepalive, name='keepalive'),
    path('report-question/', views.report_question, name='report_question'),
    
    # Main app URLs
    path('', views.home, name='home'),
    # Slug-based SEO-friendly URLs
    path('subject/<slug:slug>/', views.chapters, name='chapters'),
    path('chapter/<slug:slug>/', views.quiz, name='quiz'),
    path('chapter/<slug:slug>/subchapters/', views.subchapters, name='subchapters'),
    path('mcq/<slug:slug>/', views.subchapter_quiz, name='subchapter_quiz'),
    # Backwards-compatible redirects for old numeric URLs (301)
    path('subject/<int:subject_id>/', views.chapters_redirect),
    path('chapter/<int:chapter_id>/', views.quiz_redirect),
    path('chapter/<int:chapter_id>/subchapters/', views.subchapters_redirect),
    path('subchapter/<int:subchapter_id>/quiz/', views.subchapter_quiz_redirect),
    path('quiz/<slug:slug>/', views.subchapter_quiz_legacy_redirect),
    path('full-test/', views.full_test, name='full_test'),
    path('full-test/results/', views.full_test_results, name='full_test_results'),
    path('privacy/', views.privacy_policy_redirect, name='privacy'),
    path('privacy-policy/', views.privacy_policy_page, name='privacy_policy'),
    path('privacy-policy-old/', views.privacy_policy, name='privacy_policy_old'),
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),
    path('disclaimer/', views.disclaimer, name='disclaimer'),
    path('blog/', views.blog_index, name='blog_index'),
    path('blog/how-to-prepare-for-cee/', views.blog_post, {'slug': 'how-to-prepare-for-cee'}, name='blog_how_to_prepare_for_cee'),
    path('blog/human-biology-cee-questions/', views.blog_post, {'slug': 'human-biology-cee-questions'}, name='blog_human_biology_cee_questions'),
    path('blog/organic-chemistry-cee-tips/', views.blog_post, {'slug': 'organic-chemistry-cee-tips'}, name='blog_organic_chemistry_cee_tips'),
    path('blog/physics-high-weightage-topics/', views.blog_post, {'slug': 'physics-high-weightage-topics'}, name='blog_physics_high_weightage_topics'),
    path('blog/mat-section-tips/', views.blog_post, {'slug': 'mat-section-tips'}, name='blog_mat_section_tips'),
    path('blog/cee-exam-day-strategy/', views.blog_post, {'slug': 'cee-exam-day-strategy'}, name='blog_cee_exam_day_strategy'),
    path('blog/<slug:slug>/', views.blog_post, name='blog_post'),
    
    # SEO files
    path("robots.txt", TemplateView.as_view(
        template_name="robots.txt",
        content_type="text/plain"
    )),
    path("sitemap.xml", sitemap, {"sitemaps": sitemaps}, name="sitemap"),
    path("ads.txt", views.ads_txt, name="ads_txt"),
]