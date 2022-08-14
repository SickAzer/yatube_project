from django.contrib.auth import get_user_model
from django.test import TestCase

from ..models import Group, Post

User = get_user_model()


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='Тестовый слаг',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост',
        )


    def test_models_have_correct_object_names(self):
        """Проверяем, что у моделей корректно работает __str__."""
        post = PostModelTest.post
        group = PostModelTest.group
        expected_post_name = post.text[:15]
        expected_group_name = group.title
        self.assertEqual(expected_post_name, str(post))
        self.assertEqual(expected_group_name, str(group))
        
        
    def test_verbose_name(self):
        post = PostModelTest.post
        group = PostModelTest.group
        field_verboses_post = {
            'text': 'Текст поста',
            'pub_date': 'Дата публикации',
            'author': 'Автор',
            'group': 'Группа'
        }
        field_verboses_group = {
            'title': 'Название группы',
            'slug': 'Адрес для страницы группы',
            'description': 'Описание группы'
        }
        for value, expected in field_verboses_post.items():
            with self.subTest(value=value):
                self.assertEqual(
                    post._meta.get_field(value).verbose_name, expected)
        for value, expected in field_verboses_group.items():
            with self.subTest(value=value):
                self.assertEqual(
                    group._meta.get_field(value).verbose_name, expected)
                
                
    def test_help_text(self):
        post = PostModelTest.post
        group = PostModelTest.group
        field_help_text_post = {
            'text': 'Напишите здесь свой пост',
            'pub_date': 'Дата публикации поста',
            'author': 'Автор поста',
            'group': 'Выберите группу для поста'
        }
        field_help_text_group = {
            'title': 'Дайте название для группы',
            'slug': 'Укажите адрес для страницы группы',
            'description': 'Дайте описание группы'
        }
        for value, expected in field_help_text_post.items():
            with self.subTest(value=value):
                self.assertEqual(
                    post._meta.get_field(value).help_text, expected)
        for value, expected in field_help_text_group.items():
            with self.subTest(value=value):
                self.assertEqual(
                    group._meta.get_field(value).help_text, expected)