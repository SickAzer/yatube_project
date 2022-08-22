import shutil
import tempfile

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from posts.models import Post, Group, Comment

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)

User = get_user_model()

@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostsFormsTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='author')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Описание группы'
        )
        cls.post = Post.objects.create(
            text='Тестовый пост',
            author=cls.user,
            group=cls.group
        )
        
        
    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_create_post(self):
        """
        Валидная форма создает корректную запись в Post
        с перенаправлением в профиль автора.
        """
        posts_count = Post.objects.count()
        pic = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        uploaded = SimpleUploadedFile(
            name='new.gif',
            content=pic,
            content_type='image/gif'
        )
        form_data = {
            'text': 'Новый пост',
            'group': PostsFormsTests.group.pk,
            'image': uploaded
        }
        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        self.assertRedirects(
            response,
            reverse(
                'posts:profile',
                kwargs={'username': PostsFormsTests.user.username}
            )
        )
        # Убеждаемся, что созданный пост действительно последний в БД
        post = Post.objects.latest('created')
        self.assertEqual(Post.objects.count(), posts_count + 1)
        self.assertEqual(post.text, form_data['text'])
        self.assertEqual(post.author, PostsFormsTests.user)
        self.assertEqual(post.group, PostsFormsTests.group)
        self.assertEqual(post.image, 'posts/new.gif')

    def test_post_edit(self):
        """
        Валидная форма позволяет редактировать запись в Post
        с перенаправлением на детали поста.
        """
        pic = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        uploaded = SimpleUploadedFile(
            name='pic.gif',
            content=pic,
            content_type='image/gif'
        )
        form_data = {
            'text': 'Отредактированный пост',
            'group': PostsFormsTests.group.pk,
            'image': uploaded
        }
        response = self.authorized_client.post(
            reverse(
                'posts:post_edit',
                kwargs={'post_id': PostsFormsTests.post.pk}
            ),
            data=form_data,
            follow=True
        )
        post = Post.objects.get(pk=PostsFormsTests.post.pk)
        self.assertRedirects(
            response,
            reverse(
                'posts:post_detail',
                kwargs={'post_id': PostsFormsTests.post.pk}
            )
        )
        self.assertEqual(post.text, form_data['text'])
        self.assertEqual(post.author, PostsFormsTests.user)
        self.assertEqual(post.group, PostsFormsTests.group)
        self.assertEqual(post.image, 'posts/pic.gif')

    def test_add_comment(self):
        """
        Валидная форма создает комментарий
        с перенаправлением на страницу поста.
        """
        comment_count = Comment.objects.count()
        form_data = {
            'text': 'ПЕРВЫЙ!'
        }
        response = self.authorized_client.post(
                reverse(
                    'posts:add_comment',
                    kwargs={'post_id': PostsFormsTests.post.pk}
                ),
                data=form_data,
                follow=True
            )
        comment = Comment.objects.latest('created')
        self.assertRedirects(
                response,
                reverse(
                    'posts:post_detail',
                    kwargs={'post_id': PostsFormsTests.post.pk}
        ))
        self.assertEqual(Comment.objects.count(), comment_count + 1)
        self.assertEqual(comment.text, form_data['text'])
        self.assertEqual(comment.post, PostsFormsTests.post)
        self.assertEqual(comment.author, PostsFormsTests.user)
    
    def test_add_comment_not_availible_for_not_authorized(self):
        comment_count = Comment.objects.count()
        form_data = {
            'text': 'ПЕРВЫЙ!'
        }
        response = self.guest_client.post(
                reverse(
                    'posts:add_comment',
                    kwargs={'post_id': PostsFormsTests.post.pk}
                ),
                data=form_data,
                follow=True
            )
        self.assertEqual(Comment.objects.count(), comment_count)