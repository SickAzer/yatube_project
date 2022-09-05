from django.db import models
from django.contrib.auth import get_user_model
from django.urls import reverse

from core.models import CreatedModel

User = get_user_model()


class Post(CreatedModel):
    title = models.CharField(
        'Заголовок поста',
        max_length = 140,
        help_text='Напишите здесь заголовок поста'
    )
    text = models.TextField(
        'Текст поста',
        help_text='Напишите здесь свой пост'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='posts',
        verbose_name='Автор',
        help_text='Автор поста'
    )
    group = models.ForeignKey(
        'Group',
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='posts',
        verbose_name='Группа',
        help_text='Выберите группу для поста'
    )
    image = models.ImageField(
        'Картинка',
        upload_to='posts/',
        blank=True
    )
    liked = models.ManyToManyField(
        User,
        related_name='likes',
        default=None,
        blank=True,
        help_text='Пользователи, лайкнувшие пост'
    )
    like_count = models.BigIntegerField(
        'Количество лайков',
        default='0',
        help_text='Счетчик лайков'
        )


    class Meta:
        ordering = ['-created']
        verbose_name = 'Пост'
        verbose_name_plural = 'Посты'

    def __str__(self):
        return self.title[:15]
    
    def get_absolute_url(self):
        return reverse('posts:post_detail', args=[self.pk])
    
    # def num_likes(self):
    #     return self.liked.all().count()
    
    # def comments_count(self):
    #     return self.comments.select_related('author').count()
    
    def groups_all(self):
        return self.group_set.select_related('creator')


class Group(CreatedModel):
    title = models.CharField(
        'Название группы',
        max_length=140,
        unique=True,
        help_text='Дайте название для группы'
    )
    slug = models.SlugField(
        'Адрес для страницы группы',
        unique=True,
        help_text='Укажите адрес для страницы группы'
    )
    description = models.TextField(
        'Описание группы',
        blank=True,
        null=True,
        help_text='Дайте описание группы'
    )
    creator = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='created_groups',
        verbose_name='Создатель',
        help_text='Создатель группы'
    )

    class Meta:
        ordering = ['-created']
        verbose_name = 'Группа'
        verbose_name_plural = 'Группы'

    def __str__(self):
        return self.title
    
    def get_absolute_url(self):
        return reverse('posts:group_list', args=[self.slug])
    

class Comment(CreatedModel):
    post = models.ForeignKey(
        'Post',
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Пост',
        help_text='Добавьте комментарий к посту'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Автор',
        help_text='Автор комментария'
    )
    text = models.TextField(
        'Текст комментарий',
        help_text='Напишите здесь свой комментарий'
    )

    class Meta:
        ordering = ['-created']
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'

    def __str__(self):
        return self.text[:15]


class Follow(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='follower',
        verbose_name='Подписчик',
        help_text='Подписчик автора'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='following',
        verbose_name='Автор',
        help_text='Автор, на которого подписались'
    )

    class Meta:
        constraints = [
            # Ограничиваем подписку на себя
            models.CheckConstraint(
                check=~models.Q(user=models.F('author')),
                name='user_not_follows_self'
            ),
            # Ограничиваем создание дублирующих подписок
            models.UniqueConstraint(
                fields=['user', 'author'],
                name='unique_follow'
            )
        ]
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'

    def __str__(self):
        return f'{self.user.username} подписан на {self.author.username}'

LIKE_CHOICES = (
    ('Like', 'Like'),
    ('Unlike', 'Unlike'),
)

class Like(models.Model): 
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    value = models.CharField(choices=LIKE_CHOICES, max_length=8)
    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f'{self.user}-{self.post}-{self.value}'