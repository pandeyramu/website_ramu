from genericpath import exists
import random
import re
import uuid
import json
import socket
import logging
from functools import lru_cache
import requests
from django.contrib.sites.requests import RequestSite
from django.urls import reverse
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.http import Http404, HttpResponse, JsonResponse
from django.views.decorators.cache import cache_page
from django.views.decorators.csrf import csrf_exempt
from django.db import connection, IntegrityError
from django.db.utils import DatabaseError
from django.core.mail import send_mail
from django.conf import settings
from .models import Subject, Chapter, SubChapter, Question, TestResult, PageSEO, QuestionReport
from .sitemaps import sitemaps
from .seo_provider import get_supabase_page_seo


logger = logging.getLogger(__name__)
TEST_HISTORY_LIMIT = 5


def _ordered_subjects():
    return list(Subject.objects.only('id', 'name', 'slug').order_by('id'))


def _subject_alias_url(subject_slug):
    return f'/{subject_slug}-mcq/' if subject_slug else '/'


def _crawl_navigation_links(subject_slug=None):
    links = {
        'all_subjects_url': reverse('all_subjects'),
        'all_mcq_url': reverse('all_mcq'),
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
            'description': f'Go straight to {subject.name} chapter-wise practice and crawl the full {subject.name} topic tree.',
        })
    hubs.append({
        'name': 'All Subjects',
        'url': reverse('all_subjects'),
        'description': 'Browse every subject landing page from one hub.',
    })
    hubs.append({
        'name': 'All MCQ',
        'url': reverse('all_mcq'),
        'description': 'Open the direct MCQ landing pages and keep crawl paths short.',
    })
    hubs.append({
        'name': 'Full Test',
        'url': reverse('full_test'),
        'description': 'Run the full mock test and reinforce the strongest exam-level URL.',
    })
    return hubs


@csrf_exempt
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


