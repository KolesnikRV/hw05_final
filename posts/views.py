from django.core.paginator import Paginator
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required

from .models import Follow, Group, Post, User
from .forms import PostForm, CommentForm


def index(request):
    post_list = Post.objects.all()
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
    post_list = group.posts.all()
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

        return redirect('posts:index')

    return render(request, 'posts/post_new.html', {'form': form})


def profile(request, username):
    author = get_object_or_404(User, username=username)
    post_list = author.posts.all()
    post_count = post_list.count()
    paginator = Paginator(post_list, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    following = request.user.is_authenticated
    if following:
        following = author.following.filter(user=request.user).exists()
    context = {
        'page': page,
        'paginator': paginator,
        'author': author,
        'post_count': post_count,
        'following': following,
    }

    return render(request, 'profile.html', context)


def post_view(request, username, post_id):
    author = get_object_or_404(User, username=username)
    post = get_object_or_404(Post, pk=post_id, author=author)
    post_count = author.posts.all().count()
    form = CommentForm()
    comments = post.comments.all()
    context = {
        'author': author,
        'post': post,
        'post_count': post_count,
        'form': form,
        'comments': comments,
    }

    return render(request, 'posts/post.html', context)


@login_required
def post_edit(request, username, post_id):
    author = get_object_or_404(User, username=username)
    if request.user != author:
        return redirect('posts:post', username=username, post_id=post_id)

    post = get_object_or_404(Post, pk=post_id, author=author)
    form = PostForm(request.POST or None,
                    files=request.FILES or None,
                    instance=post)
    if form.is_valid():
        post = form.save(commit=False)
        post.save()

        return redirect(
            'posts:post',
            username=username,
            post_id=post_id,
        )

    return render(
        request,
        'posts/post_new.html',
        {'form': form, 'post': post, 'is_edit': True},
    )


@login_required
def add_comment(request, username, post_id):
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.post = Post.objects.get(pk=post_id)
        comment.author = request.user
        comment.save()

        return redirect(
            'posts:post',
            username=username,
            post_id=post_id,
        )

    return render(request, 'posts/post_new.html', {'form': form})


@login_required
def follow_index(request):
    user = get_object_or_404(User, username=request.user)
    author_list = []
    follower = user.follower.all()
    for item in follower:
        author_list.append(item.author)

    post_list = Post.objects.filter(author__in=author_list)
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
    if not Follow.objects.filter(user=request.user, author=author).exists():
        Follow(user=request.user, author=author).save()

    return redirect('posts:profile', username=username)


@login_required
def profile_unfollow(request, username):
    author = User.objects.get(username=username)
    if author == request.user:
        return redirect('posts:profile', username=username)
    follower = get_object_or_404(Follow, user=request.user, author=author)
    follower.delete()

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
