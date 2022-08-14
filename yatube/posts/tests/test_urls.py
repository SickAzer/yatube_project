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
            pk=0,
            author=cls.user,
            text='Тестовый пост',
        )
    def setUp(self):
        # Создаем неавторизованный клиент
        self.guest_client = Client()
        # Создаем второй клиент
        self.authorized_client = Client()
        # Авторизуем пользователя
        self.authorized_client.force_login(self.user)
        
        self.another_authorized_client = Client()
        
        self.another_authorized_client.force_login(self.another_user)

    def test_urls_exists_at_desired_location_anonymous(self):
        """Страницы c публичным доступом доступны любому пользователю."""
        urls = (
            '/',
            '/group/test-slug/',
            '/profile/author/',
            '/posts/0/'
        )
        for url in urls:
            with self.subTest(url=url):
                response = self.guest_client.get(url)  
                self.assertEqual(response.status_code, HTTPStatus.OK) 
    
    def test_urls_exists_at_desired_location_authorized(self):
        """Страницы доступны авторизованному пользователю."""
        urls = (
            '/create/',
            '/posts/0/edit/'
        )
        for url in urls:
            with self.subTest(url=url):    
                response = self.authorized_client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK) 
        
    def test_urls_redirect_on_login_anonymous(self):
        """Страницы перенаправляют неавторизованного пользователя для логина."""
        urls = (
            '/create/',
            '/posts/0/edit/'
        )
        for url in urls:
            with self.subTest(url=url):    
                response = self.guest_client.get(url, follow=True)
                self.assertRedirects(response, '/auth/login/?next=' + url)
    
    def test_post_edit_url_redirect_on_post_detail_not_author(self):
        """Страница перенаправляет на детали поста, если авторизованный пользователь не является автором поста"""
        response = self.another_authorized_client.get('/posts/0/edit/', follow=True)
        self.assertRedirects(response, '/posts/0/')  
    
    def test_urls_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        # Шаблоны по адресам
        url_names_templates = {
            '/': 'posts/index.html',
            '/group/test-slug/': 'posts/group_list.html',
            '/profile/author/': 'posts/profile.html',
            '/posts/0/': 'posts/post_detail.html',
            '/posts/0/edit/': 'posts/create_post.html',
            '/create/': 'posts/create_post.html'
        }
        for address, template in url_names_templates.items():
            with self.subTest(address=address):
                response = self.authorized_client.get(address)
                self.assertTemplateUsed(response, template)    
    
    def test_unexisting_page_url_returns_404(self):
        response = self.guest_client.get('/unexisting_page/')
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)