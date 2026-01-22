from django import forms
from . import models

class QuizForm(forms.ModelForm):
    class Meta:
        model = models.Quiz
        fields = ['title', 'description', 'time_limit']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter quiz title'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Enter quiz description', 'rows': 4}),
            'time_limit': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Duration in minutes', 'min': 1}),
        }

class QuestionForm(forms.ModelForm):
    class Meta:
        model = models.Question
        fields = ['text']
        widgets = {
            'text': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter question text'}),
        }

class QuizVerificationForm(forms.Form):
    username = forms.CharField(max_length=150, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Username'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Password'}))

class ChoiceForm(forms.ModelForm):
    class Meta:
        model = models.Choice
        fields = ['text', 'is_correct']
        widgets = {
            'text': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Choice text'}),
            'is_correct': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
