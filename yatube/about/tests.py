from django.test import TestCase, Client
from django.urls import reverse
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