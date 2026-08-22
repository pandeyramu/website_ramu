from genericpath import exists
import random
import re
import uuid
import json
import socket
import hashlib
import logging
from functools import lru_cache
import requests
from django.core.cache import cache
from django.contrib.sites.requests import RequestSite
from django.urls import reverse
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.http import Http404, HttpResponse, JsonResponse
from django.views.decorators.cache import never_cache
from django.db import connection, IntegrityError
from django.db.utils import DatabaseError
from django.core.mail import send_mail
from django.conf import settings
from .models import Subject, Chapter, SubChapter, Question, TestResult, PageSEO, QuestionReport, SolutionSet
from .sitemaps import sitemaps
from .seo_provider import get_supabase_page_seo
from .context_processors import _subject_defaults


logger = logging.getLogger(__name__)
TEST_HISTORY_LIMIT = 5


@lru_cache(maxsize=1)
def _ordered_subjects():
    return list(Subject.objects.only('id', 'name', 'slug').order_by('id'))


def _subject_alias_url(subject_slug):
    return reverse('chapters', args=[subject_slug]) if subject_slug else '/'


def _crawl_navigation_links(subject_slug=None):
    links = {
        'all_subjects_url': reverse('all_subjects'),
    }

    if subject_slug:
        links['subject_mcq_url'] = _subject_alias_url(subject_slug)

    subjects = _ordered_subjects()
    if subject_slug and subjects:
        current_index = next((index for index, subject in enumerate(subjects) if subject.slug == subject_slug), None)
        if current_index is not None:
            previous_subject = subjects[current_index - 1] if current_index > 0 else None
            next_subject = subjects[current_index + 1] if current_index < len(subjects) - 1 else None

            if previous_subject:
                links['previous_subject'] = {
                    'name': previous_subject.name,
                    'subject_url': reverse('chapters', args=[previous_subject.slug]),
                    'mcq_url': _subject_alias_url(previous_subject.slug),
                }
            if next_subject:
                links['next_subject'] = {
                    'name': next_subject.name,
                    'subject_url': reverse('chapters', args=[next_subject.slug]),
                    'mcq_url': _subject_alias_url(next_subject.slug),
                }

    return links


def _crawl_hubs():
    hubs = []
    for subject in _ordered_subjects():
        hubs.append({
            'name': f'{subject.name} MCQ',
            'url': _subject_alias_url(subject.slug),
            'description': f'Go straight to {subject.name} chapter wise practice and crawl the full {subject.name} topic tree.',
        })
    hubs.append({
        'name': 'All Subjects',
        'url': reverse('all_subjects'),
        'description': 'Browse every subject landing page from one hub.',
    })
    hubs.append({
        'name': 'Full Test',
        'url': reverse('full_test'),
        'description': 'Run the full mock test and reinforce the strongest exam-level URL.',
    })
    return hubs


def contact_submit(request):
    """Receive contact form POSTs and send email to site owner.
    Expects: name, email, message in POST body.
    Returns JSON {ok: true} on success or error message.
    """
    if request.method != 'POST':
        return JsonResponse({'error': 'method_not_allowed'}, status=405)

    name = request.POST.get('name', '').strip()
    email = request.POST.get('email', '').strip()
    message = request.POST.get('message', '').strip()

    if not (name and email and message):
        return JsonResponse({'error': 'missing_fields'}, status=400)

    subject = f'Website contact from {name}'
    body = f'From: {name} <{email}>\n\n{message}'
    try:
        send_mail(subject, body, getattr(settings, 'DEFAULT_FROM_EMAIL', email), ['pandeyramu57@gmail.com'])
        return JsonResponse({'ok': True})
    except Exception as exc:
        logger.exception('Failed to send contact email')
        return JsonResponse({'error': 'send_failed'}, status=500)


def _hub_page_context(*, page_slug, title, description, keywords, og_title, og_description, hub_heading, hub_intro, hub_items):
    return {
        **_crawl_navigation_links(),
        'page_slug': page_slug,
        'page_default_title': title,
        'page_default_description': description,
        'page_default_keywords': keywords,
        'page_default_og_title': og_title,
        'page_default_og_description': og_description,
        'hub_heading': hub_heading,
        'hub_intro': hub_intro,
        'hub_items': hub_items,
    }

BLOG_POST_TEMPLATES = {
    'chapter-wise-marks-distribution': 'chapter-wise-marks-distribution.html',
    'last-30-days-cee-prep-plan': 'last-30-days-cee-prep-plan.html',
    'how-to-remember-organic-reactions': 'how-to-remember-organic-reactions.html',
    'how-to-prepare-for-cee': 'how-to-prepare-for-cee.html',
    'human-biology-cee-questions': 'human-biology-cee-questions.html',
    'organic-chemistry-cee-tips': 'organic-chemistry-cee-tips.html',
    'physics-high-weightage-topics': 'blog_physics_high_weightage.html',
    'mat-section-tips': 'blog_mat_section_tips.html',
    'cee-exam-day-strategy': 'blog_exam_day_strategy.html',
    'biology-diagram-revision-cee': 'biology-diagram-revision-cee.html',
    'chemistry-reaction-map-cee': 'chemistry-reaction-map-cee.html',
    'past-papers-smart-practice-cee': 'past-papers-smart-practice-cee.html',
    'negative-marking-strategy-cee': 'negative-marking-strategy-cee.html',
    'cee-study-schedule-that-works': 'cee-study-schedule-that-works.html',
    'botany-key-topics-cee': 'botany-key-topics-cee.html',
    'inorganic-chemistry-memorise-cee': 'inorganic-chemistry-memorise-cee.html',
    'night-before-cee-preparation': 'night-before-cee-preparation.html',
    'improving-cee-score-practical-guide': 'improving-cee-score-practical-guide.html',
    'time-management-200-questions-cee': 'time-management-200-questions-cee.html',
    'common-mistakes-cee-biology': 'common-mistakes-cee-biology.html',
    'cee-eligibility-gpa-requirements': 'cee-eligibility-gpa-requirements.html',
    'cee-seats-quota-cutoff-explained': 'cee-seats-quota-cutoff-explained.html',
    'cee-mat-micro-syllabus': 'cee-mat-micro-syllabus.html',
    'cee-best-books-resources': 'cee-best-books-resources.html',
    'cee-vs-neet-nepali-students': 'cee-vs-neet-nepali-students.html',
}

BLOG_POST_ORDER = [
    'cee-vs-neet-nepali-students',
    'cee-best-books-resources',
    'cee-mat-micro-syllabus',
    'cee-seats-quota-cutoff-explained',
    'cee-eligibility-gpa-requirements',
    'night-before-cee-preparation',
    'last-30-days-cee-prep-plan',
    'time-management-200-questions-cee',
    'improving-cee-score-practical-guide',
    'cee-study-schedule-that-works',
    'negative-marking-strategy-cee',
    'inorganic-chemistry-memorise-cee',
    'organic-chemistry-cee-tips',
    'common-mistakes-cee-biology',
    'botany-key-topics-cee',
    'cee-exam-day-strategy',
    'past-papers-smart-practice-cee',
    'chemistry-reaction-map-cee',
    'biology-diagram-revision-cee',
    'how-to-remember-organic-reactions',
    'human-biology-cee-questions',
    'mat-section-tips',
    'physics-high-weightage-topics',
    'how-to-prepare-for-cee',
    'chapter-wise-marks-distribution',
]

