from django.db import models
from django.utils.text import slugify


class Subject(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=150, unique=True, blank=True, null=True)
    intro_text = models.TextField(blank=True, help_text='150-300 word intro for the subject page')

    def __str__(self):
        return self.name
    def save(self, *args, **kwargs):
        if not self.slug:
            base = slugify(self.name) or 'subject'
            slug = base
            counter = 1
            while Subject.objects.filter(slug=slug).exclude(pk=getattr(self, 'pk', None)).exists():
                slug = f"{base}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)


class Chapter(models.Model):
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    has_subchapters = models.BooleanField(default=False)
    slug = models.SlugField(max_length=150, unique=True, blank=True, null=True)
    intro_text = models.TextField(blank=True, help_text='150-300 word intro for the chapter page')

    def __str__(self):
        return f"{self.subject.name} - {self.name}"

    def save(self, *args, **kwargs):
        if not self.slug:
            base = slugify(self.name) or 'chapter'
            slug = base
            counter = 1
            while Chapter.objects.filter(slug=slug).exclude(pk=getattr(self, 'pk', None)).exists():
                slug = f"{base}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)


class PageSEO(models.Model):
    page_slug = models.CharField(max_length=100, unique=True)
    meta_title = models.CharField(max_length=70)
    meta_description = models.CharField(max_length=160)
    meta_keywords = models.TextField()
    og_title = models.CharField(max_length=70, blank=True)
    og_description = models.CharField(max_length=160, blank=True)

    def __str__(self):
        return f"{self.page_slug} - {self.meta_title}"


class SubChapter(models.Model):
    chapter = models.ForeignKey(Chapter, on_delete=models.CASCADE, related_name='subchapters')
    name = models.CharField(max_length=200)
    order = models.PositiveIntegerField(default=0)
    slug = models.SlugField(max_length=200, unique=True, blank=True, null=True)
    seo_description = models.TextField(blank=True)
    intro_text = models.TextField(blank=True, help_text='150-300 word intro for the subchapter page')

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"{self.chapter.name} - {self.name}"

    def save(self, *args, **kwargs):
        if not self.slug:
            base = slugify(self.name) or 'subchapter'
            slug = base
            counter = 1
            while SubChapter.objects.filter(slug=slug).exclude(pk=getattr(self, 'pk', None)).exists():
                slug = f"{base}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)


class Question(models.Model):
    chapter = models.ForeignKey(Chapter, on_delete=models.CASCADE)
    sub_chapter = models.ForeignKey(SubChapter, on_delete=models.CASCADE, null=True, blank=True, related_name='questions')
    question_text = models.TextField()
    solution = models.TextField(blank=True, default='')
    option_a = models.CharField(max_length=255)
    option_b = models.CharField(max_length=255)
    option_c = models.CharField(max_length=255)
    option_d = models.CharField(max_length=255)
    correct_option = models.CharField(max_length=255, choices=[('A', 'A'), ('B', 'B'), ('C', 'C'), ('D', 'D')])

    def __str__(self):
        if self.sub_chapter:
            return f"{self.sub_chapter.name} - {self.question_text[:50]}"
        return f"{self.chapter.name} - {self.question_text[:50]}"


class TestResult(models.Model):
    name = models.CharField(max_length=100)
    topic = models.CharField(max_length=200)
    score = models.FloatField()
    total_attempted = models.IntegerField()
    total_correct = models.IntegerField(default=0)
    time_taken_seconds = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} -{self.topic} - {self.score}"
class SolutionSet(models.Model):
    chapter = models.ForeignKey(Chapter, on_delete=models.CASCADE, related_name='solution_sets')
    set_number = models.PositiveIntegerField()
    title = models.CharField(max_length=200, blank=True, default='')
    intro_text = models.TextField(blank=True, help_text='3-5 sentence intro describing what topics this batch covers')
    question_ids = models.TextField(help_text='Comma-separated list of question IDs in this set')

    class Meta:
        unique_together = ['chapter', 'set_number']
        ordering = ['chapter', 'set_number']

    def __str__(self):
        return f"{self.chapter.name} - Set {self.set_number}"

    def get_questions(self):
        ids = [int(x.strip()) for x in self.question_ids.split(',') if x.strip().isdigit()]
        questions = Question.objects.filter(id__in=ids).select_related('chapter', 'sub_chapter')
        id_map = {q.id: q for q in questions}
        return [id_map[qid] for qid in ids if qid in id_map]


class QuestionReport(models.Model):
    question_id = models.IntegerField()
    user_name = models.CharField(max_length=100, blank=True)
    attempt_reference = models.CharField(max_length=100, blank=True)
    topic = models.CharField(max_length=200, blank=True)
    reason = models.TextField()
    question_text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['question_id', 'attempt_reference'],
                name='unique_question_report_per_attempt'
            )
        ]