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
    path('', views.home , name='home' ),
    path('subject/<int:subject_id>/' , views.chapters,name='chapters' ),
    path('chapter/<int:chapter_id>/' , views.quiz , name= 'quiz'),
    path('full-test/', views.full_test, name='full_test'),
     path("robots.txt", TemplateView.as_view(
        template_name="robots.txt",
        content_type="text/plain"
    )),

    # Serve sitemap.xml
    path("sitemap.xml", TemplateView.as_view(
        template_name="sitemap.xml",
        content_type="application/xml"
    )),
]
