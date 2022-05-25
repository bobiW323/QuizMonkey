from django import forms

from django.contrib.auth.models import User
from django.contrib.auth import authenticate

from quizmonkey.models import Choice, Question, Quiz


class LoginForm(forms.Form):
    username = forms.CharField(max_length=30, widget=forms.TextInput(
        attrs={'size': 13, 'class': 'form-control', 'id': 'UsernameInput', 'required': True,
               'Placeholder': 'Username'}))
    password = forms.CharField(max_length=20, widget=forms.PasswordInput(
        attrs={'size': 13, 'class': 'form-control', 'id': 'PasswordInput', 'required': True,
               'Placeholder': 'Password'}))

    # Customizes form validation for properties that apply to more
    # than one field.  Overrides the forms.Form.clean function.
    def clean(self):
        # Calls our parent (forms.Form) .clean function, gets a dictionary
        # of cleaned data as a result
        cleaned_data = super().clean()

        # Confirms that the two password fields match
        username = cleaned_data.get('username')
        password = cleaned_data.get('password')
        user = authenticate(username=username, password=password)
        if not user:
            raise forms.ValidationError("Invalid username/password")

        # We must return the cleaned data we got from our parent.
        return cleaned_data


class RegisterForm(forms.Form):
    username = forms.CharField(max_length=30, widget=forms.TextInput(
        attrs={'size': 13, 'class': 'form-control', 'id': 'UsernameInput', 'required': True,
               'Placeholder': 'Username'}))
    password = forms.CharField(max_length=20, widget=forms.PasswordInput(
        attrs={'size': 13, 'class': 'form-control', 'id': 'PasswordInput', 'required': True,
               'Placeholder': 'Password'}))
    confirm_password = forms.CharField(max_length=20,
                                       widget=forms.PasswordInput(
                                           attrs={'size': 13, 'class': 'form-control', 'id': 'ConfirmPasswordInput',
                                                  'required': True,
                                                  'Placeholder': 'Confirm Password'}))
    email = forms.CharField(max_length=40,
                            label='E-mail',
                            widget=forms.EmailInput(
                                attrs={'size': 13, 'class': 'form-control', 'id': 'EmailInput', 'required': True,
                                       'Placeholder': 'E-mail Address'}))

    # Customizes form validation for properties that apply to more
    # than one field.  Overrides the forms.Form.clean function.
    def clean(self):
        # Calls our parent (forms.Form) .clean function, gets a dictionary
        # of cleaned data as a result
        cleaned_data = super().clean()

        # Confirms that the two password fields match
        password1 = cleaned_data.get('password')
        password2 = cleaned_data.get('confirm_password')
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords did not match.")

        # We must return the cleaned data we got from our parent.
        return cleaned_data

    # Customizes form validation for the username field.
    def clean_username(self):
        # Confirms that the username is not already present in the
        # User model database.
        username = self.cleaned_data.get('username')
        if User.objects.filter(username__exact=username):
            raise forms.ValidationError("Username is already taken.")

        # We must return the cleaned data we got from the cleaned_data
        # dictionary
        return username


class QuizForm(forms.ModelForm):
    class Meta:
        model = Quiz
        fields = ["title", "description", "start_date", "end_date"]
        widgets = {
            "start_date": forms.DateTimeInput(
                attrs={'type': 'datetime-local', 'class': 'form-control'}, format='%Y-%m-%d %H:%M'),
            "end_date": forms.DateTimeInput(
                attrs={'type': 'datetime-local', 'class': 'form-control'}, format='%Y-%m-%d %H:%M'),
        }


class QuestionForm(forms.ModelForm):
    class Meta:
        model = Question
        fields = ["question_text", "score"]


class ChoiceForm(forms.ModelForm):
    class Meta:
        model = Choice
        fields = ["choice_text", "is_answer"]


class AnswerForm(forms.Form):
    def __init__(self, *args, **kwargs):
        options = kwargs.pop("options")
        choices = {(o.pk, o.choice_text) for o in options}
        super().__init__(*args, **kwargs)
        option_field = forms.ChoiceField(choices=choices, widget=forms.RadioSelect, required=True)
        self.fields["option"] = option_field


class BaseAnswerFormSet(forms.BaseFormSet):
    def get_form_kwargs(self, index):
        kwargs = super().get_form_kwargs(index)
        kwargs["options"] = kwargs["options"][index]
        return kwargs