BLOG_POST_META = {
    'chapter-wise-marks-distribution': {
        'title': 'Chapter wise Marks Distribution for CEE: What to Prioritise',
        'tag': 'Exam Strategy',
        'excerpt': 'Understand which chapters carry the most marks in CEE and how to allocate your study time for maximum impact.',
        'accent': '#1458a6', 'accent_soft': 'rgba(20, 88, 166, 0.08)', 'accent_border': 'rgba(20, 88, 166, 0.22)',
    },
    'last-30-days-cee-prep-plan': {
        'title': 'Last 30 Days CEE Preparation Plan: Time-sensitive, High-Impact',
        'tag': 'Plan',
        'excerpt': 'Use this high-impact, 30-day checklist to polish topics, fix weak areas, and simulate exam conditions before your CEE.',
        'accent': '#c04b62', 'accent_soft': 'rgba(192, 75, 98, 0.08)', 'accent_border': 'rgba(192, 75, 98, 0.22)',
    },
    'how-to-remember-organic-reactions': {
        'title': 'How to Remember Organic Chemistry Reactions: Practical Techniques',
        'tag': 'Chemistry',
        'excerpt': 'Use maps, categorization, reaction families and active recall to remember organic chemistry reactions more reliably and efficiently.',
        'accent': '#b36a00', 'accent_soft': 'rgba(179, 106, 0, 0.08)', 'accent_border': 'rgba(179, 106, 0, 0.24)',
    },
    'how-to-prepare-for-cee': {
        'title': 'How to Prepare for CEE Effectively',
        'tag': 'Study Tips',
        'excerpt': 'Build a realistic routine, focus on high weightage chapters, and use timed practice to steadily improve your CEE score.',
        'accent': '#1458a6', 'accent_soft': 'rgba(20, 88, 166, 0.08)', 'accent_border': 'rgba(20, 88, 166, 0.22)',
    },
    'human-biology-cee-questions': {
        'title': 'Human Biology: Most Important CEE Questions',
        'tag': 'Biology',
        'excerpt': 'Human Biology is a major scoring area in CEE. Focus on repeated concepts, terminology precision, and diagram-based revision.',
        'accent': '#1f8a4c', 'accent_soft': 'rgba(31, 138, 76, 0.08)', 'accent_border': 'rgba(31, 138, 76, 0.22)',
    },
    'organic-chemistry-cee-tips': {
        'title': 'Organic Chemistry Tips for CEE Nepal',
        'tag': 'Chemistry',
        'excerpt': 'Organic Chemistry carries major weight in CEE. Use reaction maps, functional-group logic, and repeated MCQ drills to convert it into a scoring section.',
        'accent': '#b36a00', 'accent_soft': 'rgba(179, 106, 0, 0.08)', 'accent_border': 'rgba(179, 106, 0, 0.24)',
    },
    'physics-high-weightage-topics': {
        'title': 'High Weightage Physics Topics for CEE',
        'tag': 'Physics',
        'excerpt': 'Prioritize Mechanics, Current Electricity, and Magnetism, then build accuracy through formula recall and timed mixed sets.',
        'accent': '#0f7a8a', 'accent_soft': 'rgba(15, 122, 138, 0.08)', 'accent_border': 'rgba(15, 122, 138, 0.22)',
    },
    'mat-section-tips': {
        'title': 'How to Score Full Marks in MAT Section',
        'tag': 'MAT',
        'excerpt': 'MAT is one of the fastest sections to improve. A disciplined daily routine can convert it into reliable marks with low preparation cost.',
        'accent': '#7a4dc7', 'accent_soft': 'rgba(122, 77, 199, 0.08)', 'accent_border': 'rgba(122, 77, 199, 0.22)',
    },
    'cee-exam-day-strategy': {
        'title': "CEE Exam Day Strategy: Do's and Don'ts",
        'tag': 'Strategy',
        'excerpt': 'A strong exam-day system can convert months of preparation into marks by protecting accuracy, pace, and confidence under pressure.',
        'accent': '#c04b62', 'accent_soft': 'rgba(192, 75, 98, 0.08)', 'accent_border': 'rgba(192, 75, 98, 0.22)',
    },
    'biology-diagram-revision-cee': {
        'title': 'Biology Diagram Revision That Actually Sticks',
        'tag': 'Biology',
        'excerpt': 'I stopped losing easy Biology marks when I began redrawing diagrams from memory and checking the labels against my own mistakes.',
        'accent': '#1f8a4c', 'accent_soft': 'rgba(31, 138, 76, 0.08)', 'accent_border': 'rgba(31, 138, 76, 0.22)',
    },
    'chemistry-reaction-map-cee': {
        'title': 'Chemistry Reaction Maps for Faster Recall',
        'tag': 'Chemistry',
        'excerpt': 'Instead of memorizing reactions in isolation, I built one map that linked every common conversion. That cut my confusion in half.',
        'accent': '#b36a00', 'accent_soft': 'rgba(179, 106, 0, 0.08)', 'accent_border': 'rgba(179, 106, 0, 0.24)',
    },
    'past-papers-smart-practice-cee': {
        'title': 'How I Use Past Papers to Study Smarter',
        'tag': 'Study Tips',
        'excerpt': 'Past papers are not just for checking yourself at the end. I use them as a map for what deserves more time now.',
        'accent': '#7a4dc7', 'accent_soft': 'rgba(122, 77, 199, 0.08)', 'accent_border': 'rgba(122, 77, 199, 0.22)',
    },
    'organic-chemistry-cee-tips': {
        'title': 'Organic Chemistry Tips for the CEE',
        'tag': 'Chemistry',
        'excerpt': 'Mastering Organic Chemistry for the CEE requires a strategic approach and consistent practice.',
        'accent': '#2c75bb', 'accent_soft': 'rgba(44, 117, 187, 0.08)', 'accent_border': 'rgba(44, 117, 187, 0.22)',
    },
    'negative-marking-strategy-cee': {
        'title': 'CEE Negative Marking Strategy: When to Skip a Question',
        'tag': 'Strategy',
        'excerpt': 'Learn when to attempt, when to skip, and how 0.25 negative marking should shape your CEE exam strategy.',
        'accent': '#c04b62', 'accent_soft': 'rgba(192, 75, 98, 0.08)', 'accent_border': 'rgba(192, 75, 98, 0.22)',
    },
    'cee-study-schedule-that-works': {
        'title': 'How to Build a CEE Study Schedule That Actually Works',
        'tag': 'Study Tips',
        'excerpt': 'Most study schedules fail because they are too rigid. Build a flexible plan with buffer days and revision cycles.',
        'accent': '#1458a6', 'accent_soft': 'rgba(20, 88, 166, 0.08)', 'accent_border': 'rgba(20, 88, 166, 0.22)',
    },
    'botany-key-topics-cee': {
        'title': 'Botany for CEE: Key Topics You Cannot Skip',
        'tag': 'Biology',
        'excerpt': 'Botany carries 40 marks in CEE. Focus on Biodiversity, Genetics, and Plant Physiology to maximise your score.',
        'accent': '#1f8a4c', 'accent_soft': 'rgba(31, 138, 76, 0.08)', 'accent_border': 'rgba(31, 138, 76, 0.22)',
    },
    'inorganic-chemistry-memorise-cee': {
        'title': 'Chemistry Inorganic Section: What to Memorise for CEE',
        'tag': 'Chemistry',
        'excerpt': 'Inorganic Chemistry feels vast but only 10 marks are tested. Here is exactly what to memorise and what to skip.',
        'accent': '#b36a00', 'accent_soft': 'rgba(179, 106, 0, 0.08)', 'accent_border': 'rgba(179, 106, 0, 0.24)',
    },
    'night-before-cee-preparation': {
        'title': 'The Night Before CEE: What to Do and What to Avoid',
        'tag': 'Strategy',
        'excerpt': 'The night before CEE can make or break your performance. Here is the ideal routine based on my experience.',
        'accent': '#c04b62', 'accent_soft': 'rgba(192, 75, 98, 0.08)', 'accent_border': 'rgba(192, 75, 98, 0.22)',
    },
    'improving-cee-score-practical-guide': {
        'title': 'How I Improved My CEE Score: A Practical Guide',
        'tag': 'Study Tips',
        'excerpt': 'From my first mock test to the final CEE, here are the specific changes that moved my score from 110 to 155.',
        'accent': '#1458a6', 'accent_soft': 'rgba(20, 88, 166, 0.08)', 'accent_border': 'rgba(20, 88, 166, 0.22)',
    },
    'time-management-200-questions-cee': {
        'title': 'Time Management During CEE: 200 Questions in 3 Hours',
        'tag': 'Strategy',
        'excerpt': 'You get 54 seconds per question. Here is how to manage that time without sacrificing accuracy.',
        'accent': '#c04b62', 'accent_soft': 'rgba(192, 75, 98, 0.08)', 'accent_border': 'rgba(192, 75, 98, 0.22)',
    },
    'common-mistakes-cee-biology': {
        'title': 'Common Mistakes in CEE Biology and How to Avoid Them',
        'tag': 'Biology',
        'excerpt': 'The 5 most common Biology mistakes in CEE cost students easy marks. Learn to avoid them with specific examples.',
        'accent': '#1f8a4c', 'accent_soft': 'rgba(31, 138, 76, 0.08)', 'accent_border': 'rgba(31, 138, 76, 0.22)',
    },
    'cee-eligibility-gpa-requirements': {
        'title': 'CEE Eligibility with Low GPA: Can You Apply with D Grades?',
        'tag': 'Eligibility',
        'excerpt': 'A plain explanation of CEE eligibility with a low GPA or D grades, based on what I found while helping a relative check his options.',
        'accent': '#0f7a8a', 'accent_soft': 'rgba(15, 122, 138, 0.08)', 'accent_border': 'rgba(15, 122, 138, 0.22)',
    },
    'cee-seats-quota-cutoff-explained': {
        'title': 'CEE Seats, Quota and Cutoffs: How Selection Actually Works',
        'tag': 'Exam Info',
        'excerpt': 'Cutoffs are not magic numbers. They are outputs of seat counts, quota categories and applicant behaviour. Rank thinking beats mark thinking.',
        'accent': '#35619e', 'accent_soft': 'rgba(53, 97, 158, 0.08)', 'accent_border': 'rgba(53, 97, 158, 0.22)',
    },
    'cee-mat-micro-syllabus': {
        'title': 'MAT Micro Syllabus for CEE: Every Question Type Explained',
        'tag': 'MAT',
        'excerpt': 'All four MAT reasoning areas with every question type inside them, which ones are fast marks, and how to drill each one efficiently.',
        'accent': '#7a4dc7', 'accent_soft': 'rgba(122, 77, 199, 0.08)', 'accent_border': 'rgba(122, 77, 199, 0.22)',
    },
    'cee-best-books-resources': {
        'title': 'CEE Preparation Books and Resources: What I Used and What I Skipped',
        'tag': 'Resources',
        'excerpt': 'An honest inventory of my CEE books: which three earned their shelf space, what I skipped without regret, and the free resources that carried real weight.',
        'accent': '#b36a00', 'accent_soft': 'rgba(179, 106, 0, 0.08)', 'accent_border': 'rgba(179, 106, 0, 0.24)',
    },
    'cee-vs-neet-nepali-students': {
        'title': 'CEE vs NEET for Nepali Students: What I Learned Comparing Both',
        'tag': 'Decisions',
        'excerpt': 'Syllabus overlap is enormous but competition mathematics differ sharply. A calm comparison covering patterns, paperwork and licensing loops.',
        'accent': '#1f8a4c', 'accent_soft': 'rgba(31, 138, 76, 0.08)', 'accent_border': 'rgba(31, 138, 76, 0.22)',
    },
}

BLOG_RELATED = {
    'chapter-wise-marks-distribution': ['physics-high-weightage-topics', 'botany-key-topics-cee', 'cee-study-schedule-that-works'],
    'last-30-days-cee-prep-plan': ['night-before-cee-preparation', 'time-management-200-questions-cee', 'cee-best-books-resources'],
    'how-to-remember-organic-reactions': ['chemistry-reaction-map-cee', 'organic-chemistry-cee-tips', 'inorganic-chemistry-memorise-cee'],
    'how-to-prepare-for-cee': ['cee-study-schedule-that-works', 'cee-eligibility-gpa-requirements', 'mat-section-tips'],
    'human-biology-cee-questions': ['common-mistakes-cee-biology', 'biology-diagram-revision-cee', 'botany-key-topics-cee'],
    'organic-chemistry-cee-tips': ['how-to-remember-organic-reactions', 'chemistry-reaction-map-cee', 'cee-best-books-resources'],
    'physics-high-weightage-topics': ['time-management-200-questions-cee', 'negative-marking-strategy-cee', 'chapter-wise-marks-distribution'],
    'mat-section-tips': ['cee-mat-micro-syllabus', 'negative-marking-strategy-cee', 'time-management-200-questions-cee'],
    'cee-exam-day-strategy': ['night-before-cee-preparation', 'negative-marking-strategy-cee', 'improving-cee-score-practical-guide'],
    'biology-diagram-revision-cee': ['botany-key-topics-cee', 'human-biology-cee-questions', 'common-mistakes-cee-biology'],
    'chemistry-reaction-map-cee': ['how-to-remember-organic-reactions', 'organic-chemistry-cee-tips', 'cee-best-books-resources'],
    'past-papers-smart-practice-cee': ['cee-study-schedule-that-works', 'improving-cee-score-practical-guide', 'last-30-days-cee-prep-plan'],
    'negative-marking-strategy-cee': ['time-management-200-questions-cee', 'cee-exam-day-strategy', 'mat-section-tips'],
    'cee-study-schedule-that-works': ['last-30-days-cee-prep-plan', 'how-to-prepare-for-cee', 'past-papers-smart-practice-cee'],
    'botany-key-topics-cee': ['biology-diagram-revision-cee', 'human-biology-cee-questions', 'common-mistakes-cee-biology'],
    'inorganic-chemistry-memorise-cee': ['how-to-remember-organic-reactions', 'chemistry-reaction-map-cee', 'cee-best-books-resources'],
    'night-before-cee-preparation': ['cee-exam-day-strategy', 'last-30-days-cee-prep-plan', 'time-management-200-questions-cee'],
    'improving-cee-score-practical-guide': ['past-papers-smart-practice-cee', 'cee-study-schedule-that-works', 'negative-marking-strategy-cee'],
    'time-management-200-questions-cee': ['negative-marking-strategy-cee', 'cee-exam-day-strategy', 'physics-high-weightage-topics'],
    'common-mistakes-cee-biology': ['human-biology-cee-questions', 'botany-key-topics-cee', 'biology-diagram-revision-cee'],
    'cee-eligibility-gpa-requirements': ['cee-vs-neet-nepali-students', 'how-to-prepare-for-cee', 'cee-seats-quota-cutoff-explained'],
    'cee-seats-quota-cutoff-explained': ['cee-eligibility-gpa-requirements', 'cee-vs-neet-nepali-students', 'chapter-wise-marks-distribution'],
    'cee-mat-micro-syllabus': ['mat-section-tips', 'negative-marking-strategy-cee', 'time-management-200-questions-cee'],
    'cee-best-books-resources': ['last-30-days-cee-prep-plan', 'how-to-prepare-for-cee', 'cee-mat-micro-syllabus'],
    'cee-vs-neet-nepali-students': ['cee-eligibility-gpa-requirements', 'cee-seats-quota-cutoff-explained', 'how-to-prepare-for-cee'],
}

