from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from django import forms

from posts.models import Post, Group


User = get_user_model()


class PostsViewsTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='author')
        cls.second_user = User.objects.create_user(username='not_author')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание'
        )
        cls.second_group = Group.objects.create(
            title='Тестовая группа 2',
            slug='test-slug-2',
            description='Тестовое описание 2'
        )
        cls.post = Post.objects.create(
            text='Тестовый пост',
            author=cls.user,
            group=cls.group
        )
        
    def setUp(self):
        # Создаем неавторизованный клиент
        self.guest_client = Client()
        # Создаем второй клиент
        self.authorized_client = Client()
        # Авторизуем пользователя
        self.authorized_client.force_login(self.user)
        
    def test_pages_uses_correct_template(self):
        templates_page_names = {
            'posts/index.html': reverse('posts:index'),
            'posts/group_list.html': (
                reverse('posts:group_list', kwargs={'slug': 'test-slug'})
            ),
            'posts/profile.html': (
                reverse('posts:profile', kwargs={'username': 'author'})
            ),
            'posts/post_detail.html': (
                reverse('posts:post_detail', kwargs={'post_id': '1'})
            ),
            'posts/create_post.html': reverse('posts:post_create'),
            'posts/create_post.html': (
                reverse('posts:post_edit', kwargs={'post_id': '1'})
            ),
        }
        for template, reverse_name in templates_page_names.items():
            with self.subTest(template=template):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)
                
    def test_pages_show_correct_context(self):
        page_kwargs = {
            'posts:index': {},
            'posts:group_list': {'slug': self.group.slug},
            'posts:profile': {'username': self.user.username}
        } 
        for page, kwargs in page_kwargs.items():
            with self.subTest(page=page):
                response = self.authorized_client.get(reverse(page, kwargs=kwargs))
                first_object = response.context['page_obj'].object_list[0]
                self.assertEqual(first_object.text, self.post.text)
                self.assertEqual(first_object.author.username, self.user.username)
                self.assertEqual(first_object.group.title, self.group.title)
                
    def test_post_not_show_in_incorrect_group_list(self):
        response = self.authorized_client.get(reverse('posts:group_list', kwargs={'slug': self.second_group.slug}))
        self.assertEqual(len(response.context['page_obj']), 0)
        
    def test_post_not_show_in_incorrect_profile(self):
        response = self.authorized_client.get(reverse('posts:profile', kwargs={'username': self.second_user.username}))
        self.assertEqual(len(response.context['page_obj']), 0)
        
    def test_post_detail_show_correct_context_filtered_by_id(self):
        response = self.authorized_client.get(reverse('posts:post_detail', kwargs={'post_id': self.post.pk}))
        detailed_post = response.context['post']
        self.assertEqual(detailed_post.pk, self.post.pk)
        self.assertEqual(detailed_post.text, self.post.text)
        self.assertEqual(detailed_post.author.username, self.user.username)
        self.assertEqual(detailed_post.group.title, self.group.title)
        
    def test_create_post_show_correct_context(self):
        response = self.authorized_client.get(reverse('posts:post_create'))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context['form'].fields[value]
                self.assertIsInstance(form_field, expected)
    
    def test_post_edit_show_correct_context(self):
        response = self.authorized_client.get(reverse('posts:post_edit', kwargs={'post_id': self.post.pk}))
        edit_post = response.context['post']
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context['form'].fields[value]
                self.assertIsInstance(form_field, expected)
        self.assertEqual(edit_post.pk, self.post.pk)
        
    def test_paginator_correct_context(self):
        page_objects = []
        for i in range(1, 15):
            new_post = Post(
                author=self.user,
                text='Тестовый пост ' + str(i),
                group=self.group
            )
            page_objects.append(new_post)
        Post.objects.bulk_create(page_objects)
        paginator_pages = (
            reverse('posts:index'),
            reverse(
                'posts:group_list',
                kwargs={'slug': self.group.slug}
            ),
            reverse(
                'posts:profile',
                kwargs={'username': self.user.username}
            )
        )
        for page in paginator_pages:
            with self.subTest(page=page):
                response_page_1 = self.authorized_client.get(page)
                response_page_2 = self.authorized_client.get(page + '?page=2')
                self.assertEqual(
                    len(response_page_1.context['page_obj'].object_list),
                    10
                )
                self.assertEqual(
                    len(response_page_2.context['page_obj'].object_list),
                    5
                )