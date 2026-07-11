from django.db import migrations

# Standard closing paragraph appended to every chapter/subchapter description so that
# all pages carry consistent, substantial (non-thin) intro text. The per-topic opening
# sentence is preserved from the existing intro_text, so each description stays specific.
CLOSING = (
    " Practising these MCQs with the detailed, step-by-step solutions provided on this site helps you build a "
    "clear understanding of the underlying concepts and improves both accuracy and speed. Because the CEE "
    "frequently frames application-based questions rather than direct recall, focus on understanding principles "
    "instead of rote memorisation. A steady, chapter-wise practice routine with regular review of mistakes is "
    "the most reliable way to strengthen this area and score well in the entrance exam."
)

MARKER = "steady, chapter-wise practice routine"


def expand(text, name, subject_name):
    if not text or not text.strip():
        text = "%s is an important part of the CEE %s syllabus." % (name, subject_name)
    text = text.strip()
    if MARKER in text:
        return text
    if not text.endswith('.'):
        text += '.'
    return (text + CLOSING).strip()


def expand_intro_texts(apps, schema_editor):
    Chapter = apps.get_model('CEE_Quiz', 'Chapter')
    SubChapter = apps.get_model('CEE_Quiz', 'SubChapter')

    for chap in Chapter.objects.all():
        subject_name = chap.subject.name if chap.subject else ''
        if chap.intro_text:
            chap.intro_text = expand(chap.intro_text, chap.name, subject_name)
            chap.save(update_fields=['intro_text'])

    for sub in SubChapter.objects.all():
        chapter_name = sub.chapter.name if sub.chapter else ''
        subject_name = ''
        if sub.chapter and sub.chapter.subject:
            subject_name = sub.chapter.subject.name
        if sub.intro_text:
            sub.intro_text = expand(sub.intro_text, sub.name, subject_name)
            sub.save(update_fields=['intro_text'])


def reverse_expand(apps, schema_editor):
    # Best-effort reversal: strip the appended closing paragraph.
    Chapter = apps.get_model('CEE_Quiz', 'Chapter')
    SubChapter = apps.get_model('CEE_Quiz', 'SubChapter')
    for chap in Chapter.objects.all():
        if chap.intro_text and MARKER in chap.intro_text:
            chap.intro_text = chap.intro_text.split(CLOSING)[0].strip()
            chap.save(update_fields=['intro_text'])
    for sub in SubChapter.objects.all():
        if sub.intro_text and MARKER in sub.intro_text:
            sub.intro_text = sub.intro_text.split(CLOSING)[0].strip()
            sub.save(update_fields=['intro_text'])


class Migration(migrations.Migration):

    dependencies = [
        ('CEE_Quiz', '0010_refix_solution_sets'),
    ]

    operations = [
        migrations.RunPython(expand_intro_texts, reverse_expand),
    ]
