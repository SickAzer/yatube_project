from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db.models import Count
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect
from django.views.generic.edit import FormMixin
from django.views.generic import View, ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse


# from core.paginator.my_paginator import paginate
from .models import Post, Group, User, Follow, Comment, Like
from .forms import PostForm, CommentForm, GroupForm


class IndexListView(ListView):
    '''Главная страница с недавно опубликованными постами'''
    template_name ='posts/index.html'
    paginate_by = 10
    queryset = Post.objects.annotate(comments_count=Count('comments'), num_likes=Count('liked')).select_related('author', 'group')
  
    # Function view version    
    # def index(request):
    #     '''Главная страница с недавно опубликованными постами'''
    #     posts = Post.objects.select_related('author', 'group').all()
    #     # Создана отдельня функция с paginator'ом, помещена в core
    #     page_obj = paginate(request, posts)
    #     return render(request, 'posts/index.html', {'page_obj': page_obj})

class GroupListView(IndexListView):
    '''Страница с постами группы'''
    template_name = 'posts/group_list.html'
    
    def get_queryset(self):
        self.group = get_object_or_404(Group, slug=self.kwargs['slug'])
        return self.group.posts.annotate(comments_count=Count('comments'), num_likes=Count('liked')).select_related('author')
        
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['group'] = self.group
        return context
        
    # Function view version 
    # def group_posts(request, slug):
    #     '''Страница с постами группы'''
    #     group = get_object_or_404(Group, slug=slug)
    #     posts = group.posts.select_related('author').all()
    #     page_obj = paginate(request, posts)
    #     context = {
    #         'group': group,
    #         'page_obj': page_obj,
    #     }
    #     return render(request, 'posts/group_list.html', context)

class ProfileListView(IndexListView):
    '''Профиль автора с его постами'''
    template_name = 'posts/profile.html'
    
    def get_queryset(self):
        self.author = get_object_or_404(User, username=self.kwargs['username'])
        return self.author.posts.annotate(comments_count=Count('comments'), num_likes=Count('liked')).select_related('group')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        following = (self.request.user.is_authenticated
            and self.request.user.follower.filter(author=self.author).exists())
        context['author'], context['following'] = self.author, following
        return context
    
    # Function view version
    # def profile(request, username):
    #     '''Профиль автора с его постами'''
    #     author = get_object_or_404(User, username=username)
    #     posts = author.posts.select_related('group').all()
    #     page_obj = paginate(request, posts)
    #     following = False
    #     if request.user.is_authenticated:
    #         following = request.user.follower.filter(author=author).exists()
    #     context = {
    #         'author': author,
    #         'page_obj': page_obj,
    #         'following': following
    #     }
    #     return render(request, 'posts/profile.html', context)


class PostDetailView(DetailView, FormMixin):
    '''Вывод подробной информации о посте'''
    template_name = 'posts/post_detail.html'
    form_class = CommentForm
    def get_object(self):
        post = get_object_or_404(Post.objects.annotate(num_likes=Count('liked')), pk=self.kwargs['post_id'])
        return post
        
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['comments'] = self.get_object().comments.select_related('author').all()
        return context
    

    # Function view version
    # def post_detail(request, post_id):
    #     '''Вывод подробной информации о посте'''
    #     post = get_object_or_404(Post, pk=post_id)
    #     comments = post.comments.select_related('author').all()
    #     form = CommentForm()
    #     context = {
    #         'post': post,
    #         'comments': comments,
    #         'form': form
    #     }
    #     return render(request, 'posts/post_detail.html', context)

