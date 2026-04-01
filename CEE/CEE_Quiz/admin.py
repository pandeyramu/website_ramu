from django.contrib import admin
from .models import Subject, Chapter, SubChapter, Question, TestResult


class SubjectAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')


class SubChapterInline(admin.TabularInline):
    model = SubChapter
    extra = 1
    ordering = ['order']


class ChapterAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'subject', 'has_subchapters')
    list_filter = ('subject', 'has_subchapters')
    inlines = [SubChapterInline]


class SubChapterAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'chapter', 'order')
    list_filter = ('chapter__subject', 'chapter')
    ordering = ['chapter', 'order']


class QuestionAdmin(admin.ModelAdmin):
    list_display = ('id', 'chapter', 'sub_chapter', 'question_text', 'correct_option', 'solution_preview')
    list_filter = ('chapter__subject', 'chapter', 'sub_chapter')
    search_fields = ('question_text', 'solution')

    @admin.display(description='Solution')
    def solution_preview(self, obj):
        text = (obj.solution or '').strip()
        if not text:
            return '-'
        return text[:120] + ('...' if len(text) > 120 else '')


class UserAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'topic', 'score', 'total_attempted', 'created_at')


admin.site.register(Subject, SubjectAdmin)
admin.site.register(Chapter, ChapterAdmin)
admin.site.register(SubChapter, SubChapterAdmin)
admin.site.register(Question, QuestionAdmin)
admin.site.register(TestResult, UserAdmin)
