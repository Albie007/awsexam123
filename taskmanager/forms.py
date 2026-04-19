from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from .models import Task, Category


class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model  = User
        fields = ['username', 'email', 'password1', 'password2']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-input'})


class LoginForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-input'})


class TaskForm(forms.ModelForm):
    class Meta:
        model  = Task
        fields = ['title', 'description', 'category', 'priority', 'status', 'due_date']
        widgets = {
            'title':       forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Task title'}),
            'description': forms.Textarea(attrs={'class': 'form-input', 'rows': 3, 'placeholder': 'Description (optional)'}),
            'category':    forms.Select(attrs={'class': 'form-input'}),
            'priority':    forms.Select(attrs={'class': 'form-input'}),
            'status':      forms.Select(attrs={'class': 'form-input'}),
            'due_date':    forms.DateInput(attrs={'class': 'form-input', 'type': 'date'}),
        }


class CategoryForm(forms.ModelForm):
    class Meta:
        model  = Category
        fields = ['name', 'color']
        widgets = {
            'name':  forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Category name'}),
            'color': forms.TextInput(attrs={'class': 'color-picker', 'type': 'color'}),
        }
