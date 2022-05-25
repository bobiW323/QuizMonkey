from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from django.urls import reverse
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
import xlwt
from django.contrib.auth.models import User

from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, Http404, HttpResponseRedirect

from quizmonkey.forms import LoginForm, RegisterForm, QuizForm, QuestionForm, ChoiceForm, AnswerForm, BaseAnswerFormSet
from quizmonkey.models import Quiz, Question, UserAnswer, UserSubmission, Choice
from quizmonkey.utilities import random_code
import json

r_code = random_code.random_code()


def front_page(request):
    return render(request, 'quizmonkey/front_page.html')


def login_action(request):
    context = {}

    # Just display the registration form if this is a GET request.
    if request.method == 'GET':
        context['form'] = LoginForm()
        return render(request, 'quizmonkey/login.html', context)

    # Creates a bound form from the request POST parameters and makes the
    # form available in the request context dictionary.
    form = LoginForm(request.POST)
    context['form'] = form

    # Validates the form.
    if not form.is_valid():
        return render(request, 'quizmonkey/login.html', context)

    new_user = authenticate(username=form.cleaned_data['username'],
                            password=form.cleaned_data['password'])

    login(request, new_user)
    return redirect(reverse('main-page'))


def logout_action(request):
    logout(request)
    return redirect(reverse('login'))


def register_action(request):
    context = {}

    # Just display the registration form if this is a GET request.
    if request.method == 'GET':
        context['form'] = RegisterForm()
        return render(request, 'quizmonkey/register.html', context)

    # Creates a bound form from the request POST parameters and makes the
    # form available in the request context dictionary.
    form = RegisterForm(request.POST)
    context['form'] = form

    # Validates the form.
    if not form.is_valid():
        return render(request, 'quizmonkey/register.html', context)

    # At this point, the form data is valid.  Register and login the user.
    new_user = User.objects.create_user(username=form.cleaned_data['username'],
                                        password=form.cleaned_data['confirm_password'],
                                        email=form.cleaned_data['email'])
    new_user.save()

    new_user = authenticate(username=form.cleaned_data['username'],
                            password=form.cleaned_data['confirm_password'])

    login(request, new_user)
    return redirect(reverse('main-page'))


def _my_json_error_response(message, status=200):
    # You can create your JSON by constructing the string representation yourself (or just use json.dumps)
    response_json = '{ "error": "' + message + '" }'
    return HttpResponse(response_json, content_type='application/json', status=status)


def main_page(request):
    if not request.user.id:
        return redirect(reverse('register'))
    return render(request, 'quizmonkey/main_page.html')


@login_required
def quiz_list(request):
    quizzes = Quiz.objects.filter(creator=request.user).order_by("start_date").reverse().all()
    return render(request, "quizmonkey/list.html", {"quizzes": quizzes})


@login_required
def create(request):
    """User can create a new quiz"""
    if request.method == "POST":
        form = QuizForm(request.POST)
        if form.is_valid():
            quiz = form.save(commit=False)
            if quiz.end_date < quiz.start_date:
                messages.error(request, "Time error: quiz end time should not be earler than quiz start time")
                return HttpResponseRedirect(reverse('quiz-create'))
            quiz.creator = request.user
            quiz.code = random_code.random_code.get_pin_code(r_code)
            quiz.save()
            return redirect("quiz-edit", pk=quiz.id)
    else:
        form = QuizForm()

    return render(request, "quizmonkey/quiz_creation.html", {"form": form})


@login_required
def edit(request, pk):
    try:
        quiz = Quiz.objects.get(pk=pk, creator=request.user)
    except Quiz.DoesNotExist:
        quiz = None

    form = QuestionForm()
    if quiz is None:
        return render(request, "quizmonkey/edit.html", {
            'message': 'The quiz does not exist or no permission to edit the quiz!'})

    if request.method == "POST":
        quiz.save()
        return redirect("quiz-detail", pk=pk)
    else:
        questions = quiz.question.all()
        return render(request, "quizmonkey/edit.html", {"quiz": quiz, "questions": questions, "QuestionForm": form})


