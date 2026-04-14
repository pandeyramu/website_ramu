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
    list_display = ('id', 'chapter', 'sub_chapter', 'question_preview', 'correct_option')
    list_filter = ('chapter',)
    search_fields = ('id',)
    list_select_related = ('chapter', 'sub_chapter', 'chapter__subject')
    show_full_result_count = False
    list_per_page = 25
    list_max_show_all = 100
    ordering = ('id',)

    def get_queryset(self, request):
        # Keep changelist queries lightweight for large question tables.
        qs = super().get_queryset(request)
        return qs.select_related('chapter', 'sub_chapter', 'chapter__subject').only(
            'id',
            'correct_option',
            'question_text',
            'chapter__name',
            'chapter__subject__name',
            'sub_chapter__name',
        )

    @admin.display(description='Question')
    def question_preview(self, obj):
        text = (obj.question_text or '').strip()
        if not text:
            return '-'
        return text[:160] + ('...' if len(text) > 160 else '')

class UserAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'topic', 'score', 'total_attempted', 'created_at')


admin.site.register(Subject, SubjectAdmin)
admin.site.register(Chapter, ChapterAdmin)
admin.site.register(SubChapter, SubChapterAdmin)
admin.site.register(Question, QuestionAdmin)
admin.site.register(TestResult, UserAdmin)