BLOG_POSTS = {
    'how-to-prepare-for-cee': {
        'title': 'How to Prepare for CEE Effectively',
        'tag': 'Study Tips',
        'accent': '#1458a6',
        'accent_soft': 'rgba(20, 88, 166, 0.08)',
        'accent_border': 'rgba(20, 88, 166, 0.22)',
        'description': 'A practical CEE preparation roadmap covering study planning, revision cycles, and mock test strategy for Biology, Chemistry, Physics, and MAT.',
        'excerpt': 'Build a realistic routine, focus on high-weightage chapters, and use timed practice to steadily improve your CEE score.',
        'sections': [
            {
                'heading': 'Start with a realistic 12-week plan',
                'paragraphs': [
                    'Most students fail not because they are weak in concepts but because they study without structure. Begin by splitting your preparation into three phases: foundation, consolidation, and test simulation.',
                    'In the foundation phase, revise core theory and formulas. In consolidation, solve chapter-wise MCQs daily and track weak areas. In the simulation phase, shift heavily to timed mixed tests and error analysis.'
                ],
                'bullets': [
                    'Weeks 1 to 4: concept revision and short chapter tests',
                    'Weeks 5 to 8: mixed chapter drills and topic repair',
                    'Weeks 9 to 12: full-length tests with strict timing'
                ]
            },
            {
                'heading': 'Use weightage to prioritize your effort',
                'paragraphs': [
                    'Not every chapter has equal impact on rank. Start with high-weightage units in Biology, Physics, and Chemistry so you build score quickly while confidence rises.',
                    'This does not mean skipping low-weightage chapters. Cover them after core topics, but give revision frequency according to marks impact.'
                ],
                'bullets': [
                    'Biology: Human biology, cell biology, genetics',
                    'Physics: Mechanics, current electricity, magnetism',
                    'Chemistry: General/physical plus organic core reactions',
                    'MAT: daily short drills to build speed and pattern recognition'
                ]
            },
            {
                'heading': 'Turn mistakes into a score-improvement system',
                'paragraphs': [
                    'After every quiz, maintain an error log with three labels: concept gap, careless mistake, and time-pressure guess. Review this log before every weekend test.',
                    'Your score improves fastest when you fix repeated errors, not when you keep solving random new questions without reflection.'
                ],
                'bullets': [
                    'Write one-line reason for every wrong answer',
                    'Re-attempt error-log questions after 3 days and 7 days',
                    'Track accuracy by subject, then by chapter'
                ]
            },
            {
                'heading': 'Mock test strategy for exam day confidence',
                'paragraphs': [
                    'Practice full tests in exam-like conditions: same time slot, no phone, and fixed duration. This trains endurance and pacing, which directly improves final rank.',
                    'Use a simple attempt rule: first secure easy marks, then medium questions, and finally return to difficult ones if time remains.'
                ],
                'bullets': [
                    'Attempt easy and familiar questions in first pass',
                    'Avoid long stalls on one question',
                    'Reserve final 10 minutes for review and marked questions'
                ]
            }
        ]
    },
    'physics-high-weightage-topics': {
        'title': 'High Weightage Physics Topics for CEE',
        'tag': 'Physics',
        'accent': '#0f7a8a',
        'accent_soft': 'rgba(15, 122, 138, 0.08)',
        'accent_border': 'rgba(15, 122, 138, 0.22)',
        'description': 'Focused guide to high-weightage Physics units for CEE with chapter priorities, question patterns, and smart practice methods.',
        'excerpt': 'Prioritize Mechanics, Current Electricity, and Magnetism, then build accuracy through formula recall and timed mixed sets.',
        'sections': [
            {
                'heading': 'Where most Physics marks come from',
                'paragraphs': [
                    'Physics can be scoring if preparation is selective and consistent. In many CEE patterns, Mechanics and Electricity-related chapters carry a large share of marks.',
                    'The goal is to master recurring question types first, then expand to the rest of the syllabus.'
                ],
                'bullets': [
                    'Mechanics: vectors, Newton laws, work-energy, circular motion',
                    'Current electricity and magnetism: circuits, Ohm/Kirchhoff, force and field',
                    'Electrostatics and capacitors: frequent conceptual numericals'
                ]
            },
            {
                'heading': 'Study method that improves both speed and accuracy',
                'paragraphs': [
                    'Many students know formulas but lose marks due to unit conversion, sign errors, or poor diagram interpretation. Make formula revision active, not passive.',
                    'Use short 20-question sets and review every wrong answer immediately to lock learning while memory is fresh.'
                ],
                'bullets': [
                    'Maintain one formula notebook with standard SI units',
                    'Draw diagrams before solving field and motion problems',
                    'Do daily 30 to 45 minutes of mixed numericals'
                ]
            },
            {
                'heading': 'Weekly Physics schedule that works',
                'paragraphs': [
                    'Split week by goal: two days concept, three days MCQ drills, one day mixed revision, one day timed section test. This rhythm prevents forgetting and improves exam stamina.',
                    'Track chapter-wise accuracy so you know whether to increase revision or move ahead.'
                ],
                'bullets': [
                    'Target 80%+ accuracy in top-weightage chapters',
                    'Revisit weak chapters every week, not once a month',
                    'Use chapter quizzes followed by one combined Physics mini-test'
                ]
            }
        ]
    },
    'human-biology-cee-questions': {
        'title': 'Human Biology: Most Important CEE Questions',
        'tag': 'Biology',
        'accent': '#1f8a4c',
        'accent_soft': 'rgba(31, 138, 76, 0.08)',
        'accent_border': 'rgba(31, 138, 76, 0.22)',
        'description': 'High-yield Human Biology revision guide for CEE with commonly tested systems, diagrams, and MCQ preparation tactics.',
        'excerpt': 'Human Biology is a major scoring area in CEE. Focus on repeated concepts, terminology precision, and diagram-based revision.',
        'sections': [
            {
                'heading': 'Why Human Biology deserves priority',
                'paragraphs': [
                    'Human biology usually contributes significant marks and includes many predictable concept clusters. With focused revision, this section can become one of your strongest scoring blocks.',
                    'The key is not reading everything repeatedly; instead, revise tested topics in cycles and solve targeted MCQs.'
                ],
                'bullets': [
                    'Digestive, respiratory, circulatory, nervous, and endocrine systems',
                    'Human diseases and prevention principles',
                    'Homeostasis and organ-level integration'
                ]
            },
            {
                'heading': 'How to study for retention',
                'paragraphs': [
                    'Biology mistakes often come from confusing similar terms. Build memory anchors with concise comparison tables and flowcharts.',
                    'After each chapter, answer at least 40 mixed MCQs and revisit mistakes after 48 hours.'
                ],
                'bullets': [
                    'Use one-page summaries for each body system',
                    'Practice statement-based and assertion-reason questions',
                    'Revise medical vocabulary with short flashcards'
                ]
            },
            {
                'heading': 'Exam strategy for biology section',
                'paragraphs': [
                    'Start with direct factual questions, then move to conceptual integration questions. Avoid overthinking simple recall items; save time for interpretation-based MCQs.',
                    'Use elimination method aggressively when two options seem close.'
                ],
                'bullets': [
                    'Mark uncertain questions and revisit in final review',
                    'Prioritize accuracy to protect score under negative marking',
                    'Keep a final-day checklist of common confusion points'
                ]
            }
        ]
    },
    'organic-chemistry-cee-tips': {
        'title': 'Organic Chemistry Tips for CEE Nepal',
        'tag': 'Chemistry',
        'accent': '#b36a00',
        'accent_soft': 'rgba(179, 106, 0, 0.08)',
        'accent_border': 'rgba(179, 106, 0, 0.24)',
        'description': 'Organic Chemistry preparation guide for CEE Nepal with high-weightage reactions, functional-group strategy, and exam-focused MCQ methods.',
        'excerpt': 'Organic Chemistry carries major weight in CEE. Use reaction maps, functional-group logic, and repeated MCQ drills to convert it into a scoring section.',
        'sections': [
            {
                'heading': 'Why Organic Chemistry can decide your Chemistry score',
                'paragraphs': [
                    'In many CEE patterns, Organic Chemistry contributes around 18 marks, equal to other major chemistry blocks. Students who prepare Organic selectively and systematically gain a large scoring advantage.',
                    'Most losses in this section happen from poor reaction recall, confusion between similar reagents, and weak distinction tests. A structured method can fix all three in a few weeks.'
                ],
                'bullets': [
                    'High-return topics: hydrocarbons, alcohols, carbonyl compounds, carboxylic acids, amines',
                    'Frequently tested concepts: IUPAC naming, reaction conditions, identifying final products',
                    'Scoring lever: master distinction tests and common conversions'
                ]
            },
            {
                'heading': 'Use functional-group clusters instead of chapter-by-chapter memorization',
                'paragraphs': [
                    'Instead of memorizing isolated reactions, build conversion chains by functional group. This helps you solve product prediction questions faster and reduces memory overload.',
                    'For example, connect hydrocarbon to haloalkane to alcohol to aldehyde/ketone to acid. When the chain is clear, many MCQs become direct pattern matches.'
                ],
                'bullets': [
                    'Maintain one reaction-map page and revise it every 2 days',
                    'Tag reactions as oxidation, reduction, substitution, elimination, or addition',
                    'Learn key reagents with conditions and expected product type'
                ]
            },
            {
                'heading': 'Most important reaction families for CEE',
                'paragraphs': [
                    'CEE often asks direct outcome and reagent-choice questions from recurring reaction families. Prepare these first before moving to low-frequency content.',
                    'Focus especially on mechanisms and exception behavior, because options are usually designed to trap superficial memorization.'
                ],
                'bullets': [
                    'Alkene addition and Markovnikov orientation',
                    'Alcohol oxidation and dehydration behavior',
                    'Aldehyde/ketone distinction via Tollens and Fehling tests',
                    'Esterification and hydrolysis in acid/basic medium',
                    'Amines classification and typical test reactions'
                ]
            },
            {
                'heading': 'A weekly routine that improves retention',
                'paragraphs': [
                    'Organic performance rises when reaction recall is frequent and timed. Use short daily mixed sets rather than long irregular sessions.',
                    'End every week with a timed organic-only mini test and a focused error correction session.'
                ],
                'bullets': [
                    'Day 1-2: concept and reaction-map revision',
                    'Day 3-5: 30-40 MCQs daily from mixed organic topics',
                    'Day 6: distinction tests and exception sheet revision',
                    'Day 7: timed test + error log update'
                ]
            },
            {
                'heading': 'Quick FAQ for common exam traps',
                'paragraphs': [
                    'Q: Why do students lose easy marks in organic? A: They forget conditions and confuse similar reagents.',
                    'Q: Is mechanism depth needed for CEE? A: Basic mechanism logic is enough to avoid most trap options.',
                    'Q: What should be revised in the final week? A: Reaction map, exception sheet, and your personal error log.'
                ],
                'bullets': [
                    'Do not rely only on passive reading of reaction charts',
                    'Always practice product prediction with timed questions',
                    'Re-attempt wrong MCQs after 48 hours'
                ]
            }
        ]
    },
    'mat-section-tips': {
        'title': 'How to Score Full Marks in MAT Section',
        'tag': 'MAT',
        'accent': '#7a4dc7',
        'accent_soft': 'rgba(122, 77, 199, 0.08)',
        'accent_border': 'rgba(122, 77, 199, 0.22)',
        'description': 'High-scoring MAT strategy for CEE with daily drill design, speed-control techniques, and trap-avoidance methods.',
        'excerpt': 'MAT is one of the fastest sections to improve. A disciplined daily routine can convert it into reliable marks with low preparation cost.',
        'sections': [
            {
                'heading': 'Why MAT is a high-return scoring section',
                'paragraphs': [
                    'Many candidates ignore MAT until the last stage, but this section rewards routine pattern practice more than heavy theory. That makes it an efficient score booster.',
                    'A short daily MAT plan improves both speed and confidence, and it also sharpens test temperament for other sections.'
                ],
                'bullets': [
                    'Small daily effort often gives large mark gains',
                    'MAT accuracy rises quickly with repetition and review',
                    'Good MAT pacing helps overall time management in CEE'
                ]
            },
            {
                'heading': 'A practical 30-minute daily MAT routine',
                'paragraphs': [
                    'Use a fixed mini-routine every day: verbal reasoning, numerical patterns, sequence logic, and abstract pattern recognition. Keep each set timed.',
                    'Your goal is to gradually reduce average solve time while preserving accuracy. Avoid uncontrolled speed; controlled speed is what wins marks.'
                ],
                'bullets': [
                    '8 minutes: verbal and analogy questions',
                    '8 minutes: numerical and arithmetic logic',
                    '7 minutes: sequence and arrangement patterns',
                    '7 minutes: abstract or figure-based reasoning'
                ]
            },
            {
                'heading': 'Common mistakes and how to avoid them',
                'paragraphs': [
                    'Most MAT errors are not from lack of ability but from avoidable habits: rushed reading, ignoring condition words, and spending too long on one puzzle.',
                    'Build a simple rule: if progress is not visible quickly, mark and move. Return in the second pass with a fresh view.'
                ],
                'bullets': [
                    'Watch for words like only, except, least, and not',
                    'Set a time cap per question to prevent stalls',
                    'Use elimination aggressively when options are close',
                    'Maintain a weekly error log of recurring trap types'
                ]
            },
            {
                'heading': 'Exam-day MAT attempt strategy',
                'paragraphs': [
                    'Start with medium and direct items to build rhythm, then solve easier leftover questions, and finally attempt difficult puzzles if time remains.',
                    'A stable attempt plan protects accuracy and avoids panic guessing under time pressure.'
                ],
                'bullets': [
                    'Pass 1: solve confident medium questions quickly',
                    'Pass 2: clear easy direct items you skipped',
                    'Pass 3: attempt selected hard puzzles only',
                    'Final review: recheck marked items with elimination'
                ]
            },
            {
                'heading': 'MAT micro-FAQ for fast improvement',
                'paragraphs': [
                    'Q: Can MAT improve in one month? A: Yes, with daily timed practice and review.',
                    'Q: Should I memorize shortcuts only? A: No, combine shortcuts with logic accuracy.',
                    'Q: What is the best revision style? A: Re-attempt previous wrong sets every 2 to 3 days.'
                ],
                'bullets': [
                    'Consistency beats occasional long sessions',
                    'Accuracy first, then speed',
                    'Review mistakes immediately after each set'
                ]
            }
        ]
    },
    'cee-exam-day-strategy': {
        'title': "CEE Exam Day Strategy: Do's and Don'ts",
        'tag': 'Strategy',
        'accent': '#c04b62',
        'accent_soft': 'rgba(192, 75, 98, 0.08)',
        'accent_border': 'rgba(192, 75, 98, 0.22)',
        'description': 'CEE exam-day strategy covering pre-exam checklist, section pacing, negative-marking control, and high-pressure decision making.',
        'excerpt': 'A strong exam-day system can convert months of preparation into marks by protecting accuracy, pace, and confidence under pressure.',
        'sections': [
            {
                'heading': 'Pre-exam day plan: protect focus and energy',
                'paragraphs': [
                    'The biggest exam-day losses usually begin the previous night through panic revision and poor sleep. Your final evening should be calm, organized, and predictable.',
                    'Prepare all logistics early so exam morning remains stress-free. Cognitive clarity matters more than late-night extra reading.'
                ],
                'bullets': [
                    'Revise only quick notes and formula lists',
                    'Prepare all required documents in advance',
                    'Sleep on time and avoid late-night heavy study'
                ]
            },
            {
                'heading': 'Morning of exam: create a steady start',
                'paragraphs': [
                    'Avoid rushing and information overload on exam morning. Keep your routine simple: light revision, stable meals, and timely arrival.',
                    'When mind and body are stable, early questions feel easier and confidence builds naturally.'
                ],
                'bullets': [
                    'Arrive early to avoid last-minute stress',
                    'Avoid discussing difficult topics with other candidates',
                    'Use a short breathing reset before starting'
                ]
            },
            {
                'heading': 'Time management during the paper',
                'paragraphs': [
                    'Use a three-pass approach: confident questions first, moderate questions second, difficult questions last. This prevents early time drain and protects accuracy.',
                    'Watch section timing checkpoints so one subject does not consume the entire exam.'
                ],
                'bullets': [
                    'Pass 1: quick confident solves',
                    'Pass 2: moderate items with short calculation',
                    'Pass 3: only selected difficult items'
                ]
            },
            {
                'heading': 'Handling negative marking safely',
                'paragraphs': [
                    'Negative marking punishes random attempts. Guess only when you can eliminate at least two options with logic.',
                    'Protecting accuracy is often better than forcing maximum attempts.'
                ],
                'bullets': [
                    'Avoid blind guesses',
                    'Use elimination before marking uncertain answers',
                    'Keep 8 to 10 minutes for final review'
                ]
            },
            {
                'heading': 'Section balancing and recovery rules',
                'paragraphs': [
                    'If one section feels difficult, do not force completion immediately. Move to a stronger section to recover tempo and marks, then return later.',
                    'This strategy protects emotional stability and prevents one bad cluster from damaging total paper performance.'
                ],
                'bullets': [
                    'Set mini checkpoints for each section',
                    'If stalled, switch section and recover momentum',
                    'Return with a calmer second-pass mindset'
                ]
            },
            {
                'heading': 'Final 10-minute finish strategy',
                'paragraphs': [
                    'The last 10 minutes are score-protection time. Focus on marked questions, careless-check scan, and only high-confidence corrections.',
                    'Do not introduce chaotic last-minute guessing. Controlled finishing often adds reliable marks.'
                ],
                'bullets': [
                    'Recheck marked questions with elimination',
                    'Verify response bubbling/selection carefully',
                    'Avoid changing answers without clear reason'
                ]
            },
            {
                'heading': 'Exam-day FAQ for confidence control',
                'paragraphs': [
                    'Q: What if the first questions are difficult? A: Skip and build rhythm with solvable items first.',
                    'Q: Should I attempt every question? A: No. Accuracy with strategy beats random high attempts.',
                    'Q: How to stay calm if time feels short? A: Use pass-based solving and commit to your checkpoints.'
                ],
                'bullets': [
                    'Trust your preparation system',
                    'Protect accuracy under negative marking',
                    'Finish with structured review, not panic'
                ]
            }
        ]
    },
    'biology-diagram-revision-cee': {
        'title': 'Biology Diagram Revision That Actually Sticks',
        'tag': 'Biology',
        'accent': '#1f8a4c',
        'accent_soft': 'rgba(31, 138, 76, 0.08)',
        'accent_border': 'rgba(31, 138, 76, 0.22)',
        'description': 'A practical Biology revision note focused on diagrams, labels, and recall tricks for CEE students.',
        'excerpt': 'I stopped losing easy Biology marks when I began redrawing diagrams from memory and checking the labels against my own mistakes.',
        'sections': [
            {
                'heading': 'Why diagrams matter so much',
                'paragraphs': [
                    'Biology becomes easier when you stop treating diagrams as decoration. In CEE, a labelled heart, kidney, neuron, or plant cell can represent marks that are simple to secure if you revise them the right way.',
                    'I used to read diagrams passively and forget the labels after two days. What helped was drawing the same figure three times: once while studying, once from memory, and once in a quick revision notebook.'
                ],
                'bullets': [
                    'Draw the diagram before reading the label list',
                    'Use a blank sheet and check your own mistakes',
                    'Repeat the same diagram after 2 days and 7 days'
                ]
            },
            {
                'heading': 'My simple recall method',
                'paragraphs': [
                    'I keep one page for each system and write only the labels that I commonly forget. That page is not a full note. It is a mistake log for things I always mix up during revision.',
                    'Short recall practice works better than long reading sessions. Even ten minutes of active drawing can improve memory more than half an hour of scanning the textbook.'
                ],
                'bullets': [
                    'Keep one page per system or organ',
                    'Write the difficult labels in a different color',
                    'Test yourself without looking at the reference image'
                ]
            },
            {
                'heading': 'What I focus on first',
                'paragraphs': [
                    'For CEE, I would start with human physiology diagrams, then move to cell structure and plant anatomy. These topics appear often enough that repeated recall gives a real return.',
                    'The aim is not artistic perfection. The aim is accurate structure and the ability to remember the sequence of parts under exam pressure.'
                ],
                'bullets': [
                    'Heart and blood flow',
                    'Kidney and nephron',
                    'Neuron and reflex arc',
                    'Plant cell and tissue sections'
                ]
            }
        ]
    },
    'chemistry-reaction-map-cee': {
        'title': 'Chemistry Reaction Maps for Faster Recall',
        'tag': 'Chemistry',
        'accent': '#b36a00',
        'accent_soft': 'rgba(179, 106, 0, 0.08)',
        'accent_border': 'rgba(179, 106, 0, 0.24)',
        'description': 'A CEE Chemistry study note on reaction maps, conversion chains, and quick recall for organic and inorganic revision.',
        'excerpt': 'Instead of memorizing reactions in isolation, I built one map that linked every common conversion. That cut my confusion in half.',
        'sections': [
            {
                'heading': 'Why reaction maps help',
                'paragraphs': [
                    'Organic Chemistry looks huge until you connect the reactions. Once I started drawing conversion maps, I could see how one functional group led to another and why options in MCQs were either obviously correct or obviously wrong.',
                    'The map does not need to be pretty. It only needs to show the direction of change, reagent, and the kind of product you expect.'
                ],
                'bullets': [
                    'Draw the starting compound in the center',
                    'Use arrows for oxidation, reduction, addition, and substitution',
                    'Add reagents and conditions beside each arrow'
                ]
            },
            {
                'heading': 'How I keep it practical',
                'paragraphs': [
                    'I keep one page for the reaction map and another page for exceptions. The exception sheet is important because CEE often tests the same reaction with one small twist.',
                    'When I revise, I cover the product and try to recall the reagent, then I cover the reagent and try to recall the product. That double recall is what makes the map stick.'
                ],
                'bullets': [
                    'One page for conversions',
                    'One page for exceptions',
                    'Revise both pages in short loops'
                ]
            },
            {
                'heading': 'What to prioritize first',
                'paragraphs': [
                    'I would start with the reactions that repeat most often in entrance questions: alcohols, carbonyl compounds, acids, amines, and hydrocarbon conversions. Once those are clear, the rest becomes easier to remember.',
                    'This method is faster than trying to read the entire chapter again and again.'
                ],
                'bullets': [
                    'Functional-group conversions',
                    'Common tests and identification reactions',
                    'Named reactions and their conditions'
                ]
            }
        ]
    },
    'chapter-wise-marks-distribution': {
        'title': 'Chapter-wise Marks Distribution for CEE: What to Prioritise',
        'tag': 'Exam Strategy',
        'accent': '#1458a6',
        'accent_soft': 'rgba(20, 88, 166, 0.08)',
        'accent_border': 'rgba(20, 88, 166, 0.22)',
        'description': 'A practical chapter-wise marks distribution guide for CEE Nepal to prioritise study effort and improve score efficiently.',
        'excerpt': 'Understand which chapters carry the most marks in CEE and how to allocate your study time for maximum impact.',
        'sections': [
            {
                'heading': 'Why chapter-wise weightage matters',
                'paragraphs': [
                    'Not all chapters are equally important in the CEE pattern. Knowing which chapters routinely contribute more MCQs helps you prioritise revision and MCQ practice so that your study time converts to the largest possible score gains.',
                    'This guide summarises typical chapter weightage across Biology, Chemistry, Physics and MAT and gives actionable advice on how to split revision hours for the maximum return.'
                ],
                'bullets': []
            },
            {
                'heading': 'Biology (Botany + Zoology) — high yield chapters',
                'paragraphs': [
                    'Biology traditionally contributes the largest block of questions in CEE. Within Biology, Human Physiology, Genetics, Cell Biology and Biodiversity are frequent sources of straightforward MCQs. If you focus first on human physiology and genetics, you can secure many marks with relatively high accuracy.',
                    'For practical study planning, aim to spend 35–40% of your Biology study time on these high-yield chapters during early revision phases.'
                ],
                'bullets': [
                    'Human Physiology: diagrams and functional questions',
                    'Genetics: inheritance patterns and simple calculations',
                    'Cell Biology: organelles, structure and processes'
                ]
            },
            {
                'heading': 'Chemistry — divide by topic type',
                'paragraphs': [
                    'Chemistry weight often splits between Physical, Organic and Inorganic sub-sections. Physical and Organic together commonly carry the majority of Chemistry marks. Prioritise reaction mapping, stoichiometry, and core physical chemistry concepts first.',
                    'Allocate roughly 40% of Chemistry revision time to Physical and Organic combined, and the rest to Inorganic and application questions.'
                ],
                'bullets': [
                    'Physical Chemistry: equations and numericals',
                    'Organic Chemistry: reaction types and mechanisms',
                    'Inorganic Chemistry: important facts and periodic trends'
                ]
            },
            {
                'heading': 'Physics — target numericals and modern physics',
                'paragraphs': [
                    'Mechanics and Modern Physics often appear with numerical problems that favour structured problem solving. Current Electricity and Magnetism also carry consistent weight. Strengthen formula recall and common numerical strategies to convert practice into points.',
                    'Dedicate timed problem sets to mechanics and electricity early in your plan; these are high-return chapters.'
                ],
                'bullets': [
                    'Mechanics: vectors, motion, energy problems',
                    'Modern Physics: direct concept application',
                    'Electricity & Magnetism: circuits and field concepts'
                ]
            },
            {
                'heading': 'MAT — speed and pattern recognition',
                'paragraphs': [
                    'MAT is short but high impact: consistent daily practice yields fast gains. Treat MAT as a speed-building exercise, not a deep-concept subject. Use short timed drills and focus on accuracy under time pressure.',
                    'Because MAT is quicker to improve, keep a small but regular allocation to MAT throughout your preparation cycle.'
                ],
                'bullets': []
            },
            {
                'heading': 'Practical study allocation example',
                'paragraphs': [
                    'If you have 10 hours a week, a practical split might be: Biology 4 hours (focused on high-yield chapters), Chemistry 3 hours (physical + organic focus), Physics 2 hours (mechanics and electricity), MAT 1 hour (daily short drills). Adjust based on your personal strengths and weaknesses.',
                    'Use chapter-wise MCQ trackers to validate whether more time on a subject yields better accuracy; move hours between subjects based on that feedback.'
                ],
                'bullets': [
                    'Track accuracy per chapter and reassign study hours weekly',
                    'Run weekly full-length mocks to test allocation efficiency'
                ]
            }
        ]
    },
    'last-30-days-cee-prep-plan': {
        'title': 'Last 30 Days CEE Preparation Plan: Time-sensitive, High-Impact',
        'tag': 'Plan',
        'accent': '#c04b62',
        'accent_soft': 'rgba(192, 75, 98, 0.08)',
        'accent_border': 'rgba(192, 75, 98, 0.22)',
        'description': 'A focused 30-day plan to maximise CEE score before exam day with a mix of revision, MCQ practice and full mocks.',
        'excerpt': 'Use this high-impact, 30-day checklist to polish topics, fix weak areas, and simulate exam conditions before your CEE.',
        'sections': [
            {
                'heading': 'Overview and mindset for the last 30 days',
                'paragraphs': [
                    'The final 30 days before CEE are about consolidation, not new learning. Prioritise high-yield chapters, error correction, and realistic mock tests. Keep your routine steady and focus on exam temperament and pacing.',
                    'This plan breaks the 30 days into three 10-day cycles: quick review, intensive MCQ practice, and mock-test simulation.'
                ],
                'bullets': []
            },
            {
                'heading': 'Days 1–10: quick review and patching',
                'paragraphs': [
                    'Use the first 10 days to patch conceptual gaps and compile a short error-sheet of topics you repeatedly miss. Revisit formulas, reaction maps, and key diagrams. Avoid major new chapters at this stage.',
                    'Schedule short daily timed quizzes (30–45 minutes) to stabilise recall under pressure.'
                ],
                'bullets': [
                    'Daily checklist: 45 minutes revision + 30 minutes MCQs',
                    'Maintain an error-tracking sheet for repeated mistakes'
                ]
            },
            {
                'heading': 'Days 11–20: intensive MCQ practice',
                'paragraphs': [
                    'Increase MCQ volume and mix chapters to simulate real exam unpredictability. Do targeted chapter sessions in the morning and mixed timed sets in the evening. Focus corrections on the error-sheet and re-test those questions.',
                    'Gradually reduce reliance on notes and force retrieval from memory during these drills.'
                ],
                'bullets': [
                    'Two daily MCQ sessions: focused chapter set + mixed timed set',
                    'Correct and re-attempt error-sheet questions after 48 hours'
                ]
            },
            {
                'heading': 'Days 21–30: mock tests and exam simulation',
                'paragraphs': [
                    'Switch to full-length mock tests under exam-like conditions. Time yourself strictly and practice the three-pass strategy: easy first, moderate second, hard last. Use the final 48 hours for light revision and rest—avoid cramming.',
                    'Simulate exam timing, breaks, and environment to build endurance and pacing.'
                ],
                'bullets': [
                    'At least 3 full mocks in the final 10 days',
                    'Review mocks thoroughly: identify why errors occurred and update the error-sheet'
                ]
            },
            {
                'heading': 'Final pre-exam checklist',
                'paragraphs': [
                    'In the last 48 hours confirm logistics, necessary documents, and a calm routine. Keep final revision selective—formula lists, reaction maps and quick fact checks only. Prioritise sleep and a consistent routine.',
                    'Plan exam-day pacing: secure easy marks early, manage time per section, and reserve the final 10–12 minutes for review.'
                ],
                'bullets': [
                    'Pack documents and test kit a day before',
                    'Avoid new topics in the final 48 hours',
                    'Get regular sleep and small, steady meals'
                ]
            }
        ]
    },
    'how-to-remember-organic-reactions': {
        'title': 'How to Remember Organic Chemistry Reactions: Practical Techniques',
        'tag': 'Chemistry',
        'accent': '#b36a00',
        'accent_soft': 'rgba(179, 106, 0, 0.08)',
        'accent_border': 'rgba(179, 106, 0, 0.24)',
        'description': 'Memory techniques and practical strategies to retain organic chemistry reactions for exams like CEE.',
        'excerpt': 'Use maps, categorization, reaction families and active recall to remember organic chemistry reactions more reliably and efficiently.',
        'sections': [
            {
                'heading': 'Why reactions are hard to remember',
                'paragraphs': [
                    'Organic reactions can feel like an endless list of reagents and conditions. The trick is not rote memorisation but pattern recognition—grouping reactions by functional-group transformations and mechanistic similarity.',
                    'This article provides practical memory strategies, example reaction clusters, and study routines that convert into better recall under test conditions.'
                ],
                'bullets': []
            },
            {
                'heading': 'Build reaction maps and family trees',
                'paragraphs': [
                    'Instead of isolated notes, create reaction maps that connect starting materials to products through common transformations. For example, track conversions from alkanes → haloalkanes → alcohols → carbonyl compounds. This reduces memory load and creates logical hooks.',
                    'Use a single-page reaction map for each functional group family and review it frequently.'
                ],
                'bullets': [
                    'Create one-page maps for hydrocarbons, alcohols, carbonyls, and amines',
                    'Highlight common reagents and typical outcomes'
                ]
            },
            {
                'heading': 'Use mechanistic logic as a mnemonic',
                'paragraphs': [
                    'Understanding the mechanism (even at a high level) helps you predict reaction outcomes and remember reagent behavior. When you know whether a reaction proceeds by nucleophilic substitution, electrophilic addition, or radical initiation, the products become more predictable and memorable.',
                    'Convert mechanism steps into short phrases you can rehearse quickly.'
                ],
                'bullets': [
                    'Label reactions as SN1/SN2, E1/E2, electrophilic addition, etc.',
                    'Use brief mechanism notes to predict exceptions'
                ]
            },
            {
                'heading': 'Active recall and spaced repetition',
                'paragraphs': [
                    'Practice recall by writing reaction outcomes from memory and testing yourself after increasing intervals. Spaced repetition ensures longer retention than cramming. Convert your reaction maps into flashcards and review them daily for short intervals.',
                    'Prioritise reactions that appear most frequently in previous CEE patterns.'
                ],
                'bullets': [
                    'Use short daily flashcard sessions (10–15 minutes)',
                    'Re-attempt incorrectly recalled reactions after 2, 5 and 10 days'
                ]
            },
            {
                'heading': 'Practical drilling and problem sets',
                'paragraphs': [
                    'Apply reactions in small timed problem sets rather than passive review. Doing product-prediction questions and mechanism-based MCQs helps cement reactions by use, not just recall. Over time, this practice builds recognition speed crucial for MCQ exams.',
                    'Mix reaction recall with small applied problems and re-check using your reaction map to close knowledge gaps.'
                ],
                'bullets': []
            }
        ]
    },
    'past-papers-smart-practice-cee': {
        'title': 'How I Use Past Papers to Study Smarter',
        'tag': 'Study Tips',
        'accent': '#7a4dc7',
        'accent_soft': 'rgba(122, 77, 199, 0.08)',
        'accent_border': 'rgba(122, 77, 199, 0.22)',
        'description': 'A practical note on using CEE past papers to find patterns, build timing, and improve revision quality.',
        'excerpt': 'Past papers are not just for checking yourself at the end. I use them as a map for what deserves more time now.',
        'sections': [
            {
                'heading': 'What past papers tell you',
                'paragraphs': [
                    'Past papers show you what repeats, how questions are phrased, and where the easy marks usually hide. They also tell you which topics deserve serious time and which ones can be revised more lightly.',
                    'The real value is pattern recognition. Once you solve enough papers, you begin to notice the same style of question returning with small changes.'
                ],
                'bullets': [
                    'Repeated concepts become obvious quickly',
                    'Question wording becomes less intimidating',
                    'Timing improves because patterns feel familiar'
                ]
            },
            {
                'heading': 'How I actually review a paper',
                'paragraphs': [
                    'I solve the paper once under time pressure, then I review every wrong and skipped item. I do not stop at the answer. I write why I missed it and whether the issue was concept, speed, or carelessness.',
                    'That second step is where the score improvement happens. Without review, a past paper is just another test.'
                ],
                'bullets': [
                    'Solve once under exam timing',
                    'Mark wrong answers in a separate notebook',
                    'Re-attempt the same paper after a few days'
                ]
            },
            {
                'heading': 'The part I would never skip',
                'paragraphs': [
                    'I always keep a list of topics that keep returning across papers. That list is better than a huge stack of notes because it tells me exactly where to revise next.',
                    'If you are short on time, use the papers to guide your next study session instead of reading chapters in order.'
                ],
                'bullets': [
                    'Build a topic frequency list',
                    'Focus revision on repeated themes first',
                    'Use papers to plan the next week, not just the final week'
                ]
            }
        ]
    },
}

