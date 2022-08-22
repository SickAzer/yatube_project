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
            description='Тестовое описание'
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост'
        )

    # Разделил все тесты так, что бы они были отдельными для каждой модели
    def test_post_model_have_correct_object_name(self):
        """Проверяем, что у модели Post корректно работает __str__."""
        post = PostModelTest.post
        expected_post_name = post.text[:15]
        self.assertEqual(expected_post_name, str(post))

    def test_group_model_have_correct_object_name(self):
        """Проверяем, что у модели Group корректно работает __str__."""
        group = PostModelTest.group
        expected_group_name = group.title
        self.assertEqual(expected_group_name, str(group))

    def test_post_model_verbose_name(self):
        """Проверяем наличие корректных verbose_name для модели Post."""
        post = PostModelTest.post
        field_verboses_post = {
            'text': 'Текст поста',
            'created': 'Дата создания',
            'author': 'Автор',
            'group': 'Группа'
        }
        for value, expected in field_verboses_post.items():
            with self.subTest(value=value):
                self.assertEqual(
                    post._meta.get_field(value).verbose_name, expected)

    def test_group_model_verbose_name(self):
        """Проверяем наличие корректных verbose_name для модели Group."""
        group = PostModelTest.group
        field_verboses_group = {
            'title': 'Название группы',
            'slug': 'Адрес для страницы группы',
            'description': 'Описание группы'
        }
        for value, expected in field_verboses_group.items():
            with self.subTest(value=value):
                self.assertEqual(
                    group._meta.get_field(value).verbose_name, expected)

    def test_post_model_help_text(self):
        """Проверяем наличие корректных help_text в модели Post."""
        post = PostModelTest.post
        field_help_text_post = {
            'text': 'Напишите здесь свой пост',
            'created': 'Дата создания',
            'author': 'Автор поста',
            'group': 'Выберите группу для поста'
        }
        for value, expected in field_help_text_post.items():
            with self.subTest(value=value):
                self.assertEqual(
                    post._meta.get_field(value).help_text, expected)

    def test_group_model_help_text(self):
        """Проверяем наличие корректных help_text в модели Group."""
        group = PostModelTest.group
        field_help_text_group = {
            'title': 'Дайте название для группы',
            'slug': 'Укажите адрес для страницы группы',
            'description': 'Дайте описание группы'
        }
        for value, expected in field_help_text_group.items():
            with self.subTest(value=value):
                self.assertEqual(
                    group._meta.get_field(value).help_text, expected)
