from django.core.cache import cache
from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from django.urls import reverse
from http import HTTPStatus

from posts.models import Post, Group, Follow

User = get_user_model()


class PostsURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='user')
        cls.author = User.objects.create_user(username='author')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост',
        )
        cls.follow = Follow.objects.create(
            user=cls.user,
            author=cls.author
        )

    def setUp(self):
        # Создаем неавторизованный клиент
        self.guest_client = Client()
        # Создаем второй клиент и авторизуем его
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        # Создаем дополнительный клиент и авторизуем его
        self.another_authorized_client = Client()
        self.another_authorized_client.force_login(self.author)

    def test_urls_exists_at_desired_location_anonymous(self):
        """Страницы c публичным доступом доступны любому пользователю."""
        urls = (
            reverse('posts:index'),
            reverse(
                'posts:group_list',
                kwargs={'slug': PostsURLTests.group.slug}
            ),
            reverse(
                'posts:profile',
                kwargs={'username': PostsURLTests.user.username}
            ),
            reverse(
                'posts:post_detail',
                kwargs={'post_id': PostsURLTests.post.pk}
            )
        )
        for url in urls:
            with self.subTest(url=url):
                response = self.guest_client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_urls_exists_at_desired_location_authorized(self):
        """Страницы доступны авторизованному пользователю."""
        urls = (
            reverse('posts:post_create'),
            reverse(
                'posts:post_edit',
                kwargs={'post_id': PostsURLTests.post.pk}
            ),
            reverse('posts:follow_index')
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
            reverse('posts:post_create'),
            reverse(
                'posts:post_edit',
                kwargs={'post_id': PostsURLTests.post.pk}
            ),
            reverse('posts:follow_index')
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
            reverse(
                'posts:post_edit',
                kwargs={'post_id': PostsURLTests.post.pk}
            ),
            follow=True
        )
        self.assertRedirects(
            response,
            reverse(
                'posts:profile',
                kwargs={'username': PostsURLTests.author.username}
            )
        )

    def test_urls_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        url_names_templates = {
            reverse('posts:index'): 'posts/index.html',
            reverse(
                'posts:group_list',
                kwargs={'slug': PostsURLTests.group.slug}
            ): 'posts/group_list.html',
            reverse(
                'posts:profile',
                kwargs={'username': PostsURLTests.user.username}
            ): 'posts/profile.html',
            reverse(
                'posts:post_detail',
                kwargs={'post_id': PostsURLTests.post.pk}
            ): 'posts/post_detail.html',
            reverse('posts:post_create'): 'posts/create_post.html',
            reverse(
                'posts:post_edit',
                kwargs={'post_id': PostsURLTests.post.pk}
            ): 'posts/create_post.html',
            reverse('posts:follow_index'): 'posts/follow.html'
        }
        for address, template in url_names_templates.items():
            with self.subTest(address=address):
                response = self.authorized_client.get(address)
                self.assertTemplateUsed(response, template)

    def test_unexisting_page_url_returns_404(self):
        """Несуществующая страница возвращает ошибку 404."""
        response = self.guest_client.get('/unexisting_page/')
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
