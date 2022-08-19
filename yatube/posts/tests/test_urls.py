from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from http import HTTPStatus

from posts.models import Post, Group

User = get_user_model()


class PostsURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='author')
        cls.another_user = User.objects.create_user(username='not_author')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост',
        )

    def setUp(self):
        # Создаем неавторизованный клиент
        self.guest_client = Client()
        # Создаем второй клиент и авторизуем его
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        # Создаем дополнительный клиент и авторизуем его
        self.another_authorized_client = Client()
        self.another_authorized_client.force_login(self.another_user)

    def test_urls_exists_at_desired_location_anonymous(self):
        """Страницы c публичным доступом доступны любому пользователю."""
        urls = (
            '/',
            f'/group/{PostsURLTests.group.slug}/',
            f'/profile/{PostsURLTests.user.username}/',
            f'/posts/{PostsURLTests.post.pk}/'
        )
        for url in urls:
            with self.subTest(url=url):
                response = self.guest_client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_urls_exists_at_desired_location_authorized(self):
        """Страницы доступны авторизованному пользователю."""
        urls = (
            '/create/',
            f'/posts/{PostsURLTests.post.pk}/edit/'
        )
        for url in urls:
            with self.subTest(url=url):
                response = self.authorized_client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_urls_redirect_on_login_anonymous(self):
        """
        Страницы перенаправляют неавторизованного пользователя для логина.
        """
        urls = (
            '/create/',
            f'/posts/{PostsURLTests.post.pk}/edit/'
        )
        for url in urls:
            with self.subTest(url=url):
                response = self.guest_client.get(url, follow=True)
                self.assertRedirects(response, '/auth/login/?next=' + url)

    def test_post_edit_url_redirect_on_post_detail_not_author(self):
        """
        Страница перенаправляет на профиль пользователя,
        если авторизованный пользователь не является автором поста.
        """
        response = self.another_authorized_client.get(
            f'/posts/{PostsURLTests.post.pk}/edit/',
            follow=True
        )
        self.assertRedirects(response, '/profile/not_author/')

    def test_urls_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        url_names_templates = {
            '/': 'posts/index.html',
            f'/group/{PostsURLTests.group.slug}/': 'posts/group_list.html',
            f'/profile/{PostsURLTests.user.username}/': 'posts/profile.html',
            f'/posts/{PostsURLTests.post.pk}/': 'posts/post_detail.html',
            f'/posts/{PostsURLTests.post.pk}/edit/': 'posts/create_post.html',
            '/create/': 'posts/create_post.html'
        }
        for address, template in url_names_templates.items():
            with self.subTest(address=address):
                response = self.authorized_client.get(address)
                self.assertTemplateUsed(response, template)

    def test_unexisting_page_url_returns_404(self):
        """Несуществующая страница возвращает ошибку 404."""
        response = self.guest_client.get('/unexisting_page/')
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
