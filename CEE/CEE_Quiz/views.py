import random
import re
import uuid
import json
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.http import Http404, HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.cache import cache_page
from django.db import connection
from django.core.mail import send_mail
from django.conf import settings
from .models import Subject, Chapter, SubChapter, Question, TestResult


BLOG_POSTS = {
    'how-to-prepare-for-cee': {
        'title': 'How to Prepare for CEE Effectively',
        'tag': 'Study Tips',
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
    }
}

BLOG_POST_ORDER = [
    'how-to-prepare-for-cee',
    'human-biology-cee-questions',
    'organic-chemistry-cee-tips',
    'physics-high-weightage-topics',
    'mat-section-tips',
    'cee-exam-day-strategy',
]

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


def _sample_question_ids(base_queryset, limit):
    """Return a random sample of question IDs without loading full model rows."""
    question_ids = list(base_queryset.values_list('id', flat=True))
    if not question_ids or limit <= 0:
        return []
    return random.sample(question_ids, min(limit, len(question_ids)))


def _attempt_reference(session, key_prefix):
    """Return a short stable attempt reference for the current quiz session."""
    session_key = f"{key_prefix}_attempt_reference"
    attempt_reference = session.get(session_key)
    if not attempt_reference:
        attempt_reference = uuid.uuid4().hex[:8].upper()
        session[session_key] = attempt_reference
        session.modified = True
    return attempt_reference


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


@csrf_exempt
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
    if request.method != 'POST':
        return JsonResponse({'ok': False, 'message': 'POST required.'}, status=405)

    try:
        payload = json.loads(request.body.decode('utf-8'))
    except (json.JSONDecodeError, UnicodeDecodeError):
        return JsonResponse({'ok': False, 'message': 'Invalid JSON payload.'}, status=400)

    user_name = (payload.get('name') or '').strip()
    attempt_reference = (payload.get('attempt_reference') or '').strip()
    topic = (payload.get('topic') or '').strip()
    reason = (payload.get('reason') or '').strip()
    question_id = _parse_non_negative_int(payload.get('question_id'), default=-1)
    question_text = (payload.get('question_text') or '').strip()

    if question_id <= 0 or not question_text or not reason:
        return JsonResponse({'ok': False, 'message': 'Missing question details.'}, status=400)

    if not settings.EMAIL_HOST_USER or not settings.EMAIL_HOST_PASSWORD:
        return JsonResponse({'ok': False, 'message': 'Email is not configured on the server.'}, status=500)

    subject = f"CEE Quiz Review Report | QID {question_id}"
    message = (
        f"User: {user_name or 'Unknown'}\n"
        f"Attempt: {attempt_reference or 'N/A'}\n"
        f"Topic: {topic or 'N/A'}\n"
        f"Reason: {reason}\n"
        f"Question ID: {question_id}\n\n"
        f"Question Text:\n{question_text}\n"
    )

    try:
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=['ceequiz9830@gmail.com'],
            fail_silently=False,
        )
    except Exception as exc:
        return JsonResponse({'ok': False, 'message': f'Failed to send report email: {exc}'}, status=500)

    return JsonResponse({'ok': True, 'message': 'Review report sent.'})


@cache_page(60 * 5)
def home(request):
    subject_list = Subject.objects.only('id', 'name').order_by('id')
    total_questions = Question.objects.count()
    return render(request, 'home.html', {
        'subjects': subject_list,
        'total_questions': total_questions,
    })


def chapters(request, subject_id):
    subject = get_object_or_404(Subject, id=subject_id)
    chapters_list = Chapter.objects.filter(subject=subject).order_by('id')
    return render(request, 'chapter.html', {'subject': subject, 'chapters': chapters_list})


def subchapters(request, chapter_id):
    """View to list subchapters for a chapter that has them (e.g., Organic Chemistry)."""
    chapter = get_object_or_404(Chapter, id=chapter_id)
    subchapter_list = SubChapter.objects.filter(chapter=chapter).order_by('order')
    return render(request, 'subchapter.html', {
        'chapter': chapter,
        'subchapters': subchapter_list,
    })


