from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Post, Group, Follow

User = get_user_model()


# Тестируем Pginator
class PaginatorViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='user')
        cls.author = User.objects.create_user(username='author')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание'
        )
        cls.follow = Follow.objects.create(
            user=cls.user,
            author=cls.author
        )
        page_objects = []
        for i in range(1, 16):
            new_post = Post(
                author=cls.author,
                text='Тестовый пост ' + str(i),
                group=cls.group
            )
            page_objects.append(new_post)
        Post.objects.bulk_create(page_objects)

    def setUp(self):
        # Создаем клиент
        self.authorized_client = Client()
        # Авторизуем пользователя
        self.authorized_client.force_login(self.user)

    def test_paginator_correct_context(self):
        """Paginator сформирован с правильным контекстом."""
        paginator_pages = (
            reverse('posts:index'),
            reverse(
                'posts:group_list',
                kwargs={'slug': PaginatorViewsTest.group.slug}
            ),
            reverse(
                'posts:profile',
                kwargs={'username': PaginatorViewsTest.author.username}
            ),
            reverse('posts:follow_index')
        )
        for page in paginator_pages:
            with self.subTest(page=page):
                response_page_1 = self.authorized_client.get(page)
                response_page_2 = self.authorized_client.get(page + '?page=2')
                # На первой странице должно быть 10 постов
                self.assertEqual(
                    len(response_page_1.context['page_obj'].object_list),
                    10
                )
                # На второй странице должно быть 5 постов
                self.assertEqual(
                    len(response_page_2.context['page_obj'].object_list),
                    5
                )
