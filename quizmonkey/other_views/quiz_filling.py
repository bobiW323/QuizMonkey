from django.forms import formset_factory
from django.shortcuts import get_object_or_404, redirect, render
from django.db import transaction

from quizmonkey.forms import AnswerForm, BaseAnswerFormSet
from quizmonkey.models import Quiz, UserSubmission, Choice, UserAnswer
from django.utils import timezone


def quiz_filling_start(request):
    return render(request, "quizmonkey/quiz_filling_start.html")


def quiz_filling_submit(request):
    context = {}
    if 'pin_input' not in request.POST or not request.POST['pin_input']:
        context['error'] = 'You must enter a valid PIN code'
        return render(request, 'quizmonkey/quiz_filling_start.html', context)

    quizcode = request.POST['pin_input']
    if not quizcode.isdigit():
        context['error'] = 'You must enter a valid PIN code in number format'
        return render(request, 'quizmonkey/quiz_filling_start.html', context)

    try:
        target_quiz = Quiz.objects.filter(code=quizcode).first()
    except IndexError:
        target_quiz = None

    if target_quiz is None:
        context['error'] = 'The PIN code does not exist!'
        return render(request, "quizmonkey/quiz_filling_start.html", context)

    # check time
    # current_time = timezone.localtime(timezone.now())
    current_time = timezone.now()
    if current_time < target_quiz.start_date:
        context['error'] = "The quiz has not began yet!"
        return render(request, "quizmonkey/quiz_filling_start.html", context)
    elif current_time > target_quiz.end_date:
        context['error'] = 'The quiz has been closed!'
        return render(request, "quizmonkey/quiz_filling_start.html", context)

    sub = UserSubmission.objects.create(quiz=target_quiz, user=request.user)

    try:
        # quiz = Quiz.objects.prefetch_related("question_set__choice_set").get(
        quiz = Quiz.objects.prefetch_related("question__choice").get(
            pk=target_quiz.pk
        )
    except Quiz.DoesNotExist:
        context['error'] = 'The quiz does not exist!'
        return render(request, "quizmonkey/quiz_filling_start.html", context)

    try:
        sub = quiz.submission.get(pk=sub.pk)
    except UserSubmission.DoesNotExist:
        context['error'] = 'Submission error!'
        return render(request, "quizmonkey/quiz_filling_start.html", context)

    return redirect("quiz_filling_post", quiz_pk=quiz.pk, sub_pk=sub.pk)


def quiz_filling_post(request, quiz_pk, sub_pk):
    quiz = Quiz.objects.get(pk=quiz_pk)
    sub = UserSubmission.objects.get(pk=sub_pk)
    questions = quiz.question.all()
    options = [q.choice.all() for q in questions]
    total_score = 0
    for q in questions:
        total_score += q.score
    form_kwargs = {"empty_permitted": False, "options": options}
    AnswerFormSet = formset_factory(AnswerForm, extra=len(questions), formset=BaseAnswerFormSet)
    if request.method == "POST":
        print("POST")
        formset = AnswerFormSet(request.POST, form_kwargs=form_kwargs)
        if formset.is_valid():
            with transaction.atomic():
                for form in formset:
                    ans = UserAnswer.objects.create(
                        choice_id=form.cleaned_data["option"], submission_id=sub.pk,
                    )
                    if ans.choice.is_answer:
                        sub.grade += ans.choice.question.score
                sub.save()
                return redirect("quiz_thanks", pk=quiz.pk, score=sub.grade, total=total_score)
    else:
        formset = AnswerFormSet(form_kwargs=form_kwargs)

    # print("formset")
    # print(formset)
    # print("management_form")
    # print(formset.management_form)

    question_forms = zip(questions, formset)
    # print("question_forms")
    # print(question_forms)
    return render(
        request,
        "quizmonkey/quiz_filling_submit.html",
        {"quiz": quiz, "question_forms": question_forms, "formset": formset},
    )


def quiz_filling_thanks(request, pk, score, total):
    """Survey-taker receives a thank-you message."""
    quiz = get_object_or_404(Quiz, pk=pk)
    return render(request, "quizmonkey/thanks.html", {"quiz": quiz, "grade": score, "total": total})
