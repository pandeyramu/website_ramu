from django.db import models


class Subject(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Chapter(models.Model):
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    has_subchapters = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.subject.name} - {self.name}"


class SubChapter(models.Model):
    chapter = models.ForeignKey(Chapter, on_delete=models.CASCADE, related_name='subchapters')
    name = models.CharField(max_length=200)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"{self.chapter.name} - {self.name}"


class Question(models.Model):
    chapter = models.ForeignKey(Chapter, on_delete=models.CASCADE)
    sub_chapter = models.ForeignKey(SubChapter, on_delete=models.CASCADE, null=True, blank=True, related_name='questions')
    question_text = models.TextField()
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
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} -{self.topic} - {self.score}"