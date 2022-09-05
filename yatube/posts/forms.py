from django import forms

from .models import Group, Post, Comment


# Добавил в форму label и helptext а русском
class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ('title', 'text', 'group', 'image')
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
    
class GroupForm(forms.ModelForm):
    class Meta:
        model = Group
        fields = ('title', 'slug', 'description')
        labels = {
                'title': 'Название группы',
                'slug': 'Адрес группы',
                'description': 'Описание группы'
            }
        help_texts = {
                'title': 'Назовите свою группу',
                'slug': (
                    'Введите адрес группы.'
                    ' Допустимы латинские буквы, цифры, дефисы и нижние подчеркивания'
                ),
                'description': 'Введите описание группы (опционально)'
            }


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('text',)
        labels = {
            'text': 'Текст комментария'
        }
        help_texts = {
            'text': 'Напишите свой коммментарий здесь'
        }

    def clean_text(self):
        data = self.cleaned_data['text']
        if not data:
            raise forms.ValidationError('Комментарий не может быть пустым!')
        return data