QUIZ_OPENERS = [
    "Every attempt on this page draws a fresh set of up to 50 questions from the verified {sub} material in our {ch} bank.",
    "This test pulls its items from the checked {ch} collection covering {sub}, reshuffled every time you begin.",
    "Each start assembles up to 50 {sub} MCQs selected at random from the reviewed {ch} question bank.",
    "Questions here come from the verified {ch} pool for {sub}; no two attempts contain the same mix.",
    "The quiz samples up to 50 items on {sub} each run, all sourced from our vetted {ch} material.",
    "A new combination of {sub} questions is chosen at every attempt from the curated {ch} bank.",
    "When you begin, the system picks up to 50 randomised {sub} questions drawn from {ch}.",
    "This drill serves a randomly chosen slice of the {ch} questions tagged {sub}, capped at 50 per round.",
]

QUIZ_MARKING = [
    "Scoring follows the real CEE convention: one mark for every correct answer and a 0.25 deduction for every wrong one.",
    "Marking mirrors the actual exam, so correct answers add a full mark while incorrect ones cost a quarter.",
    "The score sheet works like the real paper: plus one when right, minus a quarter when wrong, nothing when left blank.",
    "Attempt rules match exam day conditions, including the penalty of 0.25 marks for each incorrect response.",
    "Correct responses are worth one mark each, wrong responses deduct 0.25, and skipped questions stay neutral, just like CEE itself.",
    "We apply genuine entrance marking: a single mark per correct choice offset by a small quarter-mark cut for mistakes.",
]

QUIZ_RESULTS = [
    "On submission you immediately see your total score along with accuracy and pace figures, then every item opens its worked solution for review.",
    "Your result appears the moment you finish: score, accuracy percentage, time used, and a question-by-question walkthrough with reasons.",
    "Finishing unlocks the summary sheet first, and beneath it the complete answer key explaining why each option stands or falls.",
    "Once submitted, the report shows where marks were gained or lost and attaches a step by step justification to each question.",
    "The instant report card covers score and speed, while the review section underneath dissects all answers one at a time.",
]

QUIZ_SAMPLES = [
    "Work through these solved examples first; they show exactly how much reasoning each explanation carries.",
    "A short set of fully solved samples follows, written in the same style as the solutions you unlock after the test.",
    "Below sit a few sample items with their complete working, so you can judge the depth before committing to a timed run.",
    "These starter questions include finished solutions, giving you a feel for the format without starting the clock.",
    "Before racing the clock, skim these worked samples; each one demonstrates how our explanations handle the options in turn.",
]

QUIZ_RESULT_TAILS = [
    "Treat the review as part of the learning, not just the verdict.",
    "Most students gain more from reading the missed explanations than from the score itself.",
    "Repeat attempts feel different because the draw changes every time.",
    "Short regular sessions here compound faster than one long weekly grind.",
]

QUIZ_SAMPLE_TAILS = [
    "The full test follows the same pattern at scale.",
    "Nothing in the timed paper will stray beyond what these represent.",
    "If these feel comfortable, you are ready for a scored run.",
    "They are drawn from the same verified pool the live quiz uses.",
]

QUIZ_META_DESCRIPTIONS = [
    "Free online {sub} MCQ practice from {ch}. Randomised 50-question attempts with real CEE marking and worked solutions after submission.",
    "Attempt {sub} multiple choice questions from {ch} under timed conditions. Instant scoring with step by step answer review.",
    "{sub} quiz drawn from our verified {ch} bank for CEE preparation. Fresh mix every attempt, full explanations on completion.",
    "Practise {sub} MCQs online with exam-style negative marking. Part of the {ch} practice series for Nepal's CEE.",
    "Timed {sub} objective questions with immediate results and per-question explanations. One of the {ch} sets built for CEE aspirants.",
    "Test yourself on {sub} through randomised draws from the reviewed {ch} collection. Score, accuracy and solutions appear instantly.",
    "{ch} practice covering {sub}: up to 50 shuffled MCQs per attempt, marked like the real examination with detailed review.",
    "Sharpen {sub} with repeated randomised quizzes sourced from verified {ch} questions, each answered response explained in full.",
]

SOLVED_META_DESCRIPTIONS = [
    "Worked solutions for {sub} set {set_no}: every MCQ answered with a step by step explanation for CEE revision.",
    "Browse set {set_no} of the {sub} solved series. Each question shows its correct option plus the full reasoning behind it.",
    "{sub} solved question set {set_no} from {ch}, with answers and explanations ideal for checking yourself after a timed attempt.",
    "Study {sub} through solved MCQs, set {set_no}: correct answers alongside explanations written to teach the method.",
    "Set {set_no} of {sub} solved MCQs from {ch}. Review each explanation and note the reasoning patterns examiners favour.",
    "{sub} questions solved in detail, set {set_no}. Attempt first, then compare your approach against the worked answer.",
]

SUBCHAPTERS_META_DESCRIPTIONS = [
    "All {sub} topics in one place. Pick a subchapter to start focused MCQ practice with instant scoring.",
    "Choose a {sub} subchapter for targeted drills drawn from verified CEE-style {ch} questions.",
    "Topic wise {sub} practice: every subchapter links to a randomised quiz with worked solutions afterwards.",
    "Break {ch} into {sub} subtopics and drill each one separately before moving to mixed chapter tests.",
    "A clean index of {sub} subchapters within {ch}, each with its own quiz page and solved material.",
]


BLOG_PUBLISH_DATES = {
    'chapter-wise-marks-distribution': (2026, 1, 12),
    'how-to-prepare-for-cee': (2026, 1, 27),
    'physics-high-weightage-topics': (2026, 2, 5),
    'mat-section-tips': (2026, 2, 16),
    'human-biology-cee-questions': (2026, 2, 24),
    'how-to-remember-organic-reactions': (2026, 3, 6),
    'biology-diagram-revision-cee': (2026, 3, 17),
    'chemistry-reaction-map-cee': (2026, 3, 30),
    'past-papers-smart-practice-cee': (2026, 4, 9),
    'cee-exam-day-strategy': (2026, 4, 21),
    'botany-key-topics-cee': (2026, 5, 4),
    'common-mistakes-cee-biology': (2026, 5, 14),
    'organic-chemistry-cee-tips': (2026, 5, 26),
    'inorganic-chemistry-memorise-cee': (2026, 6, 8),
    'negative-marking-strategy-cee': (2026, 6, 18),
    'cee-study-schedule-that-works': (2026, 6, 29),
    'improving-cee-score-practical-guide': (2026, 7, 9),
    'time-management-200-questions-cee': (2026, 7, 20),
    'last-30-days-cee-prep-plan': (2026, 7, 30),
    'night-before-cee-preparation': (2026, 8, 11),
    'cee-eligibility-gpa-requirements': (2026, 8, 13),
    'cee-seats-quota-cutoff-explained': (2026, 8, 14),
    'cee-mat-micro-syllabus': (2026, 8, 17),
    'cee-best-books-resources': (2026, 8, 18),
    'cee-vs-neet-nepali-students': (2026, 8, 19),
}


def _stable_variant(key, pools):
    digest = hashlib.sha256(key.encode("utf-8")).digest()
    return tuple(pool[digest[i] % len(pool)] for i, pool in enumerate(pools))

def _get_chapter_question_ids(chapter_id):
    cache_key = f'chapter_qids:{chapter_id}'
    ids = cache.get(cache_key)
    if ids is None:
        ids = list(
            Question.objects.filter(chapter_id=chapter_id, verified=True)
            .values_list('id', flat=True)
        )
        cache.set(cache_key, ids, timeout=3600)
    return ids


def _get_subchapter_question_ids(subchapter_id):
    cache_key = f'subchapter_qids:{subchapter_id}'
    ids = cache.get(cache_key)
    if ids is None:
        ids = list(
            Question.objects.filter(sub_chapter_id=subchapter_id, verified=True)
            .values_list('id', flat=True)
        )
        cache.set(cache_key, ids, timeout=3600)
    return ids


def _pick_random_questions(question_ids, limit=50):
    if not question_ids:
        return []

    selected_ids = random.sample(question_ids, min(limit, len(question_ids)))
    selected_qs = (
        Question.objects
        .filter(id__in=selected_ids)
        .select_related('chapter', 'sub_chapter')
        .only(
            'id',
            'chapter_id',
            'sub_chapter_id',
            'question_text',
            'option_a',
            'option_b',
            'option_c',
            'option_d',
            'correct_option',
            'chapter__name',
            'chapter__subject__name',
            'sub_chapter__name',
        )
    )
    id_to_question = {q.id: q for q in selected_qs}
    return [id_to_question[qid] for qid in selected_ids if qid in id_to_question]


def _load_questions_by_ids(question_ids, *, include_solution=True):
    """Load questions in id order, caching the immutable set in-process.

    The same attempt re-loads the exact same question set across the active
    page, submission, and results view, so caching by the id-set digest turns
    several repeat DB transfers into a single one. Question content only
    changes via admin/sync scripts, so a 1h TTL is safe.
    """
    ids = [int(qid) for qid in question_ids]
    if not ids:
        return []

    digest = hashlib.md5(','.join(str(qid) for qid in ids).encode('ascii')).hexdigest()
    cache_key = f'qset:{'full' if include_solution else 'lite'}:{digest}'
    cached = cache.get(cache_key)
    if cached is not None:
        return cached

    qs = (
        Question.objects
        .filter(id__in=ids, verified=True)
        .select_related('chapter', 'sub_chapter', 'chapter__subject')
    )
    if include_solution:
        fetched = list(qs)
    else:
        fetched = list(qs.only(
            'id',
            'chapter_id',
            'sub_chapter_id',
            'question_text',
            'option_a',
            'option_b',
            'option_c',
            'option_d',
            'correct_option',
            'chapter__name',
            'chapter__subject__name',
            'sub_chapter__name',
        ))

    id_to_question = {q.id: q for q in fetched}
    ordered = [id_to_question[qid] for qid in ids if qid in id_to_question]
    cache.set(cache_key, ordered, timeout=3600)
    return ordered


