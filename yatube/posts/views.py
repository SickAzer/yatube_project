from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
# from django.views.decorators.cache import cache_page

from core.paginator.my_paginator import paginate
from .models import Post, Group, User, Comment
from .forms import PostForm, CommentForm

# @cache_page(20, key_prefix='index_page')
def index(request):
    '''Главная страница с недавно опубликованными постами'''
    posts = Post.objects.select_related('author', 'group').all()
    # Создана отдельня функция с paginator'ом, помещена в core
    page_obj = paginate(request, posts)
    return render(request, 'posts/index.html', {'page_obj': page_obj})


def group_posts(request, slug):
    '''Страница с постами группы'''
    group = get_object_or_404(Group, slug=slug)
    posts = group.posts.all()
    page_obj = paginate(request, posts)
    context = {
        'group': group,
        'page_obj': page_obj,
    }
    return render(request, 'posts/group_list.html', context)


def profile(request, username):
    '''Профиль автора с его постами'''
    author = get_object_or_404(User, username=username)
    posts = author.posts.all()
    page_obj = paginate(request, posts)
    context = {
        'author': author,
        'page_obj': page_obj
    }
    return render(request, 'posts/profile.html', context)


def post_detail(request, post_id):
    '''Вывод подробной информации о посте'''
    post = get_object_or_404(Post, pk=post_id)
    comments = post.comments.all()
    form = CommentForm()
    context = {
        'post': post,
        'comments': comments,
        'form': form
    }
    return render(request, 'posts/post_detail.html', context)


@login_required
def post_create(request):
    '''Страница создания поста'''
    form = PostForm(request.POST or None, files=request.FILES or None)
    if request.method == 'POST' and form.is_valid():
        post = form.save(commit=False)
        post.author = request.user
        post.save()
        return redirect('posts:profile', username=request.user)
    return render(request, 'posts/create_post.html', {'form': form})


@login_required
def post_edit(request, post_id):
    '''Страница редактирования поста'''
    post = get_object_or_404(Post, pk=post_id)
    if post.author != request.user:
        return redirect('posts:profile', username=request.user)
    form = PostForm(
        request.POST or None,
        files=request.FILES or None, 
        instance=post
    )
    if request.method == 'POST' and form.is_valid():
        form.save()
        return redirect('posts:post_detail', post_id=post_id)
    return render(request, 'posts/create_post.html', {'form': form})


@login_required
def add_comment(request, post_id):
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = get_object_or_404(Post, pk=post_id)
        comment.save()
    return redirect('posts:post_detail', post_id=post_id)

