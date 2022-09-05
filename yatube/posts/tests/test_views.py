import shutil
import tempfile

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse
from django import forms

from posts.models import Post, Group, Comment, Follow

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)
User = get_user_model()


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostsViewsTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='some_user')
        cls.author = User.objects.create_user(username='some_author')
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
        uploaded = SimpleUploadedFile(
            name='pic.gif',
            content=(
                b'\x47\x49\x46\x38\x39\x61\x02\x00'
                b'\x01\x00\x80\x00\x00\x00\x00\x00'
                b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
                b'\x00\x00\x00\x2C\x00\x00\x00\x00'
                b'\x02\x00\x01\x00\x00\x02\x02\x0C'
                b'\x0A\x00\x3B'
            ),
            content_type='image/gif'
        )
        cls.post = Post.objects.create(
            text='Тестовый пост',
            author=cls.user,
            group=cls.group,
            image=uploaded
        )
        cls.comment = Comment.objects.create(
            post=cls.post,
            author=cls.user,
            text='Тестовый комментарий'
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(PostsViewsTests.user)
        

    def test_pages_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_page_names = {
            reverse('posts:index'): 'posts/index.html',
            reverse(
                'posts:group_list',
                kwargs={'slug': PostsViewsTests.group.slug}
            ):
                'posts/group_list.html',
            reverse(
                'posts:profile',
                kwargs={'username': PostsViewsTests.user.username}
            ):
                'posts/profile.html',
            reverse(
                'posts:post_detail',
                kwargs={'post_id': PostsViewsTests.post.pk}
            ):
                'posts/post_detail.html',
            reverse('posts:post_create'): 'posts/create_post.html',
            reverse(
                'posts:post_edit',
                kwargs={'post_id': PostsViewsTests.post.pk}
            ):
                'posts/create_post.html',
            reverse('posts:follow_index'): 'posts/follow.html',
            '/nonexist-page/': 'core/404.html'
        }
        for reverse_name, template in templates_page_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_pages_show_correct_context(self):
        """
        Шаблоны index, group_list и profile сформированы
        с правильным контекстом.
        """
        page_kwargs = {
            'posts:index': {},
            'posts:group_list': {'slug': PostsViewsTests.group.slug},
            'posts:profile': {'username': PostsViewsTests.user.username}
        }
        for page, kwargs in page_kwargs.items():
            with self.subTest(page=page):
                response = self.authorized_client.get(
                    reverse(page, kwargs=kwargs)
                )
                first_object = response.context['page_obj'].object_list[0]
                self.assertEqual(first_object.text, PostsViewsTests.post.text)
                self.assertEqual(
                    first_object.author.username,
                    PostsViewsTests.user.username
                )
                self.assertEqual(
                    first_object.group.title,
                    PostsViewsTests.group.title
                )
                self.assertEqual(
                    first_object.image,
                    PostsViewsTests.post.image
                )

    def test_post_not_show_in_incorrect_group_list(self):
        """Пост с назначенной группой не появляется в списке другой группы"""
        response = self.authorized_client.get(reverse(
            'posts:group_list',
            kwargs={'slug': PostsViewsTests.second_group.slug}
        ))
        # Проверяем, что страница второй группы пуста
        # и созданный в классе пост отсутствует
        self.assertEqual(len(response.context['page_obj']), 0)

    def test_post_not_show_in_incorrect_profile(self):
        """Пост автора группой не появляется в профиле другого автора"""
        response = self.authorized_client.get(reverse(
            'posts:profile',
            kwargs={'username': PostsViewsTests.author.username}
        ))
        # Проверяем, что профиль второго автора пуст
        # и созданный в классе пост отсутствует
        self.assertEqual(len(response.context['page_obj']), 0)

    def test_post_detail_show_correct_context_filtered_by_id(self):
        """Шаблон post_detail сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse(
            'posts:post_detail',
            kwargs={'post_id': PostsViewsTests.post.pk}
        ))
        detailed_post = response.context['post']
        self.assertEqual(detailed_post.pk, PostsViewsTests.post.pk)
        self.assertEqual(detailed_post.text, PostsViewsTests.post.text)
        self.assertEqual(
            detailed_post.author.username,
            PostsViewsTests.user.username
        )
        self.assertEqual(
            detailed_post.group.title,
            PostsViewsTests.group.title
        )
        self.assertEqual(detailed_post.image, PostsViewsTests.post.image)

    def test_create_post_show_correct_context(self):
        """Шаблон post_create сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse('posts:post_create'))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
            'image': forms.fields.ImageField
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context['form'].fields[value]
                self.assertIsInstance(form_field, expected)

    def test_post_edit_show_correct_context(self):
        """Шаблон post_edit сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse(
            'posts:post_edit',
            kwargs={'post_id': PostsViewsTests.post.pk}
        ))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
            'image': forms.fields.ImageField
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context['form'].fields[value]
                self.assertIsInstance(form_field, expected)

    def test_index_page_cache(self):
        """Тестирование кэширования страницы index."""
        new_post = Post.objects.create(
            text='Testing cache',
            author=PostsViewsTests.user,
            group=PostsViewsTests.group
        )
        response_before = self.authorized_client.get(
            reverse('posts:index')
        )
        new_post.delete()
        response_after = self.authorized_client.get(
            reverse('posts:index')
        )
        self.assertEqual(
            response_before.content,
            response_after.content
        )
        cache.clear()
        response_no_cache = self.authorized_client.get(
            reverse('posts:index')
        )
        self.assertNotEqual(
            response_after.content,
            response_no_cache.content
        )

    def test_authorized_user_can_follow_and_unfollow(self):
        '''
        Авторизованный пользователь может подписываться
        и отписываться от авторов
        '''
        follow_count = Follow.objects.count()
        self.authorized_client.get(reverse(
            'posts:profile_follow',
            kwargs={'username': PostsViewsTests.author.username}
        ))
        follow = Follow.objects.last()
        self.assertEqual(Follow.objects.count(), follow_count + 1)
        self.assertEqual(follow.user, PostsViewsTests.user)
        self.assertEqual(follow.author, PostsViewsTests.author)
        self.authorized_client.get(reverse(
            'posts:profile_unfollow',
            kwargs={'username': PostsViewsTests.author.username}
        ))
        self.assertEqual(Follow.objects.count(), follow_count)
        self.assertNotEqual(Follow.objects.last(), follow)

    def test_post_shows_only_to_followers_follow_index(self):
        '''
        Посты появляются на странице избранных авторов
        у подписанных на этих авторов пользователей
        '''
        new_user = User.objects.create_user(username='new_user')
        authorized_client = Client()
        authorized_client.force_login(new_user)
        authorized_client.get(reverse(
            'posts:profile_follow',
            kwargs={'username': PostsViewsTests.user.username}
        ))
        response_follow = authorized_client.get(
            reverse('posts:follow_index')
        )
        # Проверяем, что пост появился с корректным содержимым
        first_object = response_follow.context['page_obj'].object_list[0]
        self.assertEqual(first_object.text, PostsViewsTests.post.text)
        self.assertEqual(
            first_object.author.username,
            PostsViewsTests.user.username
        )
        self.assertEqual(
            first_object.group.title,
            PostsViewsTests.group.title
        )
        self.assertEqual(
            first_object.image,
            PostsViewsTests.post.image
        )
        authorized_client.get(reverse(
            'posts:profile_unfollow',
            kwargs={'username': PostsViewsTests.user.username}
        ))
        response_unfollow = authorized_client.get(
            reverse('posts:follow_index')
        )
        # Проверяем, что пост отсутствует после отписки
        self.assertEqual(len(response_unfollow.context['page_obj']), 0)