FULL_TEST_BLUEPRINT = {
    'Physics': {
        'Mechanics': 10,
        'Heat and Thermodynamics': 7,
        'Waves and Optics': 8,
        'Current Electricity and Magnetism': 9,
        'Electrostatics and Capacitors': 4,
        'Modern Physics': 12,
    },
    'Chemistry': {
        'Physical Chemistry': 17,
        'Inorganic Chemistry': 10,
        'Organic Chemistry': 17,
        'Applied Chemistry': 3,
        'Analytical Chemistry': 3,
    },
    'Botany': {
        'Basic Components of Life': 2,
        'Biodiversity': 9,
        'Ecology and Vegetation': 4,
        'Cell Biology': 5,
        'Genetics': 6,
        'Plant Anatomy': 3,
        'Plant Physiology': 6,
        'Developmental Botany': 2,
        'Applied Botany': 3,
    },
    'Zoology': {
        'Evolutionary Biology': 3,
        'Animal Diversity and Classification': 4,
        'Animal Tissues and Histology': 4,
        'Study of Selected Animals': 6,
        'Human Biology and Physiology': 15,
        'Microbial Diseases and Immunology': 4,
        'Medical Technology and Applied Biology': 2,
        'Biota, Environment and Conservation': 2,
    },
    'MAT': {
        'Verbal Reasoning Test': 5,
        'Numerical Reasoning': 5,
        'Logical Sequencing': 5,
        'Spatial Relation/Abstract Reasoning': 5,
    },
}


def _build_full_test_question_ids():
    """Collect random question IDs per chapter in 2 queries instead of 23.

    The per-chapter id buckets are immutable between syncs, so they are cached
    in-process (30 min TTL) to avoid re-transferring every question id in the
    DB on each full-test start.
    """
    from collections import defaultdict

    buckets = cache.get('ft_id_buckets')
    if buckets is None:
        # 1 query: load all question IDs grouped by (subject_name, chapter_name)
        qs = Question.objects.filter(verified=True).values_list(
            'chapter__subject__name', 'chapter__name', 'id'
        )
        buckets = defaultdict(list)
        for subj, chap, qid in qs:
            buckets[(subj, chap)].append(qid)
        cache.set('ft_id_buckets', dict(buckets), timeout=1800)

    selected_ids = []
    for subject_name, chapters_config in FULL_TEST_BLUEPRINT.items():
        subject_ids = []
        for chapter_name, question_count in chapters_config.items():
            bucket = buckets.get((subject_name, chapter_name), [])
            if bucket:
                subject_ids.extend(
                    random.sample(bucket, min(question_count, len(bucket)))
                )
        # Keep questions grouped by subject (Physics, Chemistry, Botany,
        # Zoology, MAT) so the paper reads in exam order, but vary the order
        # inside each subject block between attempts.
        random.shuffle(subject_ids)
        selected_ids.extend(subject_ids)

    return selected_ids


def _attempt_reference(session, key_prefix, force_new=False):
    """Return a short stable attempt reference for the current quiz session."""
    session_key = f"{key_prefix}_attempt_reference"
    attempt_reference = None if force_new else session.get(session_key)
    if not attempt_reference:
        attempt_reference = uuid.uuid4().hex[:8].upper()
        session[session_key] = attempt_reference
        session.modified = True
    return attempt_reference


def _is_attempt_already_submitted(session, key_prefix, attempt_reference):
    if not attempt_reference:
        return False
    submitted_key = f"{key_prefix}_submitted_attempts"
    submitted = session.get(submitted_key, [])
    return attempt_reference in submitted


def _mark_attempt_submitted(session, key_prefix, attempt_reference):
    if not attempt_reference:
        return
    submitted_key = f"{key_prefix}_submitted_attempts"
    submitted = session.get(submitted_key, [])
    if attempt_reference in submitted:
        return
    submitted.append(attempt_reference)
    session[submitted_key] = submitted[-20:]
    session.modified = True


def _parse_non_negative_int(raw_value, default=0):
    try:
        parsed = int(raw_value)
        return parsed if parsed >= 0 else default
    except (TypeError, ValueError):
        return default


def _format_duration(total_seconds):
    total_seconds = max(0, int(total_seconds))
    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60
    seconds = total_seconds % 60
    if hours:
        return f"{hours}h {minutes}m {seconds}s"
    if minutes:
        return f"{minutes}m {seconds}s"
    return f"{seconds}s"


def _build_result_metrics(*, total_questions, total_attempted, total_correct, time_taken_seconds):
    accuracy = round((total_correct / total_attempted) * 100, 1) if total_attempted else 0.0
    completion = round((total_attempted / total_questions) * 100, 1) if total_questions else 0.0
    per_question_seconds = round((time_taken_seconds / total_attempted), 1) if total_attempted else 0.0

    return {
        'accuracy_percent': accuracy,
        'completion_percent': completion,
        'time_taken_seconds': time_taken_seconds,
        'time_taken_display': _format_duration(time_taken_seconds),
        'per_question_time_display': f"{per_question_seconds}s" if total_attempted else '0s',
    }


SUBJECT_ORDER = ['Physics', 'Chemistry', 'Botany', 'Zoology', 'MAT']


def _build_full_test_subject_breakdown(questions, user_answers):
    """Per-subject stats for the full test results graph.

    Returns a list of dicts ordered by SUBJECT_ORDER, each with:
    name, total, attempted, correct, accuracy_percent.
    Subjects with no questions are still included so the 5-subject
    breakdown is always shown once MAT questions are available.
    """
    breakdown = []
    for subject_name in SUBJECT_ORDER:
        subject_questions = [q for q in questions if q.chapter.subject.name == subject_name]
        total = len(subject_questions)
        attempted = 0
        correct = 0
        for q in subject_questions:
            answer = user_answers.get(q.id)
            if answer:
                attempted += 1
                if answer == q.correct_option:
                    correct += 1
        accuracy = round((correct / attempted) * 100, 1) if attempted else 0.0
        breakdown.append({
            'name': subject_name,
            'total': total,
            'attempted': attempted,
            'correct': correct,
            'accuracy_percent': accuracy,
        })
    return breakdown


def _normalize_exact_name(value):
    return ' '.join((value or '').split()).strip()


def _stringify_answer_keys(answer_map):
    if not isinstance(answer_map, dict):
        return {}
    return {str(key): value for key, value in answer_map.items()}


@lru_cache(maxsize=1)
def _testresult_columns():
    table_name = TestResult._meta.db_table
    with connection.cursor() as cursor:
        return {column.name for column in connection.introspection.get_table_description(cursor, table_name)}


def _testresult_has_columns(*column_names):
    available_columns = _testresult_columns()
    return all(column_name in available_columns for column_name in column_names)


def _refresh_testresult_columns_cache():
    _testresult_columns.cache_clear()


def _history_value(result, field_name, default=None):
    if isinstance(result, dict):
        return result.get(field_name, default)
    return getattr(result, field_name, default)


def _build_test_history_entries(results):
    entries = []
    for result in results:
        total_attempted = _history_value(result, 'total_attempted', 0) or 0
        total_correct = _history_value(result, 'total_correct', None)
        time_taken_seconds = _history_value(result, 'time_taken_seconds', None)

        if total_correct is None:
            accuracy = None
        else:
            accuracy = round((total_correct / total_attempted) * 100, 1) if total_attempted else 0.0

        if time_taken_seconds is None:
            time_taken_display = '--'
            per_question_display = '--'
        else:
            per_question_seconds = round((time_taken_seconds / total_attempted), 1) if total_attempted else 0.0
            time_taken_display = _format_duration(time_taken_seconds)
            per_question_display = f'{per_question_seconds}s' if total_attempted else '0s'

        entries.append({
            'topic': _history_value(result, 'topic', ''),
            'score': _history_value(result, 'score', 0),
            'total_attempted': total_attempted,
            'total_correct': total_correct,
            'accuracy_percent': accuracy,
            'accuracy_display': f'{accuracy}%' if accuracy is not None else '--',
            'time_taken_display': time_taken_display,
            'per_question_time_display': per_question_display,
            'created_at': _history_value(result, 'created_at', None),
        })
    return entries


def _get_test_history(*, user_name, limit=TEST_HISTORY_LIMIT):
    exact_name = _normalize_exact_name(user_name)
    if not exact_name:
        return []

    name_hash = hashlib.md5(exact_name.lower().encode()).hexdigest()
    cache_key = f'thist:{name_hash}:{limit}'
    cached_result = cache.get(cache_key)
    if cached_result is not None:
        return cached_result

    try:
        if _testresult_has_columns('total_correct', 'time_taken_seconds'):
            history_qs = TestResult.objects.filter(name__iexact=exact_name).order_by('-created_at', '-id')[:limit]
        else:
            history_qs = TestResult.objects.filter(name__iexact=exact_name).values(
                'topic',
                'score',
                'total_attempted',
                'created_at',
            ).order_by('-created_at', '-id')[:limit]
        entries = _build_test_history_entries(history_qs)
    except DatabaseError:
        _refresh_testresult_columns_cache()
        fallback_qs = TestResult.objects.filter(name__iexact=exact_name).values(
            'topic',
            'score',
            'total_attempted',
            'created_at',
        ).order_by('-created_at', '-id')[:limit]
        entries = _build_test_history_entries(fallback_qs)

    cache.set(cache_key, entries, timeout=300)
    return entries


def _save_test_result(*, user_name, topic, total_attempted, total_correct, time_taken_seconds, score):
    payload = {
        'name': user_name,
        'topic': topic,
        'score': score,
        'total_attempted': total_attempted,
    }

    try:
        if _testresult_has_columns('total_correct', 'time_taken_seconds'):
            payload['total_correct'] = total_correct
            payload['time_taken_seconds'] = time_taken_seconds

        result = TestResult.objects.create(**payload)
    except DatabaseError:
        _refresh_testresult_columns_cache()
        safe_payload = {
            'name': user_name,
            'topic': topic,
            'score': score,
            'total_attempted': total_attempted,
        }
        result = TestResult.objects.create(**safe_payload)

    exact_name = _normalize_exact_name(user_name)
    if exact_name:
        name_hash = hashlib.md5(exact_name.lower().encode()).hexdigest()
        cache.delete(f'thist:{name_hash}:{TEST_HISTORY_LIMIT}')

    return result


def keepalive(request):
    """No-DB liveness probe for Uptime Robot / client pings.

    Deliberately avoids any database query so monitoring traffic adds zero
    Postgres egress. Render keeps the instance awake on any HTTP hit.
    """
    return HttpResponse("OK", status=200)


