import random
import re
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.cache import cache_page
from django.db import connection
from .models import Subject, Chapter, SubChapter, Question, TestResult


def _pick_random_questions(base_queryset, limit=50):
    """Sample random questions efficiently by sampling IDs first."""
    question_ids = list(base_queryset.values_list('id', flat=True))
    if not question_ids:
        return []

    selected_ids = random.sample(question_ids, min(limit, len(question_ids)))
    selected_qs = Question.objects.filter(id__in=selected_ids).select_related('chapter', 'sub_chapter')
    id_to_question = {q.id: q for q in selected_qs}
    return [id_to_question[qid] for qid in selected_ids if qid in id_to_question]


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
                'total_attempted': total_attempted,
                'total_correct': total_correct,
                'total_wrong': total_wrong,
                'total_skipped': total_skipped,
                'total_questions': total_questions,
                'user_answers': user_answers,
                'quiz_started': True,
                'finished': True
            })
            
        except Exception as e:
            messages.error(request, f'Error processing submission: {str(e)}. Please try again.')
            return redirect('quiz', chapter_id=chapter_id)
    
    else:
        user_name = request.GET.get('name', '').strip()
        quiz_started = request.GET.get('start') == '1' and bool(user_name)
        questions = []

        if quiz_started:
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
            'finished': False
        })


def subchapter_quiz(request, subchapter_id):
    """Quiz view for a specific subchapter."""
    sub_chapter = get_object_or_404(SubChapter, id=subchapter_id)
    chapter = sub_chapter.chapter
    session_key = f'quiz_questions_sub_{subchapter_id}'

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
                'total_attempted': total_attempted,
                'total_correct': total_correct,
                'total_wrong': total_wrong,
                'total_skipped': total_skipped,
                'total_questions': total_questions,
                'user_answers': user_answers,
                'quiz_started': True,
                'finished': True
            })

        except Exception as e:
            messages.error(request, f'Error processing submission: {str(e)}. Please try again.')
            return redirect('subchapter_quiz', subchapter_id=subchapter_id)

    else:
        user_name = request.GET.get('name', '').strip()
        quiz_started = request.GET.get('start') == '1' and bool(user_name)
        questions = []

        if quiz_started:
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
            'finished': False
        })


def full_test(request):
    user_name = request.GET.get('name') or request.POST.get('name')
    
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
            
            questions = list(Question.objects.filter(id__in=questions_ids))
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
                'total_attempted': total_attempted,
                'total_correct': total_correct,
                'total_wrong': total_wrong,
                'total_skipped': total_skipped,
                'total_questions': total_questions,
                'user_answers': user_answers,
                'quiz_started': True,
                'finished': True
            })
            
        except Exception as e:
            messages.error(request, f'Error processing submission: {str(e)}. Please try again.')
            return redirect('full_test')
    
    else:
        user_name = request.GET.get('name', '').strip()
        chapters = Chapter.objects.filter(
            subject__name__in=['Biology', 'Physics', 'Chemistry']
        ).order_by('id')

        questions = []

        for chapter in chapters:
            weight_match = re.search(r'\((\d+)\)\s*$', chapter.name)
            if not weight_match:
                continue

            target_count = int(weight_match.group(1))
            if target_count <= 0:
                continue

            chapter_questions = Question.objects.filter(chapter=chapter)

            if chapter.has_subchapters and chapter_questions.filter(sub_chapter__isnull=False).exists():
                primary_pool = list(chapter_questions.filter(sub_chapter__isnull=False))
                fallback_pool = list(chapter_questions.filter(sub_chapter__isnull=True))
            else:
                primary_pool = list(chapter_questions)
                fallback_pool = []

            selected = random.sample(primary_pool, min(target_count, len(primary_pool)))

            remaining = target_count - len(selected)
            if remaining > 0 and fallback_pool:
                selected.extend(random.sample(fallback_pool, min(remaining, len(fallback_pool))))

            questions.extend(selected)

        random.shuffle(questions)
        
        request.session['full_test_questions'] = [q.id for q in questions]
        
        return render(request, 'full_test.html', {
            'questions': questions,
            'score': None,
            'quiz_started': False,
            'user_answers': {},
            'finished': False
        })