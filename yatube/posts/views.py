from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required

from core.paginator.my_paginator import paginate
from .models import Post, Group, User
from .forms import PostForm


# Главная страница с недавно опубликованными постами
def index(request):
    posts = Post.objects.select_related('author', 'group').all()

    # Создана отдельня функция с paginator'ом, помещена в core
    page_obj = paginate(request, posts)
    context = {
        'page_obj': page_obj,
    }
    return render(request, 'posts/index.html', context)


# Страница с постами группы
def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    posts = group.posts.all()
    page_obj = paginate(request, posts)
    context = {
        'group': group,
        'page_obj': page_obj,
    }
    return render(request, 'posts/group_list.html', context)


# Профиль автора с его постами
def profile(request, username):
    author = get_object_or_404(User, username=username)
    posts = author.posts.all()
    page_obj = paginate(request, posts)
    context = {
        'author': author,
        'page_obj': page_obj
    }
    return render(request, 'posts/profile.html', context)


# Вывод подробной информации о посте
def post_detail(request, post_id):
    # Здесь больше будет уместна get_object_or_404
    post = get_object_or_404(Post, pk=post_id)
    posts_count = post.author.posts.count()
    is_author = False
    if post.author == request.user:
        is_author = True
    context = {
        'post': post,
        'posts_count': posts_count,
        'is_author': is_author
    }
    return render(request, 'posts/post_detail.html', context)


# Страница создания поста
@login_required
def post_create(request):
    is_edit = False
    groups = Group.objects.all()
    form = PostForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        new_post = form.save(commit=False)
        new_post.author = request.user
        new_post.save()
        return redirect('posts:profile', username=request.user)
    context = {
        'form': form,
        'groups': groups,
        'is_edit': is_edit
    }
    return render(request, 'posts/create_post.html', context)


# Страница редактирования поста
@login_required
def post_edit(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    is_edit = True
    if post.author != request.user:
        return redirect('posts:post_detail', post_id=post_id)
    groups = Group.objects.all()
    # Добавил instance в форму при редактировании
    form = PostForm(request.POST or None, instance=post)
    if request.method == 'POST' and form.is_valid():
        post.text = form.cleaned_data['text']
        post.group = form.cleaned_data['group']
        post.save(update_fields=['text', 'group'])
        return redirect('posts:post_detail', post_id=post_id)
    context = {
        'form': form,
        'post': post,
        'groups': groups,
        'is_edit': is_edit
    }
    return render(request, 'posts/create_post.html', context)