def quiz(request, chapter_id):
    chapter = get_object_or_404(Chapter, id=chapter_id)
    user_name = request.GET.get('name') or request.POST.get('name')
    quiz_started = (request.GET.get('start') == '1' and user_name)
    attempt_reference = _attempt_reference(request.session, f'quiz_{chapter_id}')
    
    if request.method == 'POST':
        user_name = request.POST.get('name', '').strip()
        if not user_name:
            messages.error(request, 'Name is required to submit the quiz.')
            return redirect('quiz', chapter_id=chapter_id)
        
        try:
            # Ensure database connection is active
            connection.ensure_connection()
            
            questions_ids = request.session.get(f'quiz_questions_{chapter_id}', [])
            
            # Check if session data exists
            if not questions_ids:
                messages.error(request, 'Session expired. Please restart the quiz.')
                return redirect('quiz', chapter_id=chapter_id)
            
            questions_qs = Question.objects.filter(id__in=questions_ids).select_related('chapter', 'sub_chapter')
            id_to_question = {q.id: q for q in questions_qs}
            questions = [id_to_question[qid] for qid in questions_ids if qid in id_to_question]
            
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
            
            # Save result with error handling
            try:
                TestResult.objects.create(
                    name=user_name,
                    topic=chapter.name,
                    score=final_score,
                    total_attempted=total_attempted
                )
            except Exception as db_error:
                messages.warning(request, 'Result calculated but may not be saved. Please contact admin.')
                print(f"DB Error: {db_error}")
            
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
                **result_metrics,
            })
            
        except Exception as e:
            messages.error(request, f'Error processing submission: {str(e)}. Please try again.')
            return redirect('quiz', chapter_id=chapter_id)
    
    else:
        user_name = request.GET.get('name', '').strip()
        quiz_started = request.GET.get('start') == '1' and bool(user_name)
        questions = []

        if quiz_started:
            attempt_reference = _attempt_reference(request.session, f'quiz_{chapter_id}')
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
        })


def subchapter_quiz(request, subchapter_id):
    """Quiz view for a specific subchapter."""
    sub_chapter = get_object_or_404(SubChapter, id=subchapter_id)
    chapter = sub_chapter.chapter
    session_key = f'quiz_questions_sub_{subchapter_id}'
    attempt_reference = _attempt_reference(request.session, f'subchapter_{subchapter_id}')

    if request.method == 'POST':
        user_name = request.POST.get('name', '').strip()
        if not user_name:
            messages.error(request, 'Name is required to submit the quiz.')
            return redirect('subchapter_quiz', subchapter_id=subchapter_id)

        try:
            connection.ensure_connection()

            questions_ids = request.session.get(session_key, [])

            if not questions_ids:
                messages.error(request, 'Session expired. Please restart the quiz.')
                return redirect('subchapter_quiz', subchapter_id=subchapter_id)

            questions_qs = Question.objects.filter(id__in=questions_ids).select_related('chapter', 'sub_chapter')
            id_to_question = {q.id: q for q in questions_qs}
            questions = [id_to_question[qid] for qid in questions_ids if qid in id_to_question]

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
                TestResult.objects.create(
                    name=user_name,
                    topic=f"{chapter.name} - {sub_chapter.name}",
                    score=final_score,
                    total_attempted=total_attempted
                )
            except Exception as db_error:
                messages.warning(request, 'Result calculated but may not be saved. Please contact admin.')
                print(f"DB Error: {db_error}")

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
                'attempt_reference': attempt_reference,
                'watermark_text': f'{user_name} | Attempt #{attempt_reference}',
                **result_metrics,
            })

        except Exception as e:
            messages.error(request, f'Error processing submission: {str(e)}. Please try again.')
            return redirect('subchapter_quiz', subchapter_id=subchapter_id)

    else:
        user_name = request.GET.get('name', '').strip()
        quiz_started = request.GET.get('start') == '1' and bool(user_name)
        questions = []

        if quiz_started:
            attempt_reference = _attempt_reference(request.session, f'subchapter_{subchapter_id}')
            questions_qs = Question.objects.filter(sub_chapter=sub_chapter)
            questions = _pick_random_questions(questions_qs, limit=50)
            request.session[session_key] = [q.id for q in questions]
        else:
            request.session.pop(session_key, None)

        return render(request, 'quiz.html', {
            'chapter': chapter,
            'sub_chapter': sub_chapter,
            'questions': questions,
            'score': None,
            'user_answers': {},
            'quiz_started': quiz_started,
            'finished': False,
            'attempt_reference': attempt_reference,
            'watermark_text': f'{user_name} | Attempt #{attempt_reference}' if quiz_started else '',
        })


