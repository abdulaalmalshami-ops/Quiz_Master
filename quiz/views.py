from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.db.models import Sum, Count, F
from django.contrib.auth import authenticate
from django.http import HttpResponse
from .models import *
from django.contrib.auth.decorators import login_required
from .forms import *
from django.forms import formset_factory

@login_required(login_url='login')
def quiz_list(request):
    quizzes = Quiz.objects.all()
    return render(request, 'quiz/quiz_list.html', {'quizzes': quizzes})

def quiz_detail(request, id):
    quiz = get_object_or_404(Quiz, id=id)
    questions = quiz.question_set.all()
    return render(request, 'quiz/quiz_detail.html', {'quiz': quiz,'questions': questions})

@login_required(login_url='login')
def quiz_create(request):
    if not request.user.is_superuser:
        messages.error(request, "Access denied: Superuser permissions required.")
        return redirect('quiz_list')
    if request.method == 'POST':
        form = QuizForm(request.POST)
        if form.is_valid():
            quiz = form.save()
            if 'save_another' in request.POST:
                messages.success(request, f"Quiz '{quiz.title}' created successfully. Add another one below.")
                return redirect('quiz_create')
            messages.success(request, f"Quiz '{quiz.title}' created successfully.")
            return redirect('quiz_detail', id=quiz.id)
    else:
        form = QuizForm()
    return render(request, 'quiz/quiz_form.html', {'form': form, 'action': 'Create'})

@login_required(login_url='login')
def quiz_edit(request, id):
    if not request.user.is_superuser:
        messages.error(request, "Access denied: Superuser permissions required.")
        return redirect('quiz_list')
    quiz = get_object_or_404(Quiz, id=id)
    if request.method == 'POST':
        form = QuizForm(request.POST, instance=quiz)
        if form.is_valid():
            form.save()
            messages.success(request, f"Quiz '{quiz.title}' edited successfully.")
            return redirect('quiz_detail', id=quiz.id)
    else:
        form = QuizForm(instance=quiz)
    return render(request, 'quiz/quiz_form.html', {'form': form, 'action': 'Edit'})

@login_required(login_url='login')
def quiz_delete(request, id):
    if not request.user.is_superuser:
        messages.error(request, "Access denied: Superuser permissions required.")
        return redirect('quiz_list')
    quiz = get_object_or_404(Quiz, id=id)
    if request.method == 'POST':
        quiz.delete()
        return redirect('quiz_list')
    return render(request, 'quiz/quiz_confirm_delete.html', {'quiz': quiz})

@login_required(login_url='login')
def take_quiz(request, id):
    quiz = get_object_or_404(Quiz, id=id)

    # Verification Check
    if not request.session.get(f'verified_quiz_{id}'):
        return redirect('verify_quiz_access', id=id)
    
    # Check if user already took this quiz
    if QuizResult.objects.filter(user=request.user, quiz=quiz).exists():
        messages.info(request, "You have already completed this quiz.")
        return redirect('quiz_results')

    questions = quiz.question_set.all()
    
    if request.method == 'POST':
        # Check if this is the final confirmation
        if not request.POST.get('final_submit'):
            return render(request, 'quiz/quiz_confirm_submit.html', {
                'quiz': quiz,
                'answers': request.POST.dict()
            })

        try:
            # First pass: Calculate score and prepare answers
            user_answers_to_save = []
            score = 0
            total = questions.count()
            
            for question in questions:
                selected_choice_id = request.POST.get(f'question_{question.id}')
                selected_choice = None
                is_correct = False
                
                if selected_choice_id:
                    try:
                        selected_choice = Choice.objects.get(id=selected_choice_id)
                        if selected_choice.is_correct:
                            score += 1
                            is_correct = True
                    except (Choice.DoesNotExist, ValueError):
                        pass
                
                user_answers_to_save.append({
                    'question': question,
                    'selected_choice': selected_choice,
                    'is_correct': is_correct
                })
            
            result = QuizResult.objects.create(
                user=request.user,
                quiz=quiz,
                score=score,
                total_questions=total
            )
            
            # Second pass: Save UserAnswers
            for ans in user_answers_to_save:
                UserAnswer.objects.create(
                    quiz_result=result,
                    question=ans['question'],
                    selected_choice=ans['selected_choice'],
                    is_correct=ans['is_correct']
                )

            return render(request, 'quiz/quiz_result.html', {
                'quiz': quiz,
                'score': score,
                'total': total,
                'incorrect': total - score,
                'percentage': (score/total*100) if total > 0 else 0,
                'result_id': result.id  # Pass ID if we want to show details link immediately
            })
        except Exception as e:
            messages.error(request, f"خطأ أثناء حفظ النتيجة: {str(e)}")
            return redirect('quiz_detail', id=quiz.id)
        
    return render(request, 'quiz/take_quiz.html', {'quiz': quiz, 'questions': questions})

@login_required(login_url='login')
def add_question(request, id):
    if not request.user.is_superuser:
        messages.error(request, "Access denied: Superuser permissions required.")
        return redirect('quiz_detail', id=id)
    quiz = get_object_or_404(Quiz, id=id)
    ChoiceFormSet = formset_factory(ChoiceForm, extra=4, can_delete=False)
    
    if request.method == 'POST':
        question_form = QuestionForm(request.POST)
        formset = ChoiceFormSet(request.POST)
        
        if question_form.is_valid() and formset.is_valid():
            question = question_form.save(commit=False)
            question.quiz = quiz
            question.save()
            
            for form in formset:
                if form.cleaned_data.get('text'):
                    choice = form.save(commit=False)
                    choice.question = question
                    choice.save()
            
            messages.success(request, "Question added successfully!")
            
            if 'save_another' in request.POST:
                return redirect('add_question', id=quiz.id)
            return redirect('quiz_detail', id=quiz.id)
    else:
        question_form = QuestionForm()
        formset = ChoiceFormSet()
        
    return render(request, 'quiz/add_question.html', {
        'quiz': quiz,
        'question_form': question_form,
        'formset': formset
    })

@login_required(login_url='login')
def question_edit(request, id):
    question = get_object_or_404(Question, id=id)
    if not request.user.is_superuser:
        messages.error(request, "Access denied: Superuser permissions required.")
        return redirect('quiz_detail', id=question.quiz.id)
    quiz = question.quiz
    ChoiceFormSet = formset_factory(ChoiceForm, extra=0, can_delete=False)
    choices = question.choice_set.all()
    
    if request.method == 'POST':
        question_form = QuestionForm(request.POST, instance=question)
        initial_data = [{'text': c.text, 'is_correct': c.is_correct} for c in choices]
        formset = ChoiceFormSet(request.POST)
        
        if question_form.is_valid() and formset.is_valid():
            question_form.save()
            # Simplest way to update choices is to delete and recreate for this MVP
            question.choice_set.all().delete()
            for form in formset:
                if form.cleaned_data.get('text'):
                    choice = form.save(commit=False)
                    choice.question = question
                    choice.save()
            return redirect('quiz_detail', id=quiz.id)
    else:
        question_form = QuestionForm(instance=question)
        initial_data = [{'text': c.text, 'is_correct': c.is_correct} for c in choices]
        # Use a formset with initial data for choices
        ChoiceFormSet = formset_factory(ChoiceForm, extra=max(0, 4 - len(choices)))
        formset = ChoiceFormSet(initial=[{'text': c.text, 'is_correct': c.is_correct} for c in choices])

    return render(request, 'quiz/add_question.html', {
        'quiz': quiz,
        'question_form': question_form,
        'formset': formset,
        'action': 'Edit'
    })

@login_required(login_url='login')
def question_delete(request, id):
    question = get_object_or_404(Question, id=id)
    quiz_id = question.quiz.id
    if not request.user.is_superuser:
        messages.error(request, "Access denied: Superuser permissions required.")
        return redirect('quiz_detail', id=quiz_id)
    if request.method == 'POST':
        question.delete()
        return redirect('quiz_detail', id=quiz_id)
    return render(request, 'quiz/question_confirm_delete.html', {'question': question})

@login_required(login_url='login')
def quiz_results(request):
    if request.user.is_superuser:
        results = QuizResult.objects.all().select_related('user', 'quiz').order_by('-date_taken')
    else:
        results = QuizResult.objects.filter(user=request.user).select_related('quiz').order_by('-date_taken')
    return render(request, 'quiz/quiz_results_list.html', {'results': results})

@login_required(login_url='login')
def quiz_result_detail(request, id):
    result = get_object_or_404(QuizResult, id=id)
    # Ensure user can only view their own results unless superuser
    if not request.user.is_superuser and result.user != request.user:
        messages.error(request, "Access denied.")
        return redirect('quiz_results')
        
    user_answers = UserAnswer.objects.filter(quiz_result=result).select_related('question', 'selected_choice')
    
    return render(request, 'quiz/quiz_result_detail.html', {
        'result': result,
        'user_answers': user_answers
    })



@login_required(login_url='login')
def reset_quiz_result(request, id):
    if not request.user.is_superuser:
        messages.error(request, "Access denied: Superuser permissions required.")
        return redirect('quiz_results')
        
    result = get_object_or_404(QuizResult, id=id)
    
    if request.method == 'POST':
        result.delete()
        messages.success(request, f"Result for {result.user.username} on '{result.quiz.title}' has been reset.")
        return redirect('quiz_results')
        
    return render(request, 'quiz/quiz_result_confirm_reset.html', {'result': result})

@login_required(login_url='login')
def verify_quiz_access(request, id):
    quiz = get_object_or_404(Quiz, id=id)
    
    if request.method == 'POST':
        form = QuizVerificationForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            
            user = authenticate(username=username, password=password)
            
            if user is not None and user == request.user:
                request.session[f'verified_quiz_{id}'] = True
                return redirect('take_quiz', id=id)
            else:
                messages.error(request, "Invalid credentials or wrong user account.")
    else:
        form = QuizVerificationForm()
        
    return render(request, 'quiz/verify_quiz.html', {'form': form, 'quiz': quiz})

