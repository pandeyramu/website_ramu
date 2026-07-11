"""
Run on live server: python create_solution_sets_live.py
Creates 5 solution sets per chapter with properly chunked question IDs.
"""
import os, sys
os.environ['DJANGO_SECRET_KEY'] = 'override-this-in-production'
os.environ['DJANGO_DEBUG'] = 'True'
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'CEE.settings')

import django
django.setup()

from CEE_Quiz.models import Chapter, Question, SolutionSet

SETS_PER_CHAPTER = 5

for chapter in Chapter.objects.all().order_by('subject__name', 'name'):
    qids = list(Question.objects.filter(chapter=chapter).order_by('id').values_list('id', flat=True))
    if not qids:
        print(f'SKIP {chapter.subject.name} > {chapter.name}: no questions')
        continue
    SolutionSet.objects.filter(chapter=chapter).delete()
    total = len(qids)
    set_size = max(1, total // SETS_PER_CHAPTER)
    print(f'{chapter.subject.name} > {chapter.name}: {total} questions -> {SETS_PER_CHAPTER} sets')
    for i in range(SETS_PER_CHAPTER):
        start = i * set_size
        end = (i + 1) * set_size if i < SETS_PER_CHAPTER - 1 else total
        ids_subset = qids[start:end]
        if not ids_subset:
            continue
        SolutionSet.objects.create(
            chapter=chapter,
            set_number=i + 1,
            title=f"Set {i+1}",
            intro_text=f"Solved question set {i+1} of {SETS_PER_CHAPTER} for {chapter.name}.",
            question_ids=','.join(str(x) for x in ids_subset)
        )
print(f'\nDone! Total: {SolutionSet.objects.count()} solution sets.')
