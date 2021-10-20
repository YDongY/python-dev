from django.db import models
from django.contrib.auth.models import User
from django.shortcuts import reverse
from slugify import slugify


class Post(models.Model):
    STATUS_CHOICES = (
        ('draft', '草稿'),
        ('published', '已发布')
    )
    title = models.CharField(max_length=100, verbose_name='标题')
    content = models.TextField(verbose_name='内容')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='draft')
    slug = models.SlugField(max_length=200, blank=True, unique=True, verbose_name='URL 标记')
    author = models.ForeignKey(to=User, on_delete=models.CASCADE, verbose_name='作者')
    create_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        self.slug = slugify(self.slug)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('posts:rest-post-detail', kwargs={'pk': self.id})


class Tag(models.Model):
    name = models.CharField(max_length=100, verbose_name='名称')
    posts = models.ManyToManyField(to=Post)

    def __str__(self):
        return self.name