def report_question(request):
    try:
        if request.method != 'POST':
            return JsonResponse({'ok': False, 'message': 'POST required.'}, status=405)

        payload = json.loads(request.body.decode('utf-8'))

        user_name = (payload.get('name') or '').strip()
        attempt_reference = (payload.get('attempt_reference') or '').strip()
        topic = (payload.get('topic') or '').strip()
        reason = (payload.get('reason') or '').strip()
        question_id = int(payload.get('question_id') or -1)
        question_text = (payload.get('question_text') or '').strip()
        if question_id <= 0 or not question_text or not reason:
            return JsonResponse({'ok': False, 'message': 'Missing question details.'}, status=400)
        exists = QuestionReport.objects.filter(
            question_id=question_id,
            attempt_reference=attempt_reference
        ).exists()

        if exists:
            return JsonResponse({
                'ok': False,
                'message': 'Already reported for this attempt.'
            }, status=200)
        subject = f"CEE Quiz Report | QID {question_id}"

        message = ( 
            "🚨Wake Up Master :) ^_^🚨\n\n" 
            "🚨 CEE Quiz Report Notification 🚨\n\n"
              "A question has been flagged for review in the CEE Quiz application.\n" 
              "Please find the details below:\n\n" f"👤 User: {user_name or 'Unknown'}\n" 
              f"🧾 Attempt ID: {attempt_reference or 'N/A'}\n" 
              f"📚 Topic: {topic or 'N/A'}\n"
                f"⚠️ Reason for Report: {reason}\n" 
                f"🆔 Question ID: {question_id}\n\n" 
                f"📝 Question Text:\n{question_text}\n\n" 
                "This report was generated automatically by the system."
                  )
        use_resend = bool(getattr(settings, 'RESEND_API_KEY', '')) or \
                      getattr(settings, 'REPORT_EMAIL_PROVIDER', 'smtp') == 'resend'

        email_success = False

        if use_resend:
            resend_key = getattr(settings, 'RESEND_API_KEY', '')

            if not resend_key:
                return JsonResponse({
                    'ok': False,
                    'message': 'Resend API key missing.'
                }, status=200)

            response = requests.post(
                getattr(settings, 'RESEND_API_URL', 'https://api.resend.com/emails'),
                headers={
                    'Authorization': f'Bearer {resend_key}',
                    'Content-Type': 'application/json',
                },
                json={
                    'from': settings.DEFAULT_FROM_EMAIL,
                    'to': [getattr(settings, 'REPORT_TO_EMAIL', 'admin@example.com')],
                    'subject': subject,
                    'text': message,
                },
                timeout=getattr(settings, 'EMAIL_HTTP_TIMEOUT', 10),
            )

            email_success = response.status_code < 300

        else:
            send_mail(
                subject=subject,
                message=message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[getattr(settings, 'REPORT_TO_EMAIL', 'admin@example.com')],
                fail_silently=False,
            )
            email_success = True
        if not email_success:
            return JsonResponse({
                'ok': False,
                'message': 'Email failed. Report not saved.'
            }, status=500)

        QuestionReport.objects.create(
            question_id=question_id,
            user_name=user_name,
            attempt_reference=attempt_reference,
            topic=topic,
            reason=reason,
            question_text=question_text
        )

        return JsonResponse({'ok': True, 'message': 'Report submitted successfully.'})

    except json.JSONDecodeError:
        return JsonResponse({'ok': False, 'message': 'Invalid JSON payload.'}, status=400)

    except requests.RequestException:
        logger.exception('report_question email failed')
        return JsonResponse({'ok': False, 'message': 'Failed to submit report. Please try again later.'}, status=500)

    except Exception:
        logger.exception('Unexpected error in report_question')
        return JsonResponse({'ok': False, 'message': 'An unexpected error occurred. Please try again later.'}, status=500)
@never_cache  # Never serve a stale home page (page content is versioned in templates)
def home(request):
    subject_list = _ordered_subjects()
    total_questions = cache.get('home_total_questions')
    if total_questions is None:
        total_questions = Question.objects.count()
        cache.set('home_total_questions', total_questions, timeout=900)
    page_default_title = 'CEE MCQ | Free Practice Questions | CEE MCQ'
    page_default_description = "Free CEE MCQ practice. Chapter wise MCQ questions in Biology, Chemistry, Physics and MAT for Nepal's Common Entrance Examination."
    page_default_keywords = 'CEE MCQ, CEE Nepal, Chapter wise MCQ Questions, Biology, Chemistry, Physics, MAT'
    request.page_slug = 'home'
    return render(request, 'home.html', {
        'subjects': subject_list,
        'total_questions': total_questions,
        'crawl_hubs': _crawl_hubs(),
        'page_slug': 'home',
        'page_default_title': page_default_title,
        'page_default_description': page_default_description,
        'page_default_keywords': page_default_keywords,
        'page_default_og_title': 'CEE MCQ | Free CEE MCQ Questions',
        'page_default_og_description': "Free CEE entrance MCQ practice. Chapter wise MCQ questions in Biology, Chemistry, Physics and MAT for Nepal's Common Entrance Examination.",
    })


def all_subjects(request):
    subjects = _ordered_subjects()
    hub_items = []
    for subject in subjects:
        chapters = list(Chapter.objects.filter(subject=subject).order_by('id'))
        hub_items.append({
            'name': f'{subject.name} MCQ',
            'url': _subject_alias_url(subject.slug),
            'description': (
                f"Practice {subject.name} MCQs with structured questions, organised chapter by chapter. "
                f"Includes {len(chapters)} chapters for focused revision and exam preparation."
            ),
            'chapters': [c.name for c in chapters],
        })

    request.page_slug = 'all-subjects'
    context = _hub_page_context(
        page_slug='all-subjects',
        title='All Subjects | CEE MCQ',
        description='Browse every CEE subject landing page and move quickly between Biology, Chemistry, Physics, and MAT.',
        keywords='CEE MCQ, All Subjects, Biology MCQ, Chemistry MCQ, Physics MCQ, MAT MCQ',
        og_title='All Subjects | CEE MCQ',
        og_description='Browse every CEE subject landing page and move quickly between Biology, Chemistry, Physics, and MAT.',
        hub_heading='All Subject Entry Points',
        hub_intro=(
    "This page gives you a single place to jump into every CEE subject: Physics, Chemistry, "
    "Botany, Zoology, and MAT. Each subject is broken into chapters, and chapters with many topics "
    "are split into subchapters, so you can drill down to exactly the area you want to practise. "
    "Every MCQ comes with an answer and a step by step solution, and every test applies the real "
    "exam's negative marking."
),
        hub_items=hub_items,
    )
    return render(request, 'seo_hub.html', context)


def chapters(request, slug):
    """Subject page looked up by slug."""
    subject = get_object_or_404(Subject, slug=slug)
    chapters_list = Chapter.objects.filter(subject=subject).order_by('id')
    page_default_title = f'CEE {subject.name} MCQ Questions | Chapter Wise | CEE MCQ'
    page_default_description = f"Explore all {subject.name} chapters and practice chapter wise MCQ questions to prepare for Nepal's Common Entrance Examination."
    page_default_keywords = f'CEE MCQ, {subject.name}, CEE Nepal, Chapters, Practice Questions'
    request.page_slug = slug

    chapter_ids = [c.id for c in chapters_list]
    chapter_solution_sets = {}
    for sol_set in SolutionSet.objects.filter(chapter_id__in=chapter_ids).select_related('chapter'):
        chap_slug = sol_set.chapter.slug
        chapter_solution_sets.setdefault(chap_slug, []).append(sol_set)

    return render(request, 'chapter.html', {
        'subject': subject,
        'chapters': chapters_list,
        'chapter_solution_sets': chapter_solution_sets,
        **_crawl_navigation_links(subject.slug),
        'page_slug': slug,
        'page_seo': _subject_defaults(subject.name),
        'page_default_title': page_default_title,
        'page_default_description': page_default_description,
        'page_default_keywords': page_default_keywords,
        'page_default_og_title': f'{subject.name} Chapters | CEE MCQ',
        'page_default_og_description': f"Practice chapter wise MCQ questions for {subject.name}. Prepare for Nepal's Common Entrance Examination.",
    })


def chapters_redirect(request, subject_id):
    """Redirect old numeric subject URL to slug URL (301)."""
    subject = get_object_or_404(Subject, id=subject_id)
    return redirect('chapters', slug=subject.slug, permanent=True)


def _slug_aliases(page_slug):
    aliases = [page_slug]
    for suffix in ('-mcq', '-mc', '-quiz', '-questions'):
        if page_slug.endswith(suffix):
            trimmed = page_slug[: -len(suffix)]
            if trimmed:
                aliases.append(trimmed)
    return aliases


def dynamic_page(request, page_slug):
    """Redirect SEO alias slugs such as /physics-mcq/ to the canonical subject page (301)."""
    request.page_slug = page_slug
    slug_options = _slug_aliases(page_slug)

    for candidate in slug_options:
        subject = Subject.objects.filter(slug=candidate).first()
        if subject:
            return redirect('chapters', slug=subject.slug, permanent=True)

    raise Http404('Page not found')

def quiz_redirect(request, chapter_id):
    chapter = get_object_or_404(Chapter, id=chapter_id)
    return redirect('quiz', slug=chapter.slug, permanent=True)


def subchapter_quiz_redirect(request, subchapter_id):
    sub = get_object_or_404(SubChapter, id=subchapter_id)
    return redirect('subchapter_quiz', slug=sub.slug, permanent=True)


def subchapter_quiz_legacy_redirect(request, slug):
    sub = get_object_or_404(SubChapter, slug=slug)
    return redirect('subchapter_quiz', slug=sub.slug, permanent=True)


def subchapters(request, slug):
    """View to list subchapters for a chapter that has them (lookup by slug)."""
    chapter = get_object_or_404(Chapter.objects.select_related('subject'), slug=slug)
    subchapter_list = SubChapter.objects.filter(chapter=chapter).order_by('order')
    solution_sets = SolutionSet.objects.filter(chapter=chapter)
    request.page_slug = slug
    sc_meta = _stable_variant(
        f'scmeta:{chapter.slug}',
        (SUBCHAPTERS_META_DESCRIPTIONS,),
    )[0]
    page_default_description = sc_meta.format(
        sub=chapter.name, ch=chapter.subject.name,
    )
    return render(request, 'subchapter.html', {
        'chapter': chapter,
        'subchapters': subchapter_list,
        'solution_sets': solution_sets,
        'page_default_description': page_default_description,
        **_crawl_navigation_links(chapter.subject.slug),
    })


def subchapters_redirect(request, chapter_id):
    chapter = get_object_or_404(Chapter, id=chapter_id)
    return redirect('subchapters', slug=chapter.slug, permanent=True)


def solution_set(request, slug, set_number):
    chapter = get_object_or_404(Chapter.objects.select_related('subject'), slug=slug)
    sol_set = get_object_or_404(SolutionSet, chapter=chapter, set_number=set_number)
    questions = sol_set.get_questions()
    previous_set = SolutionSet.objects.filter(chapter=chapter, set_number=set_number - 1).first()
    next_set = SolutionSet.objects.filter(chapter=chapter, set_number=set_number + 1).first()
    page_default_title = f'{chapter.name} Solved MCQs | Set {set_number} | CEE MCQ'
    ss_meta = _stable_variant(
        f'ssmeta:{slug}:{set_number}',
        (SOLVED_META_DESCRIPTIONS,),
    )[0]
    page_default_description = ss_meta.format(
        sub=chapter.name, ch=chapter.subject.name, set_no=set_number,
    )
    page_default_keywords = f'CEE MCQ, {chapter.name}, Solved MCQs, Set {set_number}, Practice Questions'
    request.page_slug = f'{slug}-solved-set-{set_number}'
    return render(request, 'solution_set.html', {
        'chapter': chapter,
        'sol_set': sol_set,
        'questions': questions,
        'previous_set': previous_set,
        'next_set': next_set,
        'page_slug': request.page_slug,
        'page_default_title': page_default_title,
        'page_default_description': page_default_description,
        'page_default_keywords': page_default_keywords,
        'page_default_og_title': page_default_title,
        'page_default_og_description': page_default_description,
        **_crawl_navigation_links(chapter.subject.slug),
    })


