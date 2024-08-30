from django.urls import path,re_path
from ..views import *

app_name = 'entrance_quiz'
urlpatterns = [

    path('registration', quizView.registration, name='registration'),
    path('checking-OTP', quizView.validatingOTP, name='checking-OTP'),
    path('quiz-terms', quizView.quizTerm, name='quiz-terms'),
    path('quiz-start', quizView.quizStart, name='quiz-start'),
    path('quiz-questions', quizView.quizQuestions, name='quiz-questions'),
    path('quiz-save', quizView.quizSave, name='quiz-save'),
    path('quiz-submit', quizView.quizSubmit, name='quiz-submit'),
    path('ajax-quest', quizView.ajaxQuizQuestion, name='ajax-quest'),
    path('quiz-terms-decline', quizView.declineTerms, name='quiz-terms-decline'),
]