# def copy_code(request, pk):
#     try:
#         quiz = Quiz.objects.get(pk=pk, creator=request.user)
#     except Quiz.DoesNotExist:
#         quiz = None
#     if quiz is None:
#         return render(request, "quizmonkey/detail.html",
#                       {"message":"The quiz does not exist or no permission to edit the quiz!"})
#     pyperclip.copy(quiz.code)
#     return redirect('quiz-detail', pk=pk)


@login_required
def delete(request, pk):
    """User can delete an existing quiz"""

    quiz = get_object_or_404(Quiz, pk=pk, creator=request.user)
    if request.method == "POST":
        quiz.delete()
    return redirect("quiz-list")


@login_required
def question_create(request, pk):
    try:
        quiz = Quiz.objects.get(pk=pk, creator=request.user)
    except Quiz.DoesNotExist:
        quiz = None

    form = QuestionForm()
    if quiz is None:
        return render(request, "quizmonkey/edit.html", {
            'message': 'The quiz does not exist or no permission to edit the quiz!'})

    if request.method == "POST":
        form = QuestionForm(request.POST)
        if form.is_valid():
            question = form.save(commit=False)
            question.quiz = quiz
            question.save()
            return redirect("quiz-option-create", quiz_pk=pk, question_pk=question.pk)

    return render(request, "quizmonkey/edit.html", {"quiz": quiz, "QuestionForm": form})


@login_required
def option_create(request, quiz_pk, question_pk):
    try:
        quiz = Quiz.objects.get(pk=quiz_pk, creator=request.user)
    except Quiz.DoesNotExist:
        quiz = None

    if quiz is None:
        return render(request, "quizmonkey/edit.html", {
            'message': 'The quiz does not exist or no permission to edit the quiz!'})

    try:
        question = Question.objects.get(pk=question_pk)
    except Question.DoesNotExist:
        question = None
    if question is None:
        return render(request, "quizmonkey/edit.html", {"quiz": quiz, "question": question,
                                                        'message': 'The question does not exist'})

    if request.method == "POST":
        form = ChoiceForm(request.POST)
        if form.is_valid():
            option = form.save(commit=False)
            option.question_id = question_pk
            option.save()
            redirect('quiz-option-create', quiz_pk, question_pk)

    form = ChoiceForm()
    choices = question.choice.all()
    return render(
        request,
        "quizmonkey/edit.html",
        {"quiz": quiz, "question": question, "choices": choices, "choiceForm": form},
    )


@login_required
def delete_option(request, pk):
    choice = get_object_or_404(Choice, pk=pk)
    question_pk = choice.question.pk
    quiz_pk = choice.question.quiz.pk
    if request.method == "POST":
        choice.delete()
    return redirect("quiz-option-create", question_pk=question_pk, quiz_pk=quiz_pk)


@login_required
def delete_question(request, pk):
    question = get_object_or_404(Question, pk=pk)
    quiz_pk = question.quiz.pk
    if request.method == 'POST':
        question.delete()
    return redirect("quiz-edit", pk=quiz_pk)


@login_required
def detail(request, pk):
    """User can view an active quiz"""
    try:
        quiz = Quiz.objects.get(pk=pk, creator=request.user)
    except Quiz.DoesNotExist:
        raise Http404()
    questions = quiz.question.all()
    # for question in questions:
    #     choice_pks = question.choice_set.values_list("pk", flat=True)
    #     total_answers = User_Answer.objects.filter(choice_id__in=choice_pks).count()
    #     for choice in question.choice_set.all():
    #         num_answers = User_Answer.objects.filter(choice=choice).count()
    #
    num_submissions = quiz.submission.filter(is_complete=True).count()
    return render(
        request,
        "quizmonkey/detail.html",
        {
            "quiz": quiz,
            "questions": questions,
            "num_submissions": num_submissions,
        },
    )


