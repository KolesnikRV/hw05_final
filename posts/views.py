from django.core.paginator import Paginator
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.db.models import Count
from django.urls.base import reverse

from .models import Follow, Group, Post, User
from .forms import PostForm, CommentForm


def index(request):
    post_list = Post.objects.annotate(comments_count=Count('comments'))\
                            .order_by('-pub_date')
    paginator = Paginator(post_list, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    context = {
        'page': page,
        'paginator': paginator,
    }

    return render(request, 'index.html', context)


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    post_list = group.posts.annotate(comments_count=Count('comments'))\
                           .order_by('-pub_date')
    paginator = Paginator(post_list, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    context = {
        'group': group,
        'paginator': paginator,
        'page': page,
    }

    return render(request, 'group.html', context)


@login_required
def new_post(request):
    form = PostForm(request.POST or None)
    if form.is_valid():
        post = form.save(commit=False)
        post.author = request.user
        post.save()

        return HttpResponseRedirect(reverse('posts:index'))

    return render(request, 'posts/post_new.html', {'form': form})


def profile(request, username):
    author = get_object_or_404(User, username=username)
    post_list = author.posts.all()
    paginator = Paginator(post_list, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    following = False
    if request.user.is_authenticated:
        following = author.following.filter(user=request.user).exists()
    context = {
        'page': page,
        'paginator': paginator,
        'author': author,
        'post_count': paginator.count,
        'following': following,
    }

    return render(request, 'profile.html', context)


def post_view(request, username, post_id):
    post = get_object_or_404(Post, pk=post_id, author__username=username)
    post_count = post.author.posts.count()
    form = CommentForm()
    comments = post.comments.select_related('author')
    context = {
        'author': post.author,
        'post': post,
        'post_count': post_count,
        'form': form,
        'comments': comments,
    }

    return render(request, 'posts/post.html', context)


@login_required
def post_edit(request, username, post_id):
    if request.user.username != username:
        return redirect('posts:post', username=username, post_id=post_id)

    post = get_object_or_404(Post, pk=post_id, author__username=username)
    form = PostForm(request.POST or None,
                    files=request.FILES or None,
                    instance=post)
    if form.is_valid():
        post = form.save(commit=False)
        post.save()

        return HttpResponseRedirect(
            reverse('posts:post',
                    kwargs={'username': username, 'post_id': post_id}),
        )

    return render(
        request,
        'posts/post_new.html',
        {'form': form, 'post': post, 'is_edit': True},
    )


@login_required
def add_comment(request, username, post_id):
    form = CommentForm(request.POST or None)
    post = get_object_or_404(Post, pk=post_id, author__username=username)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.post = post
        comment.author = request.user
        comment.save()

        return HttpResponseRedirect(
            reverse('posts:post',
                    kwargs={'username': username, 'post_id': post_id}),
        )

    return render(request, 'posts/post_new.html', {'form': form})


@login_required
def follow_index(request):
    post_list = Post.objects.filter(author__following__user=request.user)\
                            .annotate(comments_count=Count('comments'))\
                            .order_by('-pub_date')
    paginator = Paginator(post_list, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    context = {
        'page': page,
        'paginator': paginator,
    }

    return render(request, 'follow.html', context)


@login_required
def profile_follow(request, username):
    author = User.objects.get(username=username)
    if author == request.user:
        return redirect('posts:profile', username=username)
    Follow.objects.get_or_create(user=request.user, author=author)

    return redirect('posts:profile', username=username)


@login_required
def profile_unfollow(request, username):
    author = User.objects.get(username=username)
    if author == request.user:
        return redirect('posts:profile', username=username)
    Follow.objects.filter(user=request.user, author=author).delete()

    return redirect('posts:profile', username=username)


def page_not_found(request, exception):
    return render(
        request,
        'misc/404.html',
        {'path': request.path},
        status=404,
    )


def server_error(request):
    return render(request, 'misc/500.html', status=500)
