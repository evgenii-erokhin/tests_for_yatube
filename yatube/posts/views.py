from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from .forms import PostForm, CommentForm
from .models import Group, Post, User
from .utils import get_pages


def index(request):
    posts = Post.objects.select_related('group')
    return render(request, 'posts/index.html',
                  {'page_obj': get_pages(request, posts)})


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    posts = group.posts.select_related('author')
    return render(request, 'posts/group_list.html',
                  {'group': group,
                   'page_obj': get_pages(request, posts)})


def profile(request, username):
    author = get_object_or_404(User, username=username)
    posts = author.posts.all()
    return render(request, 'posts/profile.html',
                  {'page_obj': get_pages(request, posts),
                   'author': author})


def post_detail(request, post_id):
    posts = get_object_or_404(Post, pk=post_id)
    comments = posts.comments.all()
    form = CommentForm()
    return render(request, 'posts/post_detail.html', {'posts': posts,
                                                      'form': form,
                                                      'comments': comments})


@login_required
def post_create(request):
    form = PostForm(request.POST or None, files=request.FILES or None)
    if form.is_valid():
        post = form.save(commit=False)
        post.author = request.user
        post.save()
        return redirect(f'/profile/{request.user}/')

    return render(request, 'posts/create_post.html', {'form': form, })


@login_required
def post_edit(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    if request.user != post.author:
        return redirect(f'posts/{post_id}/')

    form = PostForm(request.POST or None, files=request.FILES or None,
                    instance=post)
    if form.is_valid():
        post.save()
        return redirect(f'/posts/{post_id}/')
    return render(request, 'posts/create_post.html', {'form': form,
                                                      'is_edit': True})


@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect('posts:post_detail', post_id=post_id)