# @method_decorator(login_required, name='dispatch')
class PostCreateView(LoginRequiredMixin, CreateView):
    '''Страница создания поста'''
    template_name = 'posts/create_post.html'
    model = Post
    form_class = PostForm
    
    def form_valid(self, form):
        self.post = form.save(commit=False)
        self.post.author = self.request.user
        self.post.save()
        return super().form_valid(form)

    # Function view version
    # @login_required
    # def post_create(request):
    #     '''Страница создания поста'''
    #     form = PostForm(request.POST or None, files=request.FILES or None)
    #     if request.method == 'POST' and form.is_valid():
    #         post = form.save(commit=False)
    #         post.author = request.user
    #         post.save()
    #         return redirect('posts:profile', username=request.user)
    #     return render(request, 'posts/create_post.html', {'form': form})


class PostUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    '''Страница редактирования поста'''
    template_name = 'posts/create_post.html'
    model = Post
    form_class = PostForm
    pk_url_kwarg = 'post_id'
    
    def test_func(self):
        obj = self.get_object()
        return obj.author == self.request.user
        
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        if hasattr(self, 'object'):
            kwargs.update({'instance': self.object})
        return kwargs   

    # Function view version    
    # @login_required
    # def post_edit(request, post_id):
    #     '''Страница редактирования поста'''
    #     post = get_object_or_404(Post, pk=post_id)
    #     form = PostForm(
    #         request.POST or None,
    #         files=request.FILES or None,
    #         instance=post
    #     )
    #     if request.method == 'POST' and form.is_valid():
    #         form.save()
    #         return redirect('posts:post_detail', post_id=post_id)
    #     return render(request, 'posts/create_post.html', {'form': form})


class PostDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    '''Страница удаления поста'''
    model = Post
    pk_url_kwarg = 'post_id'
    
    def test_func(self):
        obj = self.get_object()
        return obj.author == self.request.user
    
    def get_success_url(self):
        return reverse('posts:profile', kwargs={'username': self.request.user.username})

    # Function view version 
    # @login_required
    # def post_delete(request, post_id):
    #     '''Удаление поста'''
    #     post = get_object_or_404(Post, pk=post_id)
    #     if post.author != request.user:
    #         return redirect('posts:post_detail', post_id=post_id)
    #     post.delete()
    #     return redirect('posts:profile', username=request.user)


class CommentCreateView(LoginRequiredMixin, CreateView):
    '''Добавление комментариев на странице поста'''
    template_name = 'posts/post_detail.html'
    model = Comment
    form_class = CommentForm
    
    def form_valid(self, form):
        self.comment = form.save(commit=False)
        self.comment.author = self.request.user
        self.comment.post = get_object_or_404(Post, pk=self.kwargs['post_id'])
        self.comment.save()
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse('posts:post_detail', kwargs={'post_id': self.kwargs['post_id']})
    

    # Function view version  
    # @login_required
    # def add_comment(request, post_id):
    #     '''Добавление комментариев на странице поста'''
    #     form = CommentForm(request.POST or None)
    #     if form.is_valid():
    #         comment = form.save(commit=False)
    #         comment.author = request.user
    #         comment.post = get_object_or_404(Post, pk=post_id)
    #         comment.save()
    #     return redirect('posts:post_detail', post_id=post_id)


class CommentDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    '''Удаление комментария'''
    model = Comment
    form_class = CommentForm
    pk_url_kwarg = 'comment_id'
    
    def test_func(self):
        obj = self.get_object()
        return obj.author == self.request.user
    
    def get_success_url(self):
        return reverse('posts:post_detail', kwargs={'post_id': self.kwargs['post_id']})


    # Function view version 
    # @login_required
    # def delete_comment(request, post_id, comment_id):
    #     '''Удаление комментария'''
    #     comment = get_object_or_404(Comment, pk=comment_id)
    #     if comment.author != request.user:
    #         return redirect('posts:post_detail', post_id=post_id)
    #     comment.delete()
    #     return redirect('posts:post_detail', post_id=post_id)


