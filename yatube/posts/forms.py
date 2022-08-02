from django import forms

from .models import Post, Group


# Добавил в форму label и helptext а русском
class PostForm(forms.ModelForm):

    class Meta:
        model = Post
        fields = ('text', 'group')
        labels = {
            'text': 'Текст поста',
            'group': 'Группа'
        }
        help_texts = {
            'text': 'Напишите свой пост здесь',
            'group': 'Выберите нужную группу из списка'
        }

    def clean_text(self):
        data = self.cleaned_data['text']
        if not data:
            raise forms.ValidationError('Пост не может быть пустым!')
        return data