# def _sample_questions_for_display(queryset, count=5):
#     question_ids = list(queryset.values_list('id', flat=True))
#     if not question_ids:
#         return []
#     selected_ids = random.sample(question_ids, min(count, len(question_ids)))
#     questions = Question.objects.filter(id__in=selected_ids).select_related('chapter', 'sub_chapter')
#     id_map = {q.id: q for q in questions}
#     return [id_map[qid] for qid in selected_ids if qid in id_map]


def quiz(request, slug):
    chapter = get_object_or_404(Chapter.objects.select_related('subject'), slug=slug)
    chapter_id = chapter.id
    attempt_key_prefix = f'quiz_{chapter_id}'
    attempt_reference = request.session.get(f'{attempt_key_prefix}_attempt_reference', '')
    request.page_slug = slug
    page_default_title = f'{chapter.name} MCQ | {chapter.subject.name} | CEE MCQ'
    ch_meta_variant = _stable_variant(
        f'chmeta:{chapter.slug}',
        (QUIZ_META_DESCRIPTIONS,),
    )[0]
    page_default_description = ch_meta_variant.format(
        sub=chapter.name, ch=chapter.subject.name,
    )
    page_default_keywords = f'CEE MCQ, {chapter.name} MCQ, {chapter.subject.name}, Chapter wise Questions, Online Practice'

    if request.method == 'POST':
        if request.POST.get('start') == '1':
            user_name = _normalize_exact_name(request.POST.get('name', ''))
            if not user_name:
                messages.error(request, 'Name is required to start the test.')
                return redirect('quiz', slug=chapter.slug)

            attempt_reference = _attempt_reference(request.session, attempt_key_prefix, force_new=True)
            question_ids = _get_chapter_question_ids(chapter_id)
            questions = _pick_random_questions(question_ids, limit=50)
            if not questions:
                messages.error(request, 'No questions are available for this chapter yet. Please try again later.')
                return redirect('quiz', slug=chapter.slug)

            request.session[f'quiz_questions_{chapter_id}'] = [q.id for q in questions]
            request.session[f'quiz_name_{chapter_id}'] = user_name
            return redirect('quiz', slug=chapter.slug)

        user_name = _normalize_exact_name(request.POST.get('name', ''))
        if not user_name:
            messages.error(request, 'Name is required to submit the quiz.')
            return redirect('quiz', slug=chapter.slug)

        posted_attempt_reference = (request.POST.get('attempt_reference') or '').strip()
        if posted_attempt_reference != attempt_reference:
            messages.warning(request, 'This quiz attempt is no longer active. Please start a new attempt.')
            return redirect('chapters', slug=chapter.subject.slug)

        if _is_attempt_already_submitted(request.session, attempt_key_prefix, posted_attempt_reference):
            messages.warning(request, 'This quiz attempt was already submitted.')
            return redirect('chapters', slug=chapter.subject.slug)

        try:
            connection.ensure_connection()

            questions_ids = request.session.get(f'quiz_questions_{chapter_id}', [])
            if not questions_ids:
                raw_question_ids = request.POST.get('question_ids', '')
                questions_ids = [
                    int(value)
                    for value in raw_question_ids.split(',')
                    if value.strip().isdigit()
                ]

            if not questions_ids:
                messages.error(request, 'Session expired. Please restart the quiz.')
                return redirect('quiz', slug=chapter.slug)

            questions = _load_questions_by_ids(questions_ids, include_solution=True)

            if not questions:
                messages.error(request, 'Session data is stale. Please restart the quiz.')
                request.session.pop(f'quiz_questions_{chapter_id}', None)
                return redirect('quiz', slug=chapter.slug)

            _mark_attempt_submitted(request.session, attempt_key_prefix, posted_attempt_reference)

            total_score = 0
            total_attempted = 0
            total_correct = 0
            negative_mark = 0.25
            user_answers = {}

            for q in questions:
                answer = request.POST.get(f'q{q.id}')
                if answer:
                    user_answers[q.id] = answer
                    total_attempted += 1
                    if answer == q.correct_option:
                        total_score += 1
                        total_correct += 1
                    else:
                        total_score -= negative_mark
            
            total_questions = len(questions)
            total_wrong = total_attempted - total_correct
            total_skipped = total_questions - total_attempted
            final_score = max(total_score, 0)
            time_taken_seconds = _parse_non_negative_int(request.POST.get('time_taken_seconds'), default=0)
            result_metrics = _build_result_metrics(
                total_questions=total_questions,
                total_attempted=total_attempted,
                total_correct=total_correct,
                time_taken_seconds=time_taken_seconds,
            )

            try:
                _save_test_result(
                    user_name=user_name,
                    topic=chapter.name,
                    score=final_score,
                    total_attempted=total_attempted,
                    total_correct=total_correct,
                    time_taken_seconds=time_taken_seconds,
                )
            except Exception as db_error:
                logger.error('DB save failed for chapter quiz', exc_info=True)
                messages.warning(request, 'Result calculated but may not be saved. Please contact admin.')

            history_entries = _get_test_history(user_name=user_name)
            user_answers = _stringify_answer_keys(user_answers)

            request.session.pop(f'quiz_questions_{chapter_id}', None)

            return render(request, 'quiz.html', {
                'chapter': chapter,
                'questions': questions,
                'score': final_score,
                'user_name': user_name,
                'total_attempted': total_attempted,
                'total_correct': total_correct,
                'total_wrong': total_wrong,
                'total_skipped': total_skipped,
                'total_questions': total_questions,
                'user_answers': user_answers,
                'quiz_started': True,
                'finished': True,
                'attempt_reference': attempt_reference,
                'watermark_text': f'{user_name} | Attempt #{attempt_reference}',
                'history_entries': history_entries,
                'history_user_name': user_name,
                'question_ids_csv': ','.join(str(q.id) for q in questions),
                'page_slug': slug,
                'page_default_title': page_default_title,
                'page_default_description': page_default_description,
                'page_default_keywords': page_default_keywords,
                'page_default_og_title': page_default_title,
                'page_default_og_description': page_default_description,
                **result_metrics,
            })

        except Exception as e:
            logger.exception('Quiz submission failed for chapter %s', chapter.slug)
            messages.error(request, 'An error occurred while processing your submission. Please try again.')
            return redirect('quiz', slug=chapter.slug)

    else:
        if request.GET.get('new') == '1':
            request.session.pop(f'quiz_questions_{chapter_id}', None)
            request.session.pop(f'quiz_name_{chapter_id}', None)
            return redirect('quiz', slug=chapter.slug)

        stored_ids = request.session.get(f'quiz_questions_{chapter_id}', [])
        quiz_started = bool(stored_ids)
        user_name = request.session.get(f'quiz_name_{chapter_id}', '') if quiz_started else ''
        questions = []
        preview_questions = []

        if quiz_started:
            questions = _load_questions_by_ids(stored_ids, include_solution=False)
            if not questions:
                request.session.pop(f'quiz_questions_{chapter_id}', None)
                request.session.pop(f'quiz_name_{chapter_id}', None)
                quiz_started = False
        else:
            preview_questions = list(
                Question.objects.filter(chapter=chapter, verified=True, solution__gt='').order_by('-id')[:10]
            )

        opener_v, marking_v = _stable_variant(
            f'chblurb1:{chapter.slug}', (QUIZ_OPENERS, QUIZ_MARKING),
        )
        results_v, tail_v = _stable_variant(
            f'chblurb2:{chapter.slug}', (QUIZ_RESULTS, QUIZ_RESULT_TAILS),
        )
        samples_v, stail_v = _stable_variant(
            f'chblurbS:{chapter.slug}', (QUIZ_SAMPLES, QUIZ_SAMPLE_TAILS),
        )
        blurb_1 = ' '.join([
            opener_v.format(sub=chapter.name, ch=chapter.subject.name),
            marking_v,
        ])
        blurb_2 = ' '.join([results_v, tail_v])
        preview_subtitle = ' '.join([samples_v, stail_v])

        return render(request, 'quiz.html', {
            'chapter': chapter,
            'questions': questions,
            'preview_questions': preview_questions,
            'quiz_blurb_1': blurb_1,
            'quiz_blurb_2': blurb_2,
            'preview_subtitle': preview_subtitle,
            'score': None,
            'user_answers': {},
            'quiz_started': quiz_started,
            'finished': False,
            'attempt_reference': attempt_reference,
            'watermark_text': f'{user_name} | Attempt #{attempt_reference}' if quiz_started else '',
            'history_entries': [],
            'history_user_name': user_name,
            'question_ids_csv': ','.join(str(q.id) for q in questions),
            'page_slug': slug,
            'page_default_title': page_default_title,
            'page_default_description': page_default_description,
            'page_default_keywords': page_default_keywords,
            'page_default_og_title': page_default_title,
            'page_default_og_description': page_default_description,
            **_crawl_navigation_links(chapter.subject.slug),
        })


