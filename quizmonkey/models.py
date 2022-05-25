from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class Quiz(models.Model):
    title = models.CharField(max_length=100)
    description = models.CharField(max_length=400)
    start_date = models.DateTimeField('date published', max_length=400)
    end_date = models.DateTimeField('date ended', max_length=400)
    creator = models.ForeignKey(User, on_delete=models.CASCADE)
    code = models.IntegerField()

    def __str__(self):
        return self.title


class Question(models.Model):
    question_text = models.CharField(max_length=200)
    score = models.IntegerField(default=0, validators=[MinValueValidator(1), MaxValueValidator(100)])
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name="question")

    def __str__(self):
        return self.question_text


class Choice(models.Model):
    choice_text = models.CharField(max_length=200)
    is_answer = models.BooleanField()
    # quiz = models.ForeignKey(Quiz, on_delete=models.PROTECT, related_name="quiz")
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name="choice")

    def __str__(self):
        return self.choice_text


class UserSubmission(models.Model):
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name="submission")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="submission")
    created_at = models.DateTimeField(default=timezone.now)
    is_complete = models.BooleanField(default=False)
    grade = models.IntegerField(default=0)


class UserAnswer(models.Model):
    submission = models.ForeignKey(UserSubmission, on_delete=models.CASCADE, related_name="user_answer")
    choice = models.ForeignKey(Choice, on_delete=models.CASCADE, related_name="user_answer")