BLOG_POST_ORDER = [
    'chapter-wise-marks-distribution',
    'last-30-days-cee-prep-plan',
    'how-to-remember-organic-reactions',
    'how-to-prepare-for-cee',
    'human-biology-cee-questions',
    'organic-chemistry-cee-tips',
    'physics-high-weightage-topics',
    'mat-section-tips',
    'cee-exam-day-strategy',
    'biology-diagram-revision-cee',
    'chemistry-reaction-map-cee',
    'past-papers-smart-practice-cee',
]

BLOG_THEMES = {
    slug: {
        'accent': post['accent'],
        'accent_soft': post['accent_soft'],
        'accent_border': post['accent_border'],
    }
    for slug, post in BLOG_POSTS.items()
}

BLOG_INTERNAL_LINKS = {
    'how-to-prepare-for-cee': [
        {'label': 'Chapter-wise Practice', 'url': '/'},
        {'label': 'Full Test', 'url': '/full-test/'},
        {'label': 'Privacy / Terms', 'url': '/privacy/'},
    ],
    'physics-high-weightage-topics': [
        {'label': 'Physics Chapter Practice', 'url': '/subject/2/'},
        {'label': 'Full Test', 'url': '/full-test/'},
        {'label': 'All Subjects', 'url': '/'},
    ],
    'human-biology-cee-questions': [
        {'label': 'Biology Chapter Practice', 'url': '/subject/1/'},
        {'label': 'Full Test', 'url': '/full-test/'},
        {'label': 'All Subjects', 'url': '/'},
    ],
    'organic-chemistry-cee-tips': [
        {'label': 'Chemistry Chapter Practice', 'url': '/subject/3/'},
        {'label': 'Full Test', 'url': '/full-test/'},
        {'label': 'All Subjects', 'url': '/'},
    ],
    'mat-section-tips': [
        {'label': 'MAT Practice', 'url': '/subject/1/'},
        {'label': 'Full Test', 'url': '/full-test/'},
        {'label': 'All Subjects', 'url': '/'},
    ],
    'cee-exam-day-strategy': [
        {'label': 'Full Test Simulation', 'url': '/full-test/'},
        {'label': 'Chapter-wise Practice', 'url': '/'},
        {'label': 'Privacy / Terms', 'url': '/privacy/'},
    ],
}

