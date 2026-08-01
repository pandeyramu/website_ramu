from django.db import migrations

REPLACEMENTS = [
    (' \u2014 ', ', '),
    ('\u2014', ', '),
    (' \u2013 ', ' | '),
    ('chapter-wise', 'chapter wise'),
    ('step-by-step', 'step by step'),
    ('full-length', 'full length'),
    ('high-weightage', 'high weightage'),
    ('highest-weightage', 'highest weightage'),
    ('low-weightage', 'low weightage'),
    ('2.5-hour', '2.5 hour'),
    ('200-question', '200 question'),
    ('180-question', '180 question'),
    ('3-hour', '3 hour'),
    ('sub-topic', 'sub topic'),
    ('multiple-choice', 'multiple choice'),
    ('per-question', 'per question'),
]


def clean_text(value):
    if not value:
        return value
    for old, new in REPLACEMENTS:
        value = value.replace(old, new)
    return value


def clean_intro_texts(apps, schema_editor):
    Subject = apps.get_model('CEE_Quiz', 'Subject')
    Chapter = apps.get_model('CEE_Quiz', 'Chapter')
    SubChapter = apps.get_model('CEE_Quiz', 'SubChapter')

    changed = 0
    for obj in Subject.objects.all():
        if clean_text(obj.intro_text) != obj.intro_text:
            obj.intro_text = clean_text(obj.intro_text)
            obj.save(update_fields=['intro_text'])
            changed += 1

    for obj in Chapter.objects.all():
        if clean_text(obj.intro_text) != obj.intro_text:
            obj.intro_text = clean_text(obj.intro_text)
            obj.save(update_fields=['intro_text'])
            changed += 1

    for obj in SubChapter.objects.all():
        updated = False
        if clean_text(obj.intro_text) != obj.intro_text:
            obj.intro_text = clean_text(obj.intro_text)
            updated = True
        if obj.seo_description and clean_text(obj.seo_description) != obj.seo_description:
            obj.seo_description = clean_text(obj.seo_description)
            updated = True
        if updated:
            obj.save(update_fields=['intro_text', 'seo_description'])
            changed += 1

    print(f'Cleaned intro/seo text on {changed} records')


class Migration(migrations.Migration):

    dependencies = [
        ('CEE_Quiz', '0015_reseed_corrected_intro_texts'),
    ]

    operations = [
        migrations.RunPython(clean_intro_texts, migrations.RunPython.noop),
    ]