def full_test(request):
    attempt_reference = _attempt_reference(request.session, 'full_test')
    if request.method == "POST":
        user_name = request.POST.get('name', '').strip()
        if not user_name:
            messages.error(request, 'Name is required to submit the test.')
            return redirect('full_test')
        
        try:
            # Ensure database connection is active
            connection.ensure_connection()
            
            questions_ids = request.session.get('full_test_questions', [])
            
            # Check if session data exists
            if not questions_ids:
                messages.error(request, 'Session expired. Please restart the test.')
                return redirect('full_test')

            questions_qs = Question.objects.filter(id__in=questions_ids).select_related('chapter', 'sub_chapter')
            questions = list(questions_qs)
            id_to_question = {q.id: q for q in questions}
            questions = [id_to_question[qid] for qid in questions_ids if qid in id_to_question]
            
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
                TestResult.objects.create(
                    name=user_name,
                    topic="Full Test",
                    score=final_score,
                    total_attempted=total_attempted
                )
            except Exception as db_error:
                messages.warning(request, 'Result calculated but may not be saved. Please contact admin.')
                print(f"DB Error: {db_error}")
            
            request.session.pop('full_test_questions', None)
            
            return render(request, 'full_test.html', {
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
                **result_metrics,
            })
            
        except Exception as e:
            messages.error(request, f'Error processing submission: {str(e)}. Please try again.')
            return redirect('full_test')

    else:
        user_name = request.GET.get('name', '').strip()
        quiz_started = request.GET.get('start') == '1' and bool(user_name)

        if not quiz_started:
            request.session.pop('full_test_questions', None)
            return render(request, 'full_test.html', {
                'questions': [],
                'score': None,
                'quiz_started': False,
                'user_answers': {},
                'finished': False,
                'attempt_reference': attempt_reference,
                'watermark_text': '',
            })

        chapters = Chapter.objects.filter(
            subject__name__in=['Biology', 'Physics', 'Chemistry']
        ).only('id', 'name', 'has_subchapters').order_by('id')

        selected_ids = []

        for chapter in chapters:
            weight_match = re.search(r'\((\d+)\)\s*$', chapter.name)
            if not weight_match:
                continue

            target_count = int(weight_match.group(1))
            if target_count <= 0:
                continue

            chapter_questions = Question.objects.filter(chapter_id=chapter.id)

            if chapter.has_subchapters:
                primary_ids = _sample_question_ids(chapter_questions.filter(sub_chapter__isnull=False), target_count)
                remaining = target_count - len(primary_ids)
                fallback_ids = _sample_question_ids(chapter_questions.filter(sub_chapter__isnull=True), remaining)
                selected_ids.extend(primary_ids)
                selected_ids.extend(fallback_ids)
            else:
                selected_ids.extend(_sample_question_ids(chapter_questions, target_count))

        random.shuffle(selected_ids)

        questions_qs = Question.objects.filter(id__in=selected_ids).select_related('chapter', 'sub_chapter')
        id_to_question = {q.id: q for q in questions_qs}
        questions = [id_to_question[qid] for qid in selected_ids if qid in id_to_question]

        request.session['full_test_questions'] = [q.id for q in questions]

        return render(request, 'full_test.html', {
            'questions': questions,
            'score': None,
            'quiz_started': True,
            'user_answers': {},
            'finished': False,
            'attempt_reference': attempt_reference,
            'watermark_text': f'{user_name} | Attempt #{attempt_reference}',
        })


def privacy_policy(request):
    return render(request, 'privacy.html')


def blog_index(request):
    posts = []
    for slug in BLOG_POST_ORDER:
        post = BLOG_POSTS[slug]
        posts.append({
            'slug': slug,
            'title': post['title'],
            'tag': post['tag'],
            'excerpt': post['excerpt'],
        })
    return render(request, 'blog.html', {'posts': posts})


def blog_post(request, slug):
    post = BLOG_POSTS.get(slug)
    if not post:
        raise Http404('Blog post not found')

    custom_template = BLOG_CUSTOM_TEMPLATES.get(slug)
    if custom_template:
        return render(request, custom_template)

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

    return render(request, 'blog_post.html', {
        'slug': slug,
        'post': post_with_depth,
        'related_links': BLOG_INTERNAL_LINKS.get(slug, []),
    })