BLOG_CUSTOM_TEMPLATES = {
    'physics-high-weightage-topics': 'blog_physics_high_weightage.html',
    'mat-section-tips': 'blog_mat_section_tips.html',
    'cee-exam-day-strategy': 'blog_exam_day_strategy.html',
}


def _pick_random_questions(base_queryset, limit=50):
    """Sample random questions efficiently by sampling IDs first."""
    question_ids = list(base_queryset.values_list('id', flat=True))
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
            'sub_chapter__name',
        )
    )
    id_to_question = {q.id: q for q in selected_qs}
    return [id_to_question[qid] for qid in selected_ids if qid in id_to_question]


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
}


def _build_full_test_question_ids():
    selected_ids = []

    for subject_name, chapters_config in FULL_TEST_BLUEPRINT.items():
        for chapter_name, question_count in chapters_config.items():
            chapter_questions = Question.objects.filter(
                chapter__subject__name=subject_name,
                chapter__name=chapter_name,
            )
            selected_ids.extend(_sample_question_ids(chapter_questions, question_count))

    random.shuffle(selected_ids)
    return selected_ids


def _sample_question_ids(base_queryset, limit):
    """Return a random sample of question IDs without loading full model rows."""
    question_ids = list(base_queryset.values_list('id', flat=True))
    if not question_ids or limit <= 0:
        return []
    return random.sample(question_ids, min(limit, len(question_ids)))


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
        return _build_test_history_entries(history_qs)
    except DatabaseError:
        # Handle environments where migration state and runtime schema are temporarily out of sync.
        _refresh_testresult_columns_cache()
        fallback_qs = TestResult.objects.filter(name__iexact=exact_name).values(
            'topic',
            'score',
            'total_attempted',
            'created_at',
        ).order_by('-created_at', '-id')[:limit]
        return _build_test_history_entries(fallback_qs)


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

        return TestResult.objects.create(**payload)
    except DatabaseError:
        _refresh_testresult_columns_cache()
        safe_payload = {
            'name': user_name,
            'topic': topic,
            'score': score,
            'total_attempted': total_attempted,
        }
        return TestResult.objects.create(**safe_payload)