class FollowIndexListView(LoginRequiredMixin, IndexListView):
    '''Страница с постами авторов, на которых подписан пользователь'''
    template_name ='posts/follow.html'
    def get_queryset(self):
        queryset = (Post.objects.annotate(comments_count=Count('comments'), num_likes=Count('liked')).select_related('author', 'group')
                .filter(author__following__user=self.request.user))
        return queryset
    
    # Function view version
    # @login_required
    # def follow_index(request):
    #     '''Страница с постами авторов, на которых подписан пользователь'''
    #     posts = (Post.objects.select_related('author', 'group')
    #              .filter(author__following__user=request.user))
    #     page_obj = paginate(request, posts)
    #     return render(request, 'posts/follow.html', {'page_obj': page_obj})


class FollowCreateView(LoginRequiredMixin, View):
    '''Подписка на автора в его профиле'''
    def get(self, *args, **kwargs):
        author = get_object_or_404(User, username=self.kwargs['username'])
        following = self.request.user.follower.filter(author=author).exists()
        if self.request.user != author and not following:
            follow = Follow(user=self.request.user, author=author)
            follow.save()
        return redirect('posts:profile', username=author.username)
    
    
    # Function view version
    # @login_required
    # def profile_follow(request, username):
    #     '''Подписка на автора в его профиле'''
    #     author = get_object_or_404(User, username=username)
    #     following = request.user.follower.filter(author=author).exists()
    #     if request.user != author and not following:
    #         follow = Follow(user=request.user, author=author)
    #         follow.save()
    #     return redirect('posts:profile', username=username)


class FollowDeleteView(LoginRequiredMixin, View):
    '''Отписка от автора в его профиле'''
    def get(self, *args, **kwargs):
        author = get_object_or_404(User, username=self.kwargs['username'])
        following = self.request.user.follower.filter(author=author).exists()
        if following:
            follow = self.request.user.follower.filter(author=author)
            follow.delete()
        return redirect('posts:profile', username=author.username)
    
    
    # Function view version
    # @login_required
    # def profile_unfollow(request, username):
    #     '''Отписка от автора в его профиле'''
    #     author = get_object_or_404(User, username=username)
    #     following = request.user.follower.filter(author=author).exists()
    #     if following:
    #         follow = request.user.follower.filter(author=author)
    #         follow.delete()
    #     return redirect('posts:profile', username=username)


class GroupCreateView(LoginRequiredMixin, CreateView):
    '''Страница создания группы'''
    template_name = 'posts/group_create.html'
    model = Group
    form_class = GroupForm
    
    def form_valid(self, form):
        self.group = form.save(commit=False)
        self.group.creator = self.request.user
        self.group.save()
        return super().form_valid(form)

# Function view version
# @login_required
# def group_create(request):
#     '''Страница создания группы'''
#     form = GroupForm(request.POST or None)
#     if request.method == 'POST' and form.is_valid():
#         group = form.save(commit=False)
#         group.creator = request.user
#         group.save()
#         return redirect('posts:group_list', slug=group.slug)
#     return render(request, 'posts/group_create.html', {'form': form})

class GroupDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    '''Страница удаления группы'''
    model = Group
    
    def test_func(self):
        obj = self.get_object()
        return obj.creator != self.request.user
    
    def get_success_url(self):
        return reverse('posts:profile', kwargs={'username': self.request.user.username})

@login_required
def like_unlike_post(request):
    '''Создание и удаление лайка поста'''
    user = request.user
    if request.method == 'POST':
        post_id = request.POST.get('post_id')
        post_obj = Post.objects.get(id=post_id)
        if user in post_obj.liked.all():
            post_obj.liked.remove(user)
        else:
            post_obj.liked.add(user)
        like, created = Like.objects.get_or_create(user=user, post_id=post_id)
        if not created:
            if like.value=='Like':
                like.value='Unlike'
            else:
                like.value='Like'
        else:
            like.value='Like'

            post_obj.save()
            like.save()
        data = {
            'value': like.value,
            'likes': post_obj.liked.all().count()
        }
        return JsonResponse(data, safe=False)
    return redirect('posts:index')
        