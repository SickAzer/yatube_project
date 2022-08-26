from django.test import TestCase


class ViewTestClass(TestCase):
    '''Тест на использование кастомного шаблона ошибки 404'''
    def test_error_page(self):
        response = self.client.get('/nonexist-page/')
        self.assertTemplateUsed(response, 'core/404.html')