def export_quiz_xls(request, pk):
    response = HttpResponse(content_type='application/ms-excel')
    response['Content-Disposition'] = 'attachment; filename="quiz.xls"'
    wb = xlwt.Workbook(encoding='utf-8')
    ws = wb.add_sheet('Quiz')
    # Sheet header, first row
    row_num = 0
    font_style = xlwt.XFStyle()
    font_style.font.bold = True
    columns = ['User', 'Quiz Title', 'Grade']
    quiz = get_object_or_404(Quiz, pk=pk)
    q_num = 1
    submit = UserSubmission.objects.filter(quiz=quiz)
    rows = list(submit.all().values_list('user__username', 'quiz__title', 'grade'))
    for i in range(len(submit.all())):
        sub_list = list(submit.all()[i].user_answer.values_list('choice__choice_text'))
        for sub_L in sub_list:
            rows[i] += sub_L
    for question in quiz.question.all():
        columns.append("Question " + str(q_num) + ": " + question.question_text)
        q_num += 1
    for col_num in range(len(columns)):
        ws.write(row_num, col_num, columns[col_num], font_style)
    # Sheet body, remaining rows
    font_style = xlwt.XFStyle()

    for row in rows:
        row_num += 1
        for col_num in range(len(row)):
            ws.write(row_num, col_num, row[col_num], font_style)
    wb.save(response)
    return response


@login_required
def quiz_history_list(request):
    created_quizzes = Quiz.objects.filter(creator=request.user).order_by("start_date").reverse().all()
    submits = UserSubmission.objects.filter(user=request.user).order_by("created_at").reverse().all()

    return render(request, "quizmonkey/quiz_history.html", {"created_quizzes": created_quizzes,
                                                            "submits": submits})


def quiz_stats(request, pk):
    quiz = get_object_or_404(Quiz, pk=pk)
    questions = quiz.question.all()
    total_mark = 0
    num_submissions = quiz.submission.count()
    quiz_submits = quiz.submission.all()
    total_grade = 0
    for submits in quiz_submits:
        total_grade += submits.grade
    if num_submissions == 0:
        ave_grade_quiz = 0
        highest_user = None
    else:
        ave_grade_quiz = round(total_grade / num_submissions, 2)
        highest_user = UserSubmission.objects.filter(quiz=quiz).order_by("grade").reverse().first().user

    for question in questions:
        total_mark += question.score
        choice = question.choice.filter(is_answer=True).first()
        correct_num = UserAnswer.objects.filter(choice=choice).count()
        if num_submissions == 0:
            question.ave_grade_q = 0
        else:
            question.ave_grade_q = round(question.score * correct_num / num_submissions, 2)

    return render(request, "quizmonkey/quiz_stats.html", {
        "quiz": quiz,
        "ave_grade_quiz": ave_grade_quiz,
        "questions": questions,
        "num_submissions": num_submissions,
        "highest_user": highest_user,
    })


def _my_json_error_response(message, status=200):
    # You can create your JSON by constructing the string representation yourself (or just use json.dumps)
    response_json = '{ "error": "' + message + '" }'
    return HttpResponse(response_json, content_type='application/json', status=status)


def get_question_json(request, pk):
    if not request.user.id or len(User.objects.filter(id=request.user.id)) == 0:
        return _my_json_error_response("You must be logged in to do this operation", status=401)
    response_data = {}
    response_question = []

    quiz = Quiz.objects.get(pk=pk)
    question = quiz.question.all()

    for question_item in question.order_by('id'):
        response_option = []
        for option_item in Choice.objects.filter(question_id=question_item.id).order_by('id'):
            option_item = {
                'option_id': option_item.id,
                'option': option_item.choice_text,
                'question_id': option_item.question.id,
                'is_answer': option_item.is_answer
            }
            response_option.append(option_item)

        question_item = {
            'question_id': question_item.id,
            'text': question_item.question_text,
            'score': question_item.score,
            'quiz_id': question_item.quiz.pk,
            'options': response_option
        }
        response_question.append(question_item)

    response_data['questions'] = response_question
    response_json = json.dumps(response_data)
    response = HttpResponse(response_json, content_type='application/json')
    return response