def subchapter_quiz(request, slug):
    """Quiz view for a specific subchapter (lookup by slug)."""
    sub_chapter = get_object_or_404(SubChapter, slug=slug)
    subchapter_id = sub_chapter.id
    chapter = sub_chapter.chapter
    session_key = f'quiz_questions_sub_{subchapter_id}'
    attempt_key_prefix = f'subchapter_{subchapter_id}'
    attempt_reference = request.session.get(f'{attempt_key_prefix}_attempt_reference', '')
    request.page_slug = slug
    page_default_title = f'{sub_chapter.name} MCQ | {chapter.name} | CEE MCQ'
    meta_variant = _stable_variant(
        f'mcq:{sub_chapter.slug}',
        (QUIZ_META_DESCRIPTIONS,),
    )[0]
    page_default_description = meta_variant.format(
        sub=sub_chapter.name, ch=chapter.name,
    )
    page_default_keywords = f'CEE MCQ, {sub_chapter.name} MCQ, {chapter.name} MCQ, Chapter wise Questions, Online Practice'

    if request.method == 'POST':
        if request.POST.get('start') == '1':
            user_name = _normalize_exact_name(request.POST.get('name', ''))
            if not user_name:
                messages.error(request, 'Name is required to start the test.')
                return redirect('subchapter_quiz', slug=sub_chapter.slug)

            attempt_reference = _attempt_reference(request.session, attempt_key_prefix, force_new=True)
            question_ids = _get_subchapter_question_ids(subchapter_id)
            questions = _pick_random_questions(question_ids, limit=50)
            if not questions:
                messages.error(request, 'No questions are available for this subchapter yet. Please try again later.')
                return redirect('subchapter_quiz', slug=sub_chapter.slug)

            request.session[session_key] = [q.id for q in questions]
            request.session[f'quiz_name_sub_{subchapter_id}'] = user_name
            return redirect('subchapter_quiz', slug=sub_chapter.slug)

        user_name = _normalize_exact_name(request.POST.get('name', ''))
        if not user_name:
            messages.error(request, 'Name is required to submit the quiz.')
            return redirect('subchapter_quiz', slug=sub_chapter.slug)

        posted_attempt_reference = (request.POST.get('attempt_reference') or '').strip()
        if posted_attempt_reference != attempt_reference:
            messages.warning(request, 'This quiz attempt is no longer active. Please start a new attempt.')
            return redirect('chapters', slug=chapter.subject.slug)

        if _is_attempt_already_submitted(request.session, attempt_key_prefix, posted_attempt_reference):
            messages.warning(request, 'This quiz attempt was already submitted.')
            return redirect('chapters', slug=chapter.subject.slug)

        try:
            connection.ensure_connection()

            questions_ids = request.session.get(session_key, [])
            if not questions_ids:
                raw_question_ids = request.POST.get('question_ids', '')
                questions_ids = [
                    int(value)
                    for value in raw_question_ids.split(',')
                    if value.strip().isdigit()
                ]

            if not questions_ids:
                messages.error(request, 'Session expired. Please restart the quiz.')
                return redirect('subchapter_quiz', slug=sub_chapter.slug)

            questions = _load_questions_by_ids(questions_ids, include_solution=True)

            if not questions:
                messages.error(request, 'Session data is stale. Please restart the quiz.')
                request.session.pop(session_key, None)
                return redirect('subchapter_quiz', slug=sub_chapter.slug)

            _mark_attempt_submitted(request.session, attempt_key_prefix, posted_attempt_reference)

            total_score = 0
            total_attempted = 0
            total_correct = 0
            negative_mark = 0.25
            user_answers = {}

            for q in questions:
                answer = request.POST.get(f'q{q.id}')
                if answer:
                    user_answers[q.id] = answer
                    total_attempted += 1
                    if answer == q.correct_option:
                        total_score += 1
                        total_correct += 1
                    else:
                        total_score -= negative_mark

            total_questions = len(questions)
            total_wrong = total_attempted - total_correct
            total_skipped = total_questions - total_attempted
            final_score = max(total_score, 0)
            time_taken_seconds = _parse_non_negative_int(request.POST.get('time_taken_seconds'), default=0)
            result_metrics = _build_result_metrics(
                total_questions=total_questions,
                total_attempted=total_attempted,
                total_correct=total_correct,
                time_taken_seconds=time_taken_seconds,
            )

            try:
                _save_test_result(
                    user_name=user_name,
                    topic=f"{chapter.name} - {sub_chapter.name}",
                    score=final_score,
                    total_attempted=total_attempted,
                    total_correct=total_correct,
                    time_taken_seconds=time_taken_seconds,
                )
            except Exception as db_error:
                logger.error('DB save failed for subchapter quiz', exc_info=True)
                messages.warning(request, 'Result calculated but may not be saved. Please contact admin.')

            history_entries = _get_test_history(user_name=user_name)
            user_answers = _stringify_answer_keys(user_answers)

            request.session.pop(session_key, None)

            return render(request, 'quiz.html', {
                'chapter': chapter,
                'sub_chapter': sub_chapter,
                'questions': questions,
                'score': final_score,
                'user_name': user_name,
                'total_attempted': total_attempted,
                'total_correct': total_correct,
                'total_wrong': total_wrong,
                'total_skipped': total_skipped,
                'total_questions': total_questions,
                'user_answers': user_answers,
                'quiz_started': True,
                'finished': True,
                'show_review_modal': True,
                'attempt_reference': attempt_reference,
                'watermark_text': f'{user_name} | Attempt #{attempt_reference}',
                'history_entries': history_entries,
                'history_user_name': user_name,
                'question_ids_csv': ','.join(str(q.id) for q in questions),
                'subchapter': sub_chapter,
                'page_slug': slug,
                'page_default_title': page_default_title,
                'page_default_description': page_default_description,
                'page_default_keywords': page_default_keywords,
                'page_default_og_title': page_default_title,
                'page_default_og_description': page_default_description,
                **result_metrics,
            })

        except Exception as e:
            logger.exception('Subchapter quiz submission failed for %s', sub_chapter.slug)
            messages.error(request, 'An error occurred while processing your submission. Please try again.')
            return redirect('subchapter_quiz', slug=sub_chapter.slug)

    else:
        if request.GET.get('new') == '1':
            request.session.pop(session_key, None)
            request.session.pop(f'quiz_name_sub_{subchapter_id}', None)
            return redirect('subchapter_quiz', slug=sub_chapter.slug)

        stored_ids = request.session.get(session_key, [])
        quiz_started = bool(stored_ids)
        user_name = request.session.get(f'quiz_name_sub_{subchapter_id}', '') if quiz_started else ''
        questions = []
        preview_questions = []

        if quiz_started:
            questions = _load_questions_by_ids(stored_ids, include_solution=False)
            if not questions:
                request.session.pop(session_key, None)
                request.session.pop(f'quiz_name_sub_{subchapter_id}', None)
                quiz_started = False
        else:
            preview_questions = list(
                Question.objects.filter(sub_chapter=sub_chapter, verified=True, solution__gt='').order_by('id')[:10]
            )

        opener_v, marking_v = _stable_variant(
            f'blurb1:{sub_chapter.slug}', (QUIZ_OPENERS, QUIZ_MARKING),
        )
        results_v, tail_v = _stable_variant(
            f'blurb2:{sub_chapter.slug}', (QUIZ_RESULTS, QUIZ_RESULT_TAILS),
        )
        samples_v, stail_v = _stable_variant(
            f'blurbS:{sub_chapter.slug}', (QUIZ_SAMPLES, QUIZ_SAMPLE_TAILS),
        )
        blurb_1 = ' '.join([
            opener_v.format(sub=sub_chapter.name, ch=chapter.name),
            marking_v,
        ])
        blurb_2 = ' '.join([results_v, tail_v])
        preview_subtitle = ' '.join([samples_v, stail_v])

        return render(request, 'quiz.html', {
            'chapter': chapter,
            'sub_chapter': sub_chapter,
            'subchapter': sub_chapter,
            'questions': questions,
            'preview_questions': preview_questions,
            'score': None,
            'user_answers': {},
            'quiz_started': quiz_started,
            'finished': False,
            'attempt_reference': attempt_reference,
            'watermark_text': f'{user_name} | Attempt #{attempt_reference}' if quiz_started else '',
            'history_entries': [],
            'history_user_name': user_name,
            'question_ids_csv': ','.join(str(q.id) for q in questions),
            'quiz_blurb_1': blurb_1,
            'quiz_blurb_2': blurb_2,
            'preview_subtitle': preview_subtitle,
            'page_slug': slug,
            'page_default_title': page_default_title,
            'page_default_description': page_default_description,
            'page_default_keywords': page_default_keywords,
            'page_default_og_title': page_default_title,
            'page_default_og_description': page_default_description,
        })


def full_test(request):
    result_session_key = 'full_test_result_data'
    attempt_key_prefix = 'full_test'
    attempt_reference = request.session.get(f'{attempt_key_prefix}_attempt_reference', '')
    request.page_slug = 'full-test'
    page_default_title = 'CEE Full Mock Test | 200 Questions Online | CEE MCQ'
    page_default_description = 'Take a full CEE mock test online with 200 questions, negative marking, and a 3 hour timer. Simulate the real MEC entrance exam experience.'
    page_default_keywords = 'CEE full test, CEE mock test Nepal, CEE online test, MEC full mock test, CEE 200 questions, CEE practice exam'
    if request.method == "POST":
        if request.POST.get('start') == '1':
            user_name = _normalize_exact_name(request.POST.get('name', ''))
            if not user_name:
                messages.error(request, 'Name is required to start the test.')
                return redirect('full_test')

            attempt_reference = _attempt_reference(request.session, attempt_key_prefix, force_new=True)
            selected_ids = _build_full_test_question_ids()
            questions = _load_questions_by_ids(selected_ids, include_solution=False)

            request.session['full_test_questions'] = [q.id for q in questions]
            request.session['full_test_user_name'] = user_name
            request.session.pop(result_session_key, None)
            return redirect('full_test')

        user_name = _normalize_exact_name(request.POST.get('name', ''))
        if not user_name:
            messages.error(request, 'Name is required to submit the test.')
            return redirect('full_test')

        posted_attempt_reference = (request.POST.get('attempt_reference') or '').strip()
        if posted_attempt_reference != attempt_reference:
            messages.warning(request, 'This full test attempt is no longer active. Please start a new attempt.')
            return redirect('home')

        if _is_attempt_already_submitted(request.session, attempt_key_prefix, posted_attempt_reference):
            messages.warning(request, 'This full test attempt was already submitted.')
            return redirect('home')
        
        try:
            # Ensure database connection is active
            connection.ensure_connection()
            
            questions_ids = request.session.get('full_test_questions', [])
            if not questions_ids:
                raw_question_ids = request.POST.get('question_ids', '')
                questions_ids = [
                    int(value)
                    for value in raw_question_ids.split(',')
                    if value.strip().isdigit()
                ]
            
            # Check if session data exists
            if not questions_ids:
                messages.error(request, 'Session expired. Please restart the test.')
                return redirect('full_test')

            questions = _load_questions_by_ids(questions_ids, include_solution=True)

            if not questions:
                messages.error(request, 'Session data is stale. Please restart the test.')
                request.session.pop('full_test_questions', None)
                return redirect('full_test')

            _mark_attempt_submitted(request.session, attempt_key_prefix, posted_attempt_reference)
            
            total_score = 0
            total_attempted = 0
            total_correct = 0
            negative_mark = 0.25
            user_answers = {}
            
            for q in questions:
                answer = request.POST.get(f'q{q.id}')
                if answer:
                    user_answers[q.id] = answer
                    total_attempted += 1
                    if answer == q.correct_option:
                        total_score += 1
                        total_correct += 1
                    else:
                        total_score -= negative_mark
            
            total_questions = len(questions)
            total_wrong = total_attempted - total_correct
            total_skipped = total_questions - total_attempted
            final_score = max(total_score, 0)
            time_taken_seconds = _parse_non_negative_int(request.POST.get('time_taken_seconds'), default=0)
            result_metrics = _build_result_metrics(
                total_questions=total_questions,
                total_attempted=total_attempted,
                total_correct=total_correct,
                time_taken_seconds=time_taken_seconds,
            )
            
            # Save result with retry logic
            try:
                _save_test_result(
                    user_name=user_name,
                    topic="Full Test",
                    score=final_score,
                    total_attempted=total_attempted,
                    total_correct=total_correct,
                    time_taken_seconds=time_taken_seconds,
                )
            except Exception as db_error:
                logger.error('DB save failed for full test', exc_info=True)
                messages.warning(request, 'Result calculated but may not be saved. Please contact admin.')

            user_answers = _stringify_answer_keys(user_answers)
            request.session.pop('full_test_questions', None)

            request.session[result_session_key] = {
                'question_ids': [q.id for q in questions],
                'user_answers': user_answers,
                'user_name': user_name,
                'total_attempted': total_attempted,
                'total_correct': total_correct,
                'total_wrong': total_wrong,
                'total_skipped': total_skipped,
                'total_questions': total_questions,
                'score': final_score,
                'attempt_reference': attempt_reference,
                'result_metrics': result_metrics,
            }
            request.session.modified = True

            return redirect('full_test_results')
            
        except Exception as e:
            logger.exception('Full test submission failed for user %s', user_name)
            messages.error(request, 'An error occurred while processing your submission. Please try again.')
            return redirect('full_test')

    else:
        if request.GET.get('new') == '1':
            request.session.pop('full_test_questions', None)
            request.session.pop('full_test_user_name', None)
            request.session.pop(result_session_key, None)
            return redirect('full_test')

        stored_ids = request.session.get('full_test_questions', [])
        quiz_started = bool(stored_ids)
        user_name = request.session.get('full_test_user_name', '') if quiz_started else ''

        if not quiz_started:
            request.session.pop(result_session_key, None)
            return render(request, 'full_test.html', {
                'questions': [],
                'score': None,
                'quiz_started': False,
                'user_answers': {},
                'finished': False,
                'attempt_reference': attempt_reference,
                'watermark_text': '',
                'history_entries': [],
                'history_user_name': user_name,
                'page_slug': 'full-test',
                'page_default_title': page_default_title,
                'page_default_description': page_default_description,
                'page_default_keywords': page_default_keywords,
                'page_default_og_title': page_default_title,
                'page_default_og_description': page_default_description,
                **_crawl_navigation_links(),
            })

        questions = _load_questions_by_ids(stored_ids, include_solution=False)

        if not questions:
            request.session.pop('full_test_questions', None)
            request.session.pop('full_test_user_name', None)
            request.session.pop(result_session_key, None)
            return redirect('full_test')

        return render(request, 'full_test.html', {
            'questions': questions,
            'score': None,
            'quiz_started': True,
            'user_answers': {},
            'finished': False,
            'attempt_reference': attempt_reference,
            'watermark_text': f'{user_name} | Attempt #{attempt_reference}',
            'history_entries': [],
            'history_user_name': user_name,
            'question_ids_csv': ','.join(str(q.id) for q in questions),
            'page_slug': 'full-test',
            'page_default_title': page_default_title,
            'page_default_description': page_default_description,
            'page_default_keywords': page_default_keywords,
            'page_default_og_title': page_default_title,
            'page_default_og_description': page_default_description,
            **_crawl_navigation_links(),
        })


