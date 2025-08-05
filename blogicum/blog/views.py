from django.views.generic import (
    ListView, CreateView, UpdateView, DeleteView, DetailView
)
from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth import login
from django.urls import reverse_lazy, reverse
from django.contrib import messages

from .forms import (
    PostForm, CustomUserCreationForm, CommentForm, ProfileEditForm
)
from .models import Post, Category, User, Comment
from .constants import PAGINATE_BY
from .utils import filter_published_posts


class OnlyAuthorMixin(UserPassesTestMixin):

    def test_func(self):
        obj = self.get_object()
        return self.request.user == obj.author


class OnlyCommentAuthorMixin(UserPassesTestMixin):

    def test_func(self):
        comment_id = self.kwargs.get('pk') or self.kwargs.get('comment_id')
        comment = get_object_or_404(Comment, pk=comment_id)
        return self.request.user == comment.author


class PostListView(ListView):
    model = Post
    template_name = 'blog/index.html'
    paginate_by = PAGINATE_BY

    queryset = filter_published_posts(Post.objects)


class CategoryPostView(ListView):
    model = Post
    template_name = 'blog/category.html'
    paginate_by = PAGINATE_BY

    def get_queryset(self):
        category_slug = self.kwargs['slug']
        category = get_object_or_404(
            Category,
            slug=category_slug,
            is_published=True
        )
        posts = filter_published_posts(category.category_posts.all())
        return posts

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        category_slug = self.kwargs['slug']
        context['category'] = get_object_or_404(
            Category,
            slug=category_slug,
            is_published=True
        )
        return context


class PostDetailView(LoginRequiredMixin, DetailView):
    model = Post
    template_name = 'blog/detail.html'
    pk_url_kwarg = 'post_id'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = CommentForm()
        context['comments'] = self.get_object().comments.all()
        return context

    def get_object(self, queryset=None):
        post = get_object_or_404(Post, pk=self.kwargs.get(self.pk_url_kwarg))
        if self.request.user == post.author:
            return post
        return get_object_or_404(
            filter_published_posts(Post.objects.all()),
            pk=self.kwargs.get(self.pk_url_kwarg)
        )


class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    form_class = PostForm
    template_name = 'blog/create.html'

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse(
            'blog:profile',
            kwargs={'username': self.object.author.username}
        )


class ProfileDetailView(ListView):
    model = Post
    template_name = 'blog/profile.html'
    paginate_by = PAGINATE_BY
    slug_field = 'username'
    slug_url_kwarg = 'username'
    context_object_name = 'profile'

    def get_queryset(self):
        username = self.kwargs['username']
        self.author = get_object_or_404(User, username=username)
        posts = self.author.posts.all()

        if self.request.user != self.author:
            posts = filter_published_posts(posts)
        return posts

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['profile'] = self.author
        context['post_count'] = self.author.posts.count()
        return context


class ProfileEditView(LoginRequiredMixin, UpdateView):
    form_class = ProfileEditForm
    template_name = 'blog/user.html'

    def get_object(self, queryset=None):
        return self.request.user

    def get_success_url(self):
        return reverse(
            'blog:profile',
            kwargs={'username': self.object.username}
        )

    def form_valid(self, form):
        messages.success(self.request, 'Профиль успешно обновлен')
        return super().form_valid(form)


class SignUpView(CreateView):
    form_class = CustomUserCreationForm
    template_name = 'registration/registration_form.html'

    def form_valid(self, form):
        user = form.save()
        login(self.request, user)
        return redirect('blog:profile', username=user.username)


class PostEditView(LoginRequiredMixin, OnlyAuthorMixin, UpdateView):
    model = Post
    form_class = PostForm
    pk_url_kwarg = 'post_id'
    template_name = 'blog/create.html'

    def test_func(self):
        obj = self.get_object()
        return self.request.user == obj.author

    def handle_no_permission(self):
        if self.request.user.is_authenticated:
            messages.error(
                self.request, 'Вы не можете редактировать чужой пост'
            )
        return redirect('blog:post_detail', post_id=self.kwargs['post_id'])

    def get_success_url(self):
        return reverse(
            'blog:post_detail',
            kwargs={'post_id': self.object.id}
        )


class PostDeleteView(LoginRequiredMixin, OnlyAuthorMixin, DeleteView):
    model = Post
    pk_url_kwarg = 'post_id'
    template_name = 'blog/create.html'
    success_url = reverse_lazy('blog:index')

    def handle_no_permission(self):
        if self.request.user.is_authenticated:
            messages.error(self.request, 'Не можешь удалить чужой пост)')
        return super().handle_no_permission()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = PostForm(instance=self.object)
        return context


class CommentCreateView(LoginRequiredMixin, CreateView):
    model = Comment
    form_class = CommentForm
    template_name = 'blog/comment.html'

    def form_valid(self, form):
        form.instance.author = self.request.user
        form.instance.post = get_object_or_404(Post, pk=self.kwargs['post_id'])
        return super().form_valid(form)

    def get_success_url(self):
        return reverse(
            'blog:post_detail',
            kwargs={'post_id': self.kwargs['post_id']}
        )


class CommentEditView(LoginRequiredMixin, OnlyCommentAuthorMixin, UpdateView):
    model = Comment
    form_class = CommentForm
    template_name = 'blog/comment.html'
    pk_url_kwarg = 'comment_id'

    def get_success_url(self):
        return reverse(
            'blog:post_detail',
            kwargs={'post_id': self.object.post.pk}
        )


class CommentDeleteView(
    LoginRequiredMixin, OnlyCommentAuthorMixin, DeleteView
):
    model = Comment
    template_name = 'blog/comment.html'
    pk_url_kwarg = 'comment_id'

    def get_success_url(self):
        return reverse(
            'blog:post_detail',
            kwargs={'post_id': self.object.post.pk}
        )
