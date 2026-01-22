from django.urls import path
from .views import *
urlpatterns = [
    path('quizzes/', quiz_list, name='quiz_list'),
    path('quizzes/create/', quiz_create, name='quiz_create'),
    path('quizzes/<int:id>/', quiz_detail, name='quiz_detail'),
    path('quizzes/<int:id>/edit/', quiz_edit, name='quiz_edit'),
    path('quizzes/<int:id>/delete/', quiz_delete, name='quiz_delete'),
    path('quizzes/<int:id>/take/', take_quiz, name='take_quiz'),
    path('quizzes/<int:id>/questions/add/', add_question, name='add_question'),
    path('questions/<int:id>/edit/', question_edit, name='question_edit'),
    path('questions/<int:id>/delete/', question_delete, name='question_delete'),
    path('results/', quiz_results, name='quiz_results'),
    path('results/<int:id>/', quiz_result_detail, name='quiz_result_detail'),
    path('results/<int:id>/reset/', reset_quiz_result, name='reset_quiz_result'),
    path('quizzes/<int:id>/verify/', verify_quiz_access, name='verify_quiz_access'),

]