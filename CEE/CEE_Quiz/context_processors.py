from types import SimpleNamespace

from .models import Chapter, PageSEO, SubChapter, Subject
from .seo_provider import get_supabase_page_seo


SITE_NAME = 'CEE MCQ'


def _defaults(*, title, description, keywords, og_title='', og_description=''):
    return SimpleNamespace(
        page_slug='',
        meta_title=title,
        meta_description=description,
        meta_keywords=keywords,
        og_title=og_title or title,
        og_description=og_description or description,
    )


def _home_defaults():
    return _defaults(
        title=f'{SITE_NAME} – Free Practice Questions | {SITE_NAME}',
        description='Free CEE MCQ practice. Chapter-wise MCQ questions in Biology, Chemistry, Physics and MAT for Nepal\'s Common Entrance Examination.',
        keywords='CEE MCQ, CEE Nepal, Chapter-wise MCQ Questions, Biology, Chemistry, Physics, MAT',
        og_title=f'{SITE_NAME} – Free CEE MCQ Questions',
        og_description='Free CEE entrance MCQ practice. Chapter-wise MCQ questions in Biology, Chemistry, Physics and MAT for Nepal\'s Common Entrance Examination.',
    )


def _subject_defaults(subject_name):
    return _defaults(
        title=f'CEE {subject_name} MCQ Questions – Chapter Wise | {SITE_NAME}',
        description=f'Practice chapter-wise CEE {subject_name} MCQ questions and prepare for Nepal\'s Common Entrance Examination.',
        keywords=f'CEE {subject_name} MCQ, {subject_name} MCQ Nepal, CEE Nepal, Chapter-wise Questions',
        og_title=f'{subject_name} Chapters | {SITE_NAME}',
        og_description=f'Practice chapter-wise MCQ questions for {subject_name}. Prepare for Nepal\'s Common Entrance Examination.',
    )


def _chapter_quiz_defaults(chapter_name, subject_name):
    return _defaults(
        title=f'{chapter_name} MCQ – {subject_name} | {SITE_NAME}',
        description=f'Practice the {chapter_name} MCQ for the Common Entrance Examination. Track your performance with detailed results.',
        keywords=f'CEE MCQ, {chapter_name} MCQ, {subject_name}, Chapter-wise Questions, Online Practice',
        og_title=f'{chapter_name} MCQ – {subject_name} | {SITE_NAME}',
        og_description=f'Practice the {chapter_name} MCQ for the Common Entrance Examination. Track your performance with detailed results.',
    )


def _subchapter_quiz_defaults(subchapter_name, chapter_name):
    return _defaults(
        title=f'{subchapter_name} MCQ – {chapter_name} | {SITE_NAME}',
        description=f'Practice the {subchapter_name} MCQ from {chapter_name} for the Common Entrance Examination. Track your performance with detailed results.',
        keywords=f'CEE MCQ, {subchapter_name} MCQ, {chapter_name} MCQ, Chapter-wise Questions, Online Practice',
        og_title=f'{subchapter_name} MCQ – {chapter_name} | {SITE_NAME}',
        og_description=f'Practice the {subchapter_name} MCQ from {chapter_name} for the Common Entrance Examination. Track your performance with detailed results.',
    )


def _full_test_defaults():
    return _defaults(
        title='CEE Full Mock Test – 180 Questions Online | CEE MCQ',
        description='Take a full CEE mock test online with 180 questions, negative marking, and a 2.5-hour timer. Simulate the real MEC entrance exam experience.',
        keywords='CEE full test, CEE mock test Nepal, CEE online test, MEC full mock test, CEE 180 questions, CEE practice exam',
        og_title='CEE Full Mock Test – 180 Questions Online | CEE MCQ',
        og_description='Take a full CEE mock test online with 180 questions, negative marking, and a 2.5-hour timer.',
    )


def _about_defaults():
    return _defaults(
        title='About Us | CEE MCQ',
        description='Learn about CEE MCQ, a free Nepali CEE practice platform created for students who want chapter-wise MCQs, exam tips, and better revision habits.',
        keywords='CEE MCQ, About Us, Nepal CEE practice, exam tips',
        og_title='About Us | CEE MCQ',
        og_description='CEE MCQ is a free CEE practice platform for Nepali students with chapter-wise MCQs, full tests, and study resources.',
    )


