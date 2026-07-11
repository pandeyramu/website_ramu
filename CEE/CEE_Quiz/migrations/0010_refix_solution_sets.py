import random

from django.db import migrations


def refix_solution_sets(apps, schema_editor):
    Chapter = apps.get_model('CEE_Quiz', 'Chapter')
    Question = apps.get_model('CEE_Quiz', 'Question')
    SolutionSet = apps.get_model('CEE_Quiz', 'SolutionSet')

    SETS_PER_CHAPTER = 5
    QUESTIONS_PER_SET = 20

    for chapter in Chapter.objects.all().order_by('subject__name', 'name'):
        qids = list(Question.objects.filter(chapter=chapter).values_list('id', flat=True))
        if not qids:
            continue
        # Delete old sets that had too many questions
        SolutionSet.objects.filter(chapter=chapter).delete()

        indices = list(range(len(qids)))
        random.shuffle(indices)

        for i in range(SETS_PER_CHAPTER):
            start = i * QUESTIONS_PER_SET
            selected_indices = indices[start:start + QUESTIONS_PER_SET]
            if not selected_indices:
                continue
            ids_subset = [qids[idx] for idx in selected_indices]

            SolutionSet.objects.create(
                chapter=chapter,
                set_number=i + 1,
                title=f"Set {i+1}",
                intro_text=(
                    f"Solved question set {i+1} of {SETS_PER_CHAPTER} for {chapter.name}. "
                    f"Each set contains {len(selected_indices)} randomly selected questions "
                    f"with step-by-step solutions to help you understand every concept clearly."
                ),
                question_ids=','.join(str(x) for x in ids_subset)
            )


class Migration(migrations.Migration):

    dependencies = [
        ('CEE_Quiz', '0009_seed_intro_texts'),
    ]

    operations = [
        migrations.RunPython(refix_solution_sets),
    ]
