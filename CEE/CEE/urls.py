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
from django.views.generic import TemplateView
from django.urls import path
from CEE_Quiz import views

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # Keepalive endpoint for Render free tier
    path('keepalive/', views.keepalive, name='keepalive'),
    path('report-question/', views.report_question, name='report_question'),
    
    # Main app URLs
    path('', views.home, name='home'),
    path('subject/<int:subject_id>/', views.chapters, name='chapters'),
    path('chapter/<int:chapter_id>/', views.quiz, name='quiz'),
    path('chapter/<int:chapter_id>/subchapters/', views.subchapters, name='subchapters'),
    path('subchapter/<int:subchapter_id>/quiz/', views.subchapter_quiz, name='subchapter_quiz'),
    path('full-test/', views.full_test, name='full_test'),
    path('privacy/', views.privacy_policy, name='privacy'),
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
    path("sitemap.xml", TemplateView.as_view(
        template_name="sitemap.xml",
        content_type="application/xml"
    )),
    path("ads.txt", TemplateView.as_view(
    template_name="ads.txt",
    content_type="text/plain"
    )),
]