def _contact_defaults():
    return _defaults(
        title='Contact | CEE MCQ',
        description='Contact CEE MCQ for support, feedback, or website questions. Use the form or email provided on this page.',
        keywords='CEE MCQ, Contact, support, feedback',
        og_title='Contact | CEE MCQ',
        og_description='Contact CEE MCQ for support, feedback, or website questions.',
    )


def _disclaimer_defaults():
    return _defaults(
        title='Disclaimer | CEE MCQ',
        description='Read the disclaimer for CEE MCQ. The content is for educational use only and should be used as revision support, not as an official exam source.',
        keywords='CEE MCQ, Disclaimer, educational use, exam practice',
        og_title='Disclaimer | CEE MCQ',
        og_description='Educational disclaimer for CEE MCQ and its practice content.',
    )


def _privacy_defaults():
    return _defaults(
        title='Privacy Policy | CEE MCQ',
        description='Read the privacy policy for CEE MCQ. Learn what minimal data may be collected, how cookies are used, and how AdSense or analytics may operate on the site.',
        keywords='CEE MCQ, Privacy Policy, cookies, data handling, AdSense',
        og_title='Privacy Policy | CEE MCQ',
        og_description='Privacy policy for CEE MCQ, including cookies, minimal data handling, and AdSense or analytics usage.',
    )


def _safe_lookup(request):
    resolver = getattr(request, 'resolver_match', None)
    route_name = getattr(resolver, 'url_name', '') or ''
    page_slug = getattr(request, 'page_slug', '') or (resolver.kwargs.get('slug') if resolver and resolver.kwargs else '') or route_name

    try:
        supabase_seo = get_supabase_page_seo(page_slug)
        if supabase_seo:
            return SimpleNamespace(
                page_slug=supabase_seo.get('page_slug', page_slug),
                meta_title=supabase_seo.get('meta_title', SITE_NAME),
                meta_description=supabase_seo.get('meta_description', ''),
                meta_keywords=supabase_seo.get('meta_keywords', ''),
                og_title=supabase_seo.get('og_title') or supabase_seo.get('meta_title', SITE_NAME),
                og_description=supabase_seo.get('og_description') or supabase_seo.get('meta_description', ''),
            )

        seo = PageSEO.objects.filter(page_slug=page_slug).first()
        if seo:
            return seo

        if route_name == 'home':
            return _home_defaults()

        if route_name == 'chapters':
            subject_slug = (resolver.kwargs or {}).get('slug') if resolver else ''
            subject = Subject.objects.filter(slug=subject_slug).only('name').first()
            return _subject_defaults(subject.name if subject else SITE_NAME)

        if route_name == 'quiz':
            chapter_slug = (resolver.kwargs or {}).get('slug') if resolver else ''
            chapter = Chapter.objects.select_related('subject').filter(slug=chapter_slug).first()
            if chapter and chapter.subject:
                return _chapter_quiz_defaults(chapter.name, chapter.subject.name)

        if route_name == 'subchapter_quiz':
            subchapter_slug = (resolver.kwargs or {}).get('slug') if resolver else ''
            subchapter = SubChapter.objects.select_related('chapter__subject').filter(slug=subchapter_slug).first()
            if subchapter and subchapter.chapter and subchapter.chapter.subject:
                return _subchapter_quiz_defaults(subchapter.name, subchapter.chapter.name)

        if route_name == 'full_test':
            return _full_test_defaults()

        if route_name == 'about':
            return _about_defaults()

        if route_name == 'contact':
            return _contact_defaults()

        if route_name == 'disclaimer':
            return _disclaimer_defaults()

        if route_name == 'privacy_policy':
            return _privacy_defaults()

    except Exception:
        pass

    return _defaults(
        title=SITE_NAME,
        description='Practice free CEE MCQ questions for Nepal\'s Common Entrance Examination.',
        keywords='CEE MCQ, CEE Nepal, practice test, MCQ questions',
    )


def page_seo(request):
    return {'page_seo': _safe_lookup(request)}