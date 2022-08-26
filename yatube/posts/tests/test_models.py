from django.db import IntegrityError
from django.contrib.auth import get_user_model
from django.test import TestCase

from ..models import Group, Post, Comment, Follow

User = get_user_model()


class PostsModelTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='user')
        cls.author = User.objects.create_user(username='author')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='Тестовый слаг',
            description='Тестовое описание'
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост'
        )
        cls.comment = Comment.objects.create(
            post=cls.post,
            author=cls.user,
            text='Тестовый комментарий'
        )
        cls.follow = Follow.objects.create(
            user=cls.user,
            author=cls.author
        )

    # Разделил все тесты так, что бы они были отдельными для каждой модели
    def test_post_model_have_correct_object_name(self):
        """Проверяем, что у модели Post корректно работает __str__."""
        post = PostsModelTests.post
        expected_post_name = post.text[:15]
        self.assertEqual(expected_post_name, str(post))

    def test_group_model_have_correct_object_name(self):
        """Проверяем, что у модели Group корректно работает __str__."""
        group = PostsModelTests.group
        expected_group_name = group.title
        self.assertEqual(expected_group_name, str(group))

    def test_comment_model_have_correct_object_name(self):
        """Проверяем, что у модели Comment корректно работает __str__."""
        comment = PostsModelTests.comment
        expected_comment_name = comment.text[:15]
        self.assertEqual(expected_comment_name, str(comment))

    def test_follow_model_have_correct_object_name(self):
        """Проверяем, что у модели Follow корректно работает __str__."""
        follow = PostsModelTests.follow
        expected_follow_name = f'{follow.user} подписан на {follow.author}'
        self.assertEqual(expected_follow_name, str(follow))

    def test_post_model_verbose_name(self):
        """Проверяем наличие корректных verbose_name для модели Post."""
        post = PostsModelTests.post
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
        group = PostsModelTests.group
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
        post = PostsModelTests.post
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
        group = PostsModelTests.group
        field_help_text_group = {
            'title': 'Дайте название для группы',
            'slug': 'Укажите адрес для страницы группы',
            'description': 'Дайте описание группы'
        }
        for value, expected in field_help_text_group.items():
            with self.subTest(value=value):
                self.assertEqual(
                    group._meta.get_field(value).help_text, expected)

    def test_no_self_follow(self):
        constraint_name = 'user_not_follows_self'
        with self.assertRaisesMessage(IntegrityError, constraint_name):
            Follow.objects.create(
                user=PostsModelTests.user,
                author=PostsModelTests.user
            )

    def test_no_duplicate_follows(self):

        with self.assertRaisesMessage(
            IntegrityError,
            'UNIQUE constraint failed'
        ):
            Follow.objects.create(
                user=PostsModelTests.user,
                author=PostsModelTests.author
            )
            Follow.objects.create(
                user=PostsModelTests.user,
                author=PostsModelTests.author
            )
