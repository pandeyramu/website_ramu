from django.db import migrations


def update_full_test_seo(apps, schema_editor):
    PageSEO = apps.get_model('CEE_Quiz', 'PageSEO')
    PageSEO.objects.update_or_create(
        page_slug='full-test',
        defaults={
            'meta_title': 'CEE Full Mock Test – 200 Questions Online | CEE MCQ',
            'meta_description': 'Take a full CEE mock test online with 200 questions, negative marking, and a 3 hour timer. Simulate the real MEC entrance exam experience.',
            'meta_keywords': 'CEE full test, CEE mock test Nepal, CEE online test, MEC full mock test, CEE 200 questions, CEE practice exam',
            'og_title': 'CEE Full Mock Test – 200 Questions Online | CEE MCQ',
            'og_description': 'Take a full CEE mock test online with 200 questions, negative marking, and a 3 hour timer.',
        },
    )


def reverse_full_test_seo(apps, schema_editor):
    PageSEO = apps.get_model('CEE_Quiz', 'PageSEO')
    PageSEO.objects.update_or_create(
        page_slug='full-test',
        defaults={
            'meta_title': 'CEE Full Mock Test – 180 Questions Online | CEE MCQ',
            'meta_description': 'Take a full CEE mock test online with 180 questions, negative marking, and a 2.5-hour timer. Simulate the real MEC entrance exam experience.',
            'meta_keywords': 'CEE full test, CEE mock test Nepal, CEE online test, MEC full mock test, CEE 180 questions, CEE practice exam',
            'og_title': 'CEE Full Mock Test – 180 Questions Online | CEE MCQ',
            'og_description': 'Take a full CEE mock test online with 180 questions, negative marking, and a 2.5-hour timer.',
        },
    )


class Migration(migrations.Migration):

    dependencies = [
        ('CEE_Quiz', '0016_remove_dashes_from_intro_texts'),
    ]

    operations = [
        migrations.RunPython(update_full_test_seo, reverse_full_test_seo),
    ]
