from django.test import TestCase, Client
from django.urls import reverse
from http import HTTPStatus


# Тестируем URLs для страниц about
class AboutURLTests(TestCase):
    def setUp(self):
        # Создаем неавторизованный клиент
        self.guest_client = Client()

    def test_urls_exist_at_desired_location(self):
        """Страницы author и tech доступны любому пользователю."""
        urls = (
            '/about/author/',
            '/about/tech/'
        )
        for url in urls:
            with self.subTest(url=url):
                response = self.guest_client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_urls_use_correct_template(self):
        """Страницы author и tech используют соответствующий шаблон."""
        url_names_templates = {
            '/about/author/': 'about/author.html',
            '/about/tech/': 'about/tech.html'
        }
        for address, template in url_names_templates.items():
            with self.subTest(address=address):
                response = self.guest_client.get(address)
                self.assertTemplateUsed(response, template)


# Тестируем Views для страниц about
class AboutViewsTests(TestCase):
    def setUp(self):
        self.guest_client = Client()

    def test_pages_uses_correct_template(self):
        templates_page_names = {
            'about:author': 'about/author.html',
            'about:tech': 'about/tech.html'
        }
        for name, template in templates_page_names.items():
            with self.subTest(name=name):
                response = self.guest_client.get(reverse(name))
                self.assertTemplateUsed(response, template)