def keepalive(request):
    """Keep database connection alive - for Uptime Robot and client pings"""
    try:
        # Ensure database connection is active
        connection.ensure_connection()
        # Use a minimal probe query to keep connection warm.
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        return HttpResponse("OK", status=200)
    except Exception as e:
        return HttpResponse(f"Error: {str(e)}", status=500)
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

    except requests.RequestException as exc:
        return JsonResponse({'ok': False, 'message': f'Email API error: {exc}'}, status=500)

    except Exception as exc:
        return JsonResponse({'ok': False, 'message': f'Unexpected error: {exc}'}, status=500)
@cache_page(0)  # Disable caching for development
def home(request):
    subject_list = _ordered_subjects()
    total_questions = Question.objects.count()
    page_default_title = 'CEE MCQ – Free Practice Questions | CEE MCQ'
    page_default_description = "Free CEE MCQ practice. Chapter-wise MCQ questions in Biology, Chemistry, Physics and MAT for Nepal's Common Entrance Examination."
    page_default_keywords = 'CEE MCQ, CEE Nepal, Chapter-wise MCQ Questions, Biology, Chemistry, Physics, MAT'
    request.page_slug = 'home'
    return render(request, 'home.html', {
        'subjects': subject_list,
        'total_questions': total_questions,
        'crawl_hubs': _crawl_hubs(),
        'page_slug': 'home',
        'page_default_title': page_default_title,
        'page_default_description': page_default_description,
        'page_default_keywords': page_default_keywords,
        'page_default_og_title': 'CEE MCQ – Free CEE MCQ Questions',
        'page_default_og_description': "Free CEE entrance MCQ practice. Chapter-wise MCQ questions in Biology, Chemistry, Physics and MAT for Nepal's Common Entrance Examination.",
    })


