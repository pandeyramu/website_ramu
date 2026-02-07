import random
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.db import connection
from .models import Subject, Chapter, Question, TestResult


@csrf_exempt
def keepalive(request):
    """Keep database connection alive - for Uptime Robot and client pings"""
    try:
        # Ensure database connection is active
        connection.ensure_connection()
        # Simple query to keep DB active
        Subject.objects.first()
        return HttpResponse("OK", status=200)
    except Exception as e:
        return HttpResponse(f"Error: {str(e)}", status=500)


def home(request):
    subject_list = Subject.objects.all()
    return render(request, 'home.html', {'subjects': subject_list})


def chapters(request, subject_id):
    subject = get_object_or_404(Subject, id=subject_id)
    chapters_list = Chapter.objects.filter(subject=subject)
    return render(request, 'chapter.html', {'subject': subject, 'chapters': chapters_list})


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
            
            questions_qs = Question.objects.filter(id__in=questions_ids)
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
        questions_qs = Question.objects.filter(chapter=chapter)
        questions_count = min(50, questions_qs.count())
        questions = random.sample(list(questions_qs), questions_count)
        request.session[f'quiz_questions_{chapter_id}'] = [q.id for q in questions]
        quiz_started = request.GET.get('start') == '1'
        
        return render(request, 'quiz.html', {
            'chapter': chapter,
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
        biology_questions = list(Question.objects.filter(chapter__subject__name='Biology'))
        physics_questions = list(Question.objects.filter(chapter__subject__name='Physics'))
        chemistry_questions = list(Question.objects.filter(chapter__subject__name='Chemistry'))
        
        selected_biology = random.sample(biology_questions, min(80, len(biology_questions)))
        selected_physics = random.sample(physics_questions, min(50, len(physics_questions)))
        selected_chemistry = random.sample(chemistry_questions, min(50, len(chemistry_questions)))
        
        questions = selected_biology + selected_physics + selected_chemistry
        
        request.session['full_test_questions'] = [q.id for q in questions]
        
        return render(request, 'full_test.html', {
            'questions': questions,
            'score': None,
            'quiz_started': False,
            'user_answers': {},
            'finished': False
        })