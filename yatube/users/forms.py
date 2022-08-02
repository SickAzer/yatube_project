from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model
from .models import Contact


User = get_user_model()


class CreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('first_name', 'last_name', 'username', 'email')
        labels = {
            'first_name': 'Имя',
            'last_name': 'Фамилия',
            'username': 'Имя пользователя',
            'email': 'Адрес электронной почты'
        }
        help_texts = {
            'first_name': 'Введите имя',
            'last_name': 'Введите фамилию',
            'username': 'Введите имя пользователя',
            'email': 'Введите адрес электронной почты'
        }


class ContactForm(forms.ModelForm):
    class Meta:
        model = Contact
        fields = ('name', 'email', 'subject', 'body')