def full_test_exit(request):
    request.session.pop('full_test_questions', None)
    request.session.pop('full_test_user_name', None)
    request.session.pop('full_test_result_data', None)
    return redirect('home')


def quiz_exit(request, slug):
    chapter = get_object_or_404(Chapter, slug=slug)
    request.session.pop(f'quiz_questions_{chapter.id}', None)
    request.session.pop(f'quiz_name_{chapter.id}', None)
    return redirect('chapters', slug=chapter.subject.slug)


def subchapter_quiz_exit(request, slug):
    sub_chapter = get_object_or_404(SubChapter, slug=slug)
    request.session.pop(f'quiz_questions_sub_{sub_chapter.id}', None)
    request.session.pop(f'quiz_name_sub_{sub_chapter.id}', None)
    return redirect('chapters', slug=sub_chapter.chapter.subject.slug)


def full_test_results(request):
    request.page_slug = 'full-test'
    # Default page metadata for full test results
    page_default_title = 'CEE Full Mock Test | 200 Questions Online | CEE MCQ'
    page_default_description = 'Take a full CEE mock test online with 200 questions, negative marking, and a 3 hour timer. Simulate the real MEC entrance exam experience.'
    page_default_keywords = 'CEE full test, CEE mock test Nepal, CEE online test, MEC full mock test, CEE 200 questions, CEE practice exam'
    # Consume the stored result data so visiting the results URL directly won't re-show old results.
    result_payload = request.session.pop('full_test_result_data', None)
    if not result_payload:
        messages.error(request, 'No completed test result found. Please take the test first.')
        return redirect('full_test')

    question_ids = result_payload.get('question_ids') or []
    if not question_ids:
        messages.error(request, 'Result data is incomplete. Please retake the test.')
        return redirect('full_test')

    try:
        connection.ensure_connection()
        questions = _load_questions_by_ids(question_ids, include_solution=True)
    except Exception as error:
        logger.exception('Failed to load test results')
        messages.error(request, 'Unable to load test results. Please retake the test.')
        return redirect('full_test')

    if not questions:
        messages.error(request, 'Result questions are no longer available. Please retake the test.')
        return redirect('full_test')

    raw_user_answers = result_payload.get('user_answers') or {}
    user_answers = {}
    for key, value in raw_user_answers.items():
        try:
            normalized_key = int(key)
        except (TypeError, ValueError):
            normalized_key = key
        user_answers[normalized_key] = value

    result_metrics = result_payload.get('result_metrics') or {}
    user_name = result_payload.get('user_name', '')
    attempt_reference = result_payload.get('attempt_reference', '')
    history_entries = _get_test_history(user_name=user_name)
    subject_breakdown = _build_full_test_subject_breakdown(questions, user_answers)

    return render(request, 'full_test.html', {
        'questions': questions,
        'score': result_payload.get('score', 0),
        'user_name': user_name,
        'total_attempted': result_payload.get('total_attempted', 0),
        'total_correct': result_payload.get('total_correct', 0),
        'total_wrong': result_payload.get('total_wrong', 0),
        'total_skipped': result_payload.get('total_skipped', 0),
        'total_questions': result_payload.get('total_questions', len(questions)),
        'user_answers': user_answers,
        'quiz_started': True,
        'finished': True,
        'attempt_reference': attempt_reference,
        'watermark_text': f'{user_name} | Attempt #{attempt_reference}' if user_name and attempt_reference else '',
        'history_entries': history_entries,
        'history_user_name': user_name,
        'question_ids_csv': ','.join(str(q.id) for q in questions),
        'page_slug': 'full-test',
        'page_default_title': page_default_title,
        'page_default_description': page_default_description,
        'page_default_keywords': page_default_keywords,
        'page_default_og_title': page_default_title,
        'page_default_og_description': page_default_description,
        'subject_breakdown': subject_breakdown,
        **_crawl_navigation_links(),
        **result_metrics,
    })


def privacy_policy(request):
    return redirect('privacy_policy', permanent=True)


def privacy_policy_redirect(request):
    return redirect('privacy_policy', permanent=True)


def privacy_policy_page(request):
    return render(request, 'privacy_policy.html')


def about(request):
    return render(request, 'about.html')


def disclaimer(request):
    return render(request, 'disclaimer.html')


def terms_of_service(request):
    return render(request, 'terms-of-service.html')


def contact(request):
    if request.method == 'POST':
        name = (request.POST.get('name') or '').strip()
        email = (request.POST.get('email') or '').strip()
        message = (request.POST.get('message') or '').strip()

        if not name or not email or not message:
            messages.error(request, 'Please fill in all contact fields.')
        else:
            subject = f'Website contact from {name}'
            body = f'From: {name} <{email}>\n\n{message}'
            try:
                send_mail(
                    subject,
                    body,
                    getattr(settings, 'DEFAULT_FROM_EMAIL', email),
                    ['pandeyramu57@gmail.com'],
                )
                messages.success(request, 'Thanks for reaching out. We will get back to you soon.')
            except Exception:
                logger.exception('Failed to send contact email from contact() view')
                messages.error(request, 'Something went wrong sending your message. Please email us directly instead.')

    return render(request, 'contact.html')

def ads_txt(request):
    try:
        with open(settings.BASE_DIR / 'static' / 'ads.txt', 'r', encoding='utf-8') as ads_file:
            content = ads_file.read()
    except FileNotFoundError:
        content = 'google.com, pub-3880021540956659, DIRECT, f08c47fec0942fa0'
    return HttpResponse(content, content_type='text/plain')


def llms_txt(request):
    content = (
        "# CEE MCQ\n\n"
        "> Free CEE practice questions for Nepal's Common Entrance Examination (CEE).\n\n"
        "CEE MCQ (https://pandeyramu.com.np) is a free, ad-supported practice platform for students preparing "
        "for the Common Entrance Examination conducted by Nepal's Medical Education Commission (MEC). It offers "
        "47,000+ chapter-wise MCQs across Physics, Chemistry, Zoology, Botany and MAT, each with a step-by-step "
        "solution. Every test applies the real exam's negative marking (+1 / -0.25) and a timer.\n\n"
        "## Key facts\n"
        "- Exam format: 200 MCQs in 3 hours - Physics 50, Chemistry 50, Biology (Zoology + Botany) 80, MAT 20.\n"
        "- Marking: +1 for a correct answer, -0.25 for an incorrect answer, maximum score 200.\n"
        "- Highest weightage topics: Human Biology and Physiology (15), Physical Chemistry (17), Organic Chemistry (17), Modern Physics (12), Mechanics (10).\n"
        "- The Biology section is split equally: Zoology 40 questions, Botany 40 questions.\n\n"
        "## Core pages\n"
        "- Home: https://pandeyramu.com.np/\n"
        "- All subjects: https://pandeyramu.com.np/all-subjects/\n"
        "- Full mock test: https://pandeyramu.com.np/full-test/\n"
        "- About: https://pandeyramu.com.np/about/\n"
        "- Contact: https://pandeyramu.com.np/contact/\n"
        "- Blog: https://pandeyramu.com.np/blog/\n"
    )
    return HttpResponse(content, content_type='text/plain; charset=utf-8')


def blog_index(request):
    request.page_slug = 'blog'
    posts = []
    for slug in BLOG_POST_ORDER:
        meta = BLOG_POST_META[slug]
        posts.append({
            'slug': slug,
            'title': meta['title'],
            'tag': meta['tag'],
            'excerpt': meta['excerpt'],
            'accent': meta['accent'],
            'accent_soft': meta['accent_soft'],
            'accent_border': meta['accent_border'],
        })
    return render(request, 'blog.html', {'posts': posts})

def blog_post(request, slug):
    request.page_slug = f'blog/{slug}'
    template_name = BLOG_POST_TEMPLATES.get(slug)
    if not template_name:
        raise Http404('Blog post not found')

    related = []
    for related_slug in BLOG_RELATED.get(slug, []):
        meta = BLOG_POST_META[related_slug]
        related.append({
            'slug': related_slug,
            'title': meta['title'],
            'tag': meta['tag'],
            'accent': meta['accent'],
        })

    return render(request, template_name, {'slug': slug, 'related_posts': related})