def all_subjects(request):
    subjects = _ordered_subjects()
    hub_items = []
    for subject in subjects:
        chapter_total = Chapter.objects.filter(subject=subject).count()
        hub_items.append({
        'name': f'{subject.name} MCQ',
        'url': _subject_alias_url(subject.slug),
        'description': (
            f"Practice {subject.name} MCQs with structured chapter-wise questions. "
            f"Includes {chapter_total} chapters for focused revision and exam preparation."
        ),
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
    "This page provides quick access to all major CEE subjects, "
    "including Biology, Chemistry, Physics, and MAT, "
    "making navigation simple and structured."
),
        hub_items=hub_items,
    )
    return render(request, 'seo_hub.html', context)


def all_mcq(request):
    # Route disabled: redirect to home to avoid exposing a separate "All MCQ" hub.
    return redirect('home')


def chapters(request, slug):
    """Subject page looked up by slug."""
    subject = get_object_or_404(Subject, slug=slug)
    chapters_list = Chapter.objects.filter(subject=subject).order_by('id')
    page_default_title = f'CEE {subject.name} MCQ Questions – Chapter Wise | CEE MCQ'
    page_default_description = f"Explore all {subject.name} chapters and practice chapter-wise MCQ questions to prepare for Nepal's Common Entrance Examination."
    page_default_keywords = f'CEE MCQ, {subject.name}, CEE Nepal, Chapters, Practice Questions'
    request.page_slug = slug
    return render(request, 'chapter.html', {
        'subject': subject,
        'chapters': chapters_list,
        **_crawl_navigation_links(subject.slug),
        'page_slug': slug,
        'page_default_title': page_default_title,
        'page_default_description': page_default_description,
        'page_default_keywords': page_default_keywords,
        'page_default_og_title': f'{subject.name} Chapters | CEE MCQ',
        'page_default_og_description': f"Practice chapter-wise MCQ questions for {subject.name}. Prepare for Nepal's Common Entrance Examination.",
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
    """Resolve SEO slugs such as /physics-mcq/ without defining separate URL patterns."""
    request.page_slug = page_slug
    slug_options = _slug_aliases(page_slug)

    for candidate in slug_options:
        subject = Subject.objects.filter(slug=candidate).first()
        if subject:
            chapters_list = Chapter.objects.filter(subject=subject).order_by('id')
            page_default_title = f'CEE {subject.name} MCQ Questions – Chapter Wise | CEE MCQ'
            page_default_description = f"Explore all {subject.name} chapters and practice chapter-wise MCQ questions to prepare for Nepal's Common Entrance Examination."
            page_default_keywords = f'CEE MCQ, {subject.name}, CEE Nepal, Chapters, Practice Questions'
            return render(request, 'chapter.html', {
                'subject': subject,
                'chapters': chapters_list,
                **_crawl_navigation_links(subject.slug),
                'page_slug': page_slug,
                'page_default_title': page_default_title,
                'page_default_description': page_default_description,
                'page_default_keywords': page_default_keywords,
                'page_default_og_title': f'{subject.name} Chapters | CEE MCQ',
                'page_default_og_description': f"Practice chapter-wise MCQ questions for {subject.name}. Prepare for Nepal's Common Entrance Examination.",
            })

        chapter = Chapter.objects.filter(slug=candidate).first()
        if chapter:
            if chapter.has_subchapters:
                return redirect('subchapters', slug=chapter.slug)
            return redirect('quiz', slug=chapter.slug)

        subchapter = SubChapter.objects.filter(slug=candidate).first()
        if subchapter:
            return redirect('subchapter_quiz', slug=subchapter.slug)

    # If SEO exists but content route is not mapped yet, show a soft landing page.
    seo_entry = PageSEO.objects.filter(page_slug=page_slug).first()
    supabase_entry = get_supabase_page_seo(page_slug)
    if seo_entry or supabase_entry:
        return render(request, 'dynamic_page.html', {'page_slug': page_slug})

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
    chapter = get_object_or_404(Chapter, slug=slug)
    subchapter_list = SubChapter.objects.filter(chapter=chapter).order_by('order')
    return render(request, 'subchapter.html', {
        'chapter': chapter,
        'subchapters': subchapter_list,
        **_crawl_navigation_links(chapter.subject.slug),
    })


def subchapters_redirect(request, chapter_id):
    chapter = get_object_or_404(Chapter, id=chapter_id)
    return redirect('subchapters', slug=chapter.slug, permanent=True)


def quiz(request, slug):
    chapter = get_object_or_404(Chapter, slug=slug)
    chapter_id = chapter.id
    user_name = _normalize_exact_name(request.GET.get('name') or request.POST.get('name'))
    quiz_started = (request.GET.get('start') == '1' and user_name)
    attempt_key_prefix = f'quiz_{chapter_id}'
    attempt_reference = _attempt_reference(request.session, attempt_key_prefix)
    request.page_slug = slug
    page_default_title = f'{chapter.name} MCQ – {chapter.subject.name} | CEE MCQ'
    page_default_description = f'Practice the {chapter.name} MCQ for the Common Entrance Examination. Track your performance with detailed results.'
    page_default_keywords = f'CEE MCQ, {chapter.name} MCQ, {chapter.subject.name}, Chapter-wise Questions, Online Practice'

    if request.method == 'POST':
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

            questions_qs = Question.objects.filter(id__in=questions_ids).select_related('chapter', 'sub_chapter')
            id_to_question = {q.id: q for q in questions_qs}
            questions = [id_to_question[qid] for qid in questions_ids if qid in id_to_question]

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
                messages.warning(request, 'Result calculated but may not be saved. Please contact admin.')
                print(f"DB Error: {db_error}")

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
            messages.error(request, f'Error processing submission: {str(e)}. Please try again.')
            return redirect('quiz', slug=chapter.slug)

    else:
        user_name = _normalize_exact_name(request.GET.get('name', ''))
        quiz_started = request.GET.get('start') == '1' and bool(user_name)
        questions = []

        if quiz_started:
            attempt_reference = _attempt_reference(request.session, attempt_key_prefix, force_new=True)
            questions_qs = Question.objects.filter(chapter=chapter)
            questions = _pick_random_questions(questions_qs, limit=50)
            request.session[f'quiz_questions_{chapter_id}'] = [q.id for q in questions]
        else:
            request.session.pop(f'quiz_questions_{chapter_id}', None)
        
        return render(request, 'quiz.html', {
            'chapter': chapter,
            'questions': questions,
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
    attempt_reference = _attempt_reference(request.session, attempt_key_prefix)
    request.page_slug = slug
    page_default_title = f'{sub_chapter.name} MCQ – {chapter.name} | CEE MCQ'
    page_default_description = f'Practice the {sub_chapter.name} MCQ from {chapter.name} for the Common Entrance Examination. Track your performance with detailed results.'
    page_default_keywords = f'CEE MCQ, {sub_chapter.name} MCQ, {chapter.name} MCQ, Chapter-wise Questions, Online Practice'

    if request.method == 'POST':
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

            questions_qs = Question.objects.filter(id__in=questions_ids).select_related('chapter', 'sub_chapter')
            id_to_question = {q.id: q for q in questions_qs}
            questions = [id_to_question[qid] for qid in questions_ids if qid in id_to_question]

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
                messages.warning(request, 'Result calculated but may not be saved. Please contact admin.')
                print(f"DB Error: {db_error}")

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
            messages.error(request, f'Error processing submission: {str(e)}. Please try again.')
            return redirect('subchapter_quiz', slug=sub_chapter.slug)

    else:
        user_name = _normalize_exact_name(request.GET.get('name', ''))
        quiz_started = request.GET.get('start') == '1' and bool(user_name)
        questions = []

        if quiz_started:
            attempt_reference = _attempt_reference(request.session, attempt_key_prefix, force_new=True)
            questions_qs = Question.objects.filter(sub_chapter=sub_chapter)
            questions = _pick_random_questions(questions_qs, limit=50)
            request.session[session_key] = [q.id for q in questions]
        else:
            request.session.pop(session_key, None)

        return render(request, 'quiz.html', {
            'chapter': chapter,
            'sub_chapter': sub_chapter,
            'subchapter': sub_chapter,
            'questions': questions,
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
        })


def full_test(request):
    result_session_key = 'full_test_result_data'
    attempt_key_prefix = 'full_test'
    attempt_reference = _attempt_reference(request.session, attempt_key_prefix)
    request.page_slug = 'full-test'
    page_default_title = 'CEE Full Mock Test – 180 Questions Online | CEE MCQ'
    page_default_description = 'Take a full CEE mock test online with 180 questions, negative marking, and a 2.5-hour timer. Simulate the real MEC entrance exam experience.'
    page_default_keywords = 'CEE full test, CEE mock test Nepal, CEE online test, MEC full mock test, CEE 180 questions, CEE practice exam'
    if request.method == "POST":
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

            questions_qs = Question.objects.filter(id__in=questions_ids).select_related('chapter', 'sub_chapter')
            questions = list(questions_qs)
            id_to_question = {q.id: q for q in questions}
            questions = [id_to_question[qid] for qid in questions_ids if qid in id_to_question]

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
                messages.warning(request, 'Result calculated but may not be saved. Please contact admin.')
                print(f"DB Error: {db_error}")

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
            messages.error(request, f'Error processing submission: {str(e)}. Please try again.')
            return redirect('full_test')

    else:
        user_name = _normalize_exact_name(request.GET.get('name', ''))
        quiz_started = request.GET.get('start') == '1' and bool(user_name)

        if not quiz_started:
            request.session.pop('full_test_questions', None)
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

        attempt_reference = _attempt_reference(request.session, attempt_key_prefix, force_new=True)
        selected_ids = _build_full_test_question_ids()

        questions_qs = Question.objects.filter(id__in=selected_ids).select_related('chapter', 'sub_chapter')
        id_to_question = {q.id: q for q in questions_qs}
        questions = [id_to_question[qid] for qid in selected_ids if qid in id_to_question]

        request.session['full_test_questions'] = [q.id for q in questions]
        request.session.pop(result_session_key, None)

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


def full_test_results(request):
    request.page_slug = 'full-test'
    # Default page metadata for full test results
    page_default_title = 'CEE Full Mock Test – 180 Questions Online | CEE MCQ'
    page_default_description = 'Take a full CEE mock test online with 180 questions, negative marking, and a 2.5-hour timer. Simulate the real MEC entrance exam experience.'
    page_default_keywords = 'CEE full test, CEE mock test Nepal, CEE online test, MEC full mock test, CEE 180 questions, CEE practice exam'
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
        questions_qs = Question.objects.filter(id__in=question_ids).select_related('chapter', 'sub_chapter')
        id_to_question = {q.id: q for q in questions_qs}
        questions = [id_to_question[qid] for qid in question_ids if qid in id_to_question]
    except Exception as error:
        messages.error(request, f'Unable to load test results: {error}')
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
        **_crawl_navigation_links(),
        **result_metrics,
    })


def privacy_policy(request):
    return render(request, 'privacy.html')


def privacy_policy_redirect(request):
    return redirect('privacy_policy', permanent=True)


def privacy_policy_page(request):
    return render(request, 'privacy_policy.html')


def about(request):
    return render(request, 'about.html')


def disclaimer(request):
    return render(request, 'disclaimer.html')


def contact(request):
    if request.method == 'POST':
        name = (request.POST.get('name') or '').strip()
        email = (request.POST.get('email') or '').strip()
        message = (request.POST.get('message') or '').strip()

        if not name or not email or not message:
            messages.error(request, 'Please fill in all contact fields.')
        else:
            messages.success(request, 'Thanks for reaching out. Please email us if you need a faster reply.')

    return render(request, 'contact.html')


def ads_txt(request):
    try:
        with open(settings.BASE_DIR / 'static' / 'ads.txt', 'r', encoding='utf-8') as ads_file:
            content = ads_file.read()
    except FileNotFoundError:
        content = 'google.com, pub-3880021540956659, DIRECT, f08c47fec0942fa0'
    return HttpResponse(content, content_type='text/plain')


def sitemap_xml(request):
    req_site = RequestSite(request)
    req_protocol = request.scheme
    urls = []

    for sitemap in sitemaps.values():
        if callable(sitemap):
            sitemap = sitemap()
        for page_number in range(1, sitemap.paginator.num_pages + 1):
            urls.extend(sitemap.get_urls(page=page_number, site=req_site, protocol=req_protocol))

    return render(request, 'sitemap.xml', {'urls': urls}, content_type='application/xml')


def blog_index(request):
    posts = []
    for slug in BLOG_POST_ORDER:
        post = BLOG_POSTS[slug]
        posts.append({
            'slug': slug,
            'title': post['title'],
            'tag': post['tag'],
            'excerpt': post['excerpt'],
            'accent': post['accent'],
            'accent_soft': post['accent_soft'],
            'accent_border': post['accent_border'],
        })
    return render(request, 'blog.html', {'posts': posts})


def blog_post(request, slug):
    post = BLOG_POSTS.get(slug)
    if not post:
        raise Http404('Blog post not found')

    custom_template = BLOG_CUSTOM_TEMPLATES.get(slug)
    if custom_template:
        return render(request, custom_template, {'theme': BLOG_THEMES.get(slug, BLOG_THEMES['how-to-prepare-for-cee'])})

    expanded_sections = list(post['sections'])
    expanded_sections.append({
        'heading': '90-day preparation framework for consistent score growth',
        'paragraphs': [
            f'To get stable results in {post["title"]}, focus on consistency instead of intensity spikes. Use a rolling 90-day cycle with weekly checkpoints. Your objective each week should be measurable: chapter completion, accuracy target, and timed-practice target. This prevents random study and gives you clear signals about whether your plan is working.',
            'A practical method is to combine concept revision, active recall, and timed MCQ solving in every week. For example, use two days for concept reinforcement, three days for question practice, and one day for review and retest. The final day can be used for mixed-set simulation under real exam timing. Repeat weak topics in the next cycle rather than postponing them for the final month.',
            'Keep one progress sheet where you record attempts, accuracy, and average solving time. Over a few weeks, this data shows exactly where marks are leaking. Many students think they need more study hours, but often they only need better sequencing and better revision timing.'
        ],
        'bullets': [
            'Set weekly targets for completion, accuracy, and speed',
            'Review mistakes within 24 hours for stronger retention',
            'Revisit weak topics every 5 to 7 days until accuracy stabilizes',
            'Use one full-length simulation each week in the final phase'
        ]
    })
    expanded_sections.append({
        'heading': 'Mistakes that lower rank and how to avoid them',
        'paragraphs': [
            'A common error is over-investing time in favorite subjects while avoiding weak areas. In a competitive exam, rank depends on total score, so weak-section recovery is essential. Another frequent issue is passive reading without retrieval practice. If you cannot recall concepts under time pressure, reading alone will not convert into marks.',
            'Students also lose marks due to poor test behavior: rushing early questions, ignoring negative marking impact, and failing to reserve review time. A controlled attempt strategy is more powerful than trying to attempt everything. Accuracy-first planning usually outperforms high-attempt guessing in scored competitive tests.',
            'Finally, avoid last-week content panic. In the final stretch, prioritize revision quality and test rhythm. The goal is calm execution, strong recall, and disciplined decision-making under time constraints.'
        ],
        'bullets': [
            'Do not skip weak chapters for more than one week',
            'Use active recall and short self-tests, not passive rereading',
            'Plan attempt order before each test to reduce panic',
            'Keep final revision compact: formulas, reactions, and high-yield notes'
        ]
    })

    post_with_depth = {
        'title': post['title'],
        'tag': post['tag'],
        'description': post['description'],
        'excerpt': post['excerpt'],
        'sections': expanded_sections,
    }

    # Calculate reading time (approx. 200 wpm)
    text_parts = [post_with_depth['title'], post_with_depth.get('excerpt', ''), post_with_depth.get('description', '')]
    for sec in post_with_depth['sections']:
        text_parts.append(sec.get('heading', ''))
        for p in sec.get('paragraphs', []):
            text_parts.append(p)
        for b in sec.get('bullets', []):
            text_parts.append(b)
    all_text = ' '.join(text_parts)
    words = len(re.findall(r"\w+", all_text))
    reading_time = max(1, round(words / 200))

    # Use a stable published date for these static posts
    date_published = '2026-05-23'

    return render(request, 'blog_post.html', {
        'slug': slug,
        'post': post_with_depth,
        'theme': BLOG_THEMES.get(slug, BLOG_THEMES['how-to-prepare-for-cee']),
        'related_links': BLOG_INTERNAL_LINKS.get(slug, []),
        'reading_time': reading_time,
        'date_published': date_published,
    })