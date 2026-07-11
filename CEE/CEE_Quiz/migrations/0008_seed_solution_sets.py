from django.db import migrations


def seed_solution_sets(apps, schema_editor):
    Chapter = apps.get_model('CEE_Quiz', 'Chapter')
    Question = apps.get_model('CEE_Quiz', 'Question')
    SolutionSet = apps.get_model('CEE_Quiz', 'SolutionSet')

    SETS_PER_CHAPTER = 5

    for chapter in Chapter.objects.all().order_by('subject__name', 'name'):
        qids = list(Question.objects.filter(chapter=chapter).order_by('id').values_list('id', flat=True))
        if not qids:
            continue
        SolutionSet.objects.filter(chapter=chapter).delete()
        total = len(qids)
        set_size = max(1, total // SETS_PER_CHAPTER)
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


def delete_solution_sets(apps, schema_editor):
    SolutionSet = apps.get_model('CEE_Quiz', 'SolutionSet')
    SolutionSet.objects.all().delete()


class Migration(migrations.Migration):

    dependencies = [
        ('CEE_Quiz', '0007_subchapter_intro_text'),
    ]

    operations = [
        migrations.RunPython(seed_solution_sets, delete_solution_sets),
    ]
