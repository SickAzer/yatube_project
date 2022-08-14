from django.test import TestCase, Client
from http import HTTPStatus

class AboutURLTests(TestCase):
    def setUp(self):
        self.guest_client = Client()
        
    def test_urls_exist_at_desired_location(self):
        urls = (
            '/about/author/',
            '/about/tech/'
        )
        for url in urls:
            with self.subTest(url=url):
                response = self.guest_client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)
                
    def test_urls_use_correct_template(self):
        url_names_templates = {
            '/about/author/': 'about/author.html',
            '/about/tech/': 'about/tech.html'
        }
        for address, template in url_names_templates.items():
            with self.subTest(address=address):
                response = self.guest_client.get(address)
                self.assertTemplateUsed(response, template)