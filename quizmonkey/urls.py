from django.urls import path
from quizmonkey import views
from quizmonkey.other_views import quiz_filling

urlpatterns = [
    path('', views.front_page, name='front_page'),
    path('login/', views.login_action, name='login'),
    path('logout', views.logout_action, name='logout'),
    path('register', views.register_action, name='register'),
    path('quiz-list', views.quiz_list, name='quiz-list'),
    path('main-page', views.main_page, name='main-page'),
    path('quiz-create', views.create, name='quiz-create'),
    path('quiz-delete/<int:pk>', views.delete, name='quiz-delete'),
    # path('copy-code/<int:pk>', views.copy_code, name='copy-code'),
    path('quiz-edit/<int:pk>', views.edit, name='quiz-edit'),
    path('quiz-question-create/<int:pk>', views.question_create, name='quiz-question-create'),
    path('quiz-detail/<int:pk>', views.detail, name='quiz-detail'),
    path('quiz-option-create/<int:quiz_pk>/<int:question_pk>', views.option_create, name='quiz-option-create'),
    path('delete-option/<int:pk>', views.delete_option, name='delete-option'),
    path('delete-question/<int:pk>', views.delete_question, name='delete-question'),
    path('export/<int:pk>', views.export_quiz_xls, name='export'),
    path('quiz-history', views.quiz_history_list, name='quiz-history'),
    path('quiz-stats/<int:pk>', views.quiz_stats, name='quiz-stats'),
    path('quiz_filling_start', quiz_filling.quiz_filling_start, name='quiz_filling_start'),
    path('quiz_filling_submit', quiz_filling.quiz_filling_submit, name='quiz_filling_submit'),
    path('quiz_filling_post/<int:quiz_pk>/<int:sub_pk>', quiz_filling.quiz_filling_post, name='quiz_filling_post'),
    path('quiz_thanks/<int:pk>/<int:score>/<int:total>', quiz_filling.quiz_filling_thanks, name='quiz_thanks'),
    path('get-question/<int:pk>', views.get_question_json, name='get-question'),
]
