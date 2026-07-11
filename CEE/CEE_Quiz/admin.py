from django.contrib import admin
from .models import Subject, Chapter, SubChapter, Question, TestResult, PageSEO, SolutionSet


class SubjectAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'slug', 'has_intro')
    prepopulated_fields = {'slug': ('name',)}
    fields = ('name', 'slug', 'intro_text')

    @admin.display(description='Has Intro', boolean=True)
    def has_intro(self, obj):
        return bool(obj.intro_text)


class SubChapterInline(admin.TabularInline):
    model = SubChapter
    extra = 1
    ordering = ['order']
    fields = ('name', 'order', 'slug', 'seo_description')


class ChapterAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'slug', 'subject', 'has_subchapters', 'has_intro')
    list_filter = ('subject', 'has_subchapters')
    search_fields = ('name',)
    inlines = [SubChapterInline]
    prepopulated_fields = {'slug': ('name',)}
    fields = ('subject', 'name', 'slug', 'has_subchapters', 'intro_text')

    @admin.display(description='Has Intro', boolean=True)
    def has_intro(self, obj):
        return bool(obj.intro_text)


class SubChapterAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'slug', 'chapter', 'order', 'has_intro')
    list_filter = ('chapter__subject', 'chapter')
    ordering = ['chapter', 'order']
    prepopulated_fields = {'slug': ('name',)}
    fields = ('chapter', 'name', 'order', 'slug', 'seo_description', 'intro_text')

    @admin.display(description='Has Intro', boolean=True)
    def has_intro(self, obj):
        return bool(obj.intro_text)


class PageSEOAdmin(admin.ModelAdmin):
    list_display = ['page_slug', 'meta_title']
    search_fields = ['page_slug']


class QuestionAdmin(admin.ModelAdmin):
    list_display = ('id', 'subject_name', 'chapter', 'sub_chapter', 'question_preview', 'correct_option')
    list_filter = ('chapter__subject', 'chapter', 'sub_chapter', 'correct_option')
    search_fields = ('question_text', 'id')
    list_select_related = ('chapter', 'sub_chapter', 'chapter__subject')
    show_full_result_count = False
    list_per_page = 50
    list_max_show_all = 200
    ordering = ('-id',)
    readonly_fields = ('question_text', 'option_a', 'option_b', 'option_c', 'option_d', 'correct_option', 'solution')
    fieldsets = (
        ('Question Details', {
            'fields': ('question_text', 'solution')
        }),
        ('Options', {
            'fields': ('option_a', 'option_b', 'option_c', 'option_d', 'correct_option')
        }),
        ('Classification', {
            'fields': ('chapter', 'sub_chapter')
        }),
    )

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

    @admin.display(description='Subject', ordering='chapter__subject__name')
    def subject_name(self, obj):
        return obj.chapter.subject.name

    @admin.display(description='Question')
    def question_preview(self, obj):
        text = (obj.question_text or '').strip()
        if not text:
            return '-'
        return text[:160] + ('...' if len(text) > 160 else '')

class SolutionSetAdmin(admin.ModelAdmin):
    list_display = ('id', 'chapter', 'set_number', 'title', 'question_count')
    list_filter = ('chapter__subject', 'chapter')
    search_fields = ('title', 'chapter__name')
    autocomplete_fields = ('chapter',)

    @admin.display(description='Questions')
    def question_count(self, obj):
        ids = [x.strip() for x in obj.question_ids.split(',') if x.strip().isdigit()]
        return len(ids)


class UserAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'topic', 'score', 'total_attempted', 'total_correct', 'time_taken_seconds', 'created_at')


admin.site.register(Subject, SubjectAdmin)
admin.site.register(Chapter, ChapterAdmin)
admin.site.register(SubChapter, SubChapterAdmin)
admin.site.register(Question, QuestionAdmin)
admin.site.register(TestResult, UserAdmin)
admin.site.register(PageSEO, PageSEOAdmin)
admin.site.register(SolutionSet, SolutionSetAdmin)
