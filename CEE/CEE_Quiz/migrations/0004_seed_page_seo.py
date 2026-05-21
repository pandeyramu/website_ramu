from django.db import migrations


def seed_page_seo(apps, schema_editor):
    PageSEO = apps.get_model('CEE_Quiz', 'PageSEO')

    seed_data = [
        {
            'page_slug': 'home',
            'meta_title': 'CEE MCQ – Free CEE Practice Questions Nepal | MEC Entrance Exam',
            'meta_description': "Practice free CEE MCQ questions chapter-wise. Physics, Chemistry, Biology, MAT for Nepal's MEC medical entrance exam. 47,000+ questions with solutions.",
            'meta_keywords': 'CEE MCQ, CEE Nepal, CEE questions, MEC entrance exam, MBBS entrance Nepal, CEE practice test, chapter wise CEE MCQ, free CEE questions',
        },
        {
            'page_slug': 'physics',
            'meta_title': 'CEE Physics MCQ Questions – Chapter Wise | CEE MCQ',
            'meta_description': "Practice chapter-wise CEE Physics MCQ questions covering Mechanics, Thermodynamics, Optics, Electricity, and Modern Physics for Nepal's CEE entrance exam.",
            'meta_keywords': 'CEE Physics MCQ, CEE Physics questions, Physics MCQ Nepal, CEE Mechanics MCQ, CEE Modern Physics, MEC Physics practice',
        },
        {
            'page_slug': 'chemistry',
            'meta_title': 'CEE Chemistry MCQ Questions – Chapter Wise | CEE MCQ',
            'meta_description': "Practice CEE Chemistry MCQ questions chapter-wise. Covers Physical, Organic, Inorganic and Applied Chemistry for Nepal's MEC entrance exam.",
            'meta_keywords': 'CEE Chemistry MCQ, CEE Organic Chemistry, CEE Physical Chemistry, Chemistry MCQ Nepal, MEC Chemistry questions',
        },
        {
            'page_slug': 'zoology',
            'meta_title': 'CEE Zoology MCQ Questions – Chapter Wise | CEE MCQ',
            'meta_description': "Practice CEE Zoology MCQ questions on Human Physiology, Animal Diversity, Microbiology and more for Nepal's MEC entrance exam.",
            'meta_keywords': 'CEE Zoology MCQ, CEE Biology MCQ, Human Physiology MCQ Nepal, CEE Zoology questions, MEC Zoology practice',
        },
        {
            'page_slug': 'botany',
            'meta_title': 'CEE Botany MCQ Questions – Chapter Wise | CEE MCQ',
            'meta_description': "Practice CEE Botany MCQ questions covering Plant Physiology, Genetics, Cell Biology, Biodiversity and more for Nepal's MEC entrance exam.",
            'meta_keywords': 'CEE Botany MCQ, CEE Plant Physiology MCQ, CEE Genetics MCQ, Botany MCQ Nepal, MEC Botany questions',
        },
        {
            'page_slug': 'full-test',
            'meta_title': 'CEE Full Mock Test – 180 Questions Online | CEE MCQ',
            'meta_description': 'Take a full CEE mock test online with 180 questions, negative marking, and a 2.5-hour timer. Simulate the real MEC entrance exam experience.',
            'meta_keywords': 'CEE full test, CEE mock test Nepal, CEE online test, MEC full mock test, CEE 180 questions, CEE practice exam',
        },
    ]

    for item in seed_data:
        PageSEO.objects.update_or_create(
            page_slug=item['page_slug'],
            defaults={
                'meta_title': item['meta_title'],
                'meta_description': item['meta_description'],
                'meta_keywords': item['meta_keywords'],
                'og_title': item['meta_title'],
                'og_description': item['meta_description'],
            },
        )


def unseed_page_seo(apps, schema_editor):
    PageSEO = apps.get_model('CEE_Quiz', 'PageSEO')
    PageSEO.objects.filter(page_slug__in=['home', 'physics', 'chemistry', 'zoology', 'botany', 'full-test']).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('CEE_Quiz', '0003_pageseo_subchapter_seo_description'),
    ]

    operations = [
        migrations.RunPython(seed_page_seo, unseed_page_seo),
    ]