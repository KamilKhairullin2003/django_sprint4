from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone

from .constants import LENGTH_TITLE, MAX_STR_LENGTH, COMMENT_LENGTH

User = get_user_model()


class PublishedPostManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().select_related(
            'category', 'location'
        ).filter(
            is_published=True,
            pub_date__lte=timezone.now(),
            category__is_published=True
        )


class PublishedModel(models.Model):
    is_published = models.BooleanField(
        default=True,
        verbose_name='Опубликовано',
        help_text='Снимите галочку, чтобы скрыть публикацию.'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Добавлено'
    )

    class Meta:
        abstract = True


class Post(PublishedModel, models.Model):
    title = models.CharField(
        max_length=LENGTH_TITLE, verbose_name='Заголовок'
    )
    text = models.TextField(verbose_name='Текст')
    pub_date = models.DateTimeField(
        verbose_name='Дата и время публикации',
        help_text=(
            'Если установить дату и время в будущем — можно делать '
            'отложенные публикации.'
        )
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор публикации'
    )
    location = models.ForeignKey(
        'Location',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='Местоположение'
    )
    category = models.ForeignKey(
        'Category',
        on_delete=models.SET_NULL,
        null=True,
        verbose_name='Категория'
    )
    image = models.ImageField('Фото', upload_to='post_images', blank=True)

    objects = models.Manager()
    published = PublishedPostManager()

    class Meta:
        ordering = ['-pub_date']
        verbose_name = 'публикация'
        verbose_name_plural = 'Публикации'
        default_related_name = 'posts'

    def __str__(self):
        if len(self.title) > MAX_STR_LENGTH:
            return self.title[:MAX_STR_LENGTH] + '...'
        return self.title


class Category(PublishedModel, models.Model):
    title = models.CharField(
        max_length=LENGTH_TITLE,
        verbose_name='Заголовок'
    )
    description = models.TextField(
        verbose_name='Описание'
    )
    slug = models.SlugField(
        max_length=LENGTH_TITLE,
        unique=True,
        verbose_name='Идентификатор',
        help_text=(
            'Идентификатор страницы для URL; разрешены символы '
            'латиницы, цифры, дефис и подчёркивание.'
        )
    )

    class Meta:
        ordering = ['title']
        verbose_name = 'категория'
        verbose_name_plural = 'Категории'

    def __str__(self):
        if len(self.title) > MAX_STR_LENGTH:
            return self.title[:MAX_STR_LENGTH] + '...'
        return self.title


class Location(PublishedModel, models.Model):
    name = models.CharField(
        max_length=LENGTH_TITLE,
        verbose_name='Название места'
    )

    class Meta:
        ordering = ['name']
        verbose_name = 'местоположение'
        verbose_name_plural = 'Местоположения'

    def __str__(self):
        if len(self.name) > MAX_STR_LENGTH:
            return self.name[:MAX_STR_LENGTH] + '...'
        return self.name


class Comment(models.Model):
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Публикация'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор'
    )
    text = models.TextField('Комментарий')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']
        verbose_name = 'комментарий'
        verbose_name_plural = 'Комментарии'

    def __str__(self):
        return self.text[:COMMENT_LENGTH]
