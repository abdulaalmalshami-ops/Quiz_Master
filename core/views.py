from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.db.models import F
from quiz.models import Quiz, Question, QuizResult

@login_required(login_url='login')
def dashboard(request):
    # Base stats
    total_quizzes = Quiz.objects.count()
    total_questions = Question.objects.count()
    
    # User stats
    user_results = QuizResult.objects.filter(user=request.user).order_by('-date_taken')
    results_count = user_results.count()
    
    # Calculate average score (percentage)
    avg_score = 0
    if results_count > 0:
        total_percentage = 0
        for result in user_results:
            if result.total_questions > 0:
                total_percentage += (result.score / result.total_questions) * 100
        avg_score = round(total_percentage / results_count, 1)

    
    # Get recent activity (last 5)
    recent_activity = user_results[:5]

    context = {
        'total_quizzes': total_quizzes,
        'total_questions': total_questions,
        'user_results_count': results_count,
        'avg_score': avg_score,
        'recent_activity': recent_activity,
    }
    return render(request, 'core/dashboard.html', context)