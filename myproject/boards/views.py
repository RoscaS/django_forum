from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator

from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib.auth.models import User
from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Count
from django.urls import reverse_lazy

from django.views.generic import UpdateView, ListView
from django.utils import timezone
from django.urls import reverse

from .models import Board, Topic, Post
from .forms import NewTopicForm, PostForm


@method_decorator(login_required, name='dispatch')
class PostUpdateView(UpdateView): # GCBV
    model         = Post
    fields        = ('message', )
    template_name = 'edit_post.html'
    pk_url_kwarg  = 'post_pk'
    context_object_name = 'post'

    def get_queryset(self): # A topic can only be edited by the owner
        queryset = super().get_queryset()
        return queryset.filter(created_by=self.request.user)

    def form_valid(self, form):
        post = form.save(commit=False)
        post.updated_by = self.request.user
        post.updated_at = timezone.now()
        post.save()
        return redirect(
            'topic_posts', 
            pk = post.topic.board.pk, 
            topic_pk = post.topic.pk
        )


class BoardListView(ListView): 
    model               = Board
    context_object_name = 'boards'
    template_name       = 'home.html'


class TopicListView(ListView):
    '''
    `paginator`, `page_obj`, `is_paginated`, `object_list`
    Are available to use in template.
    Variable set in `context_object_name` is alias for `object_list`.

    '''
    model               = Topic
    context_object_name = 'topics'
    template_name       = 'topics.html'
    paginate_by         =  10

    def get_context_data(self, **kwargs):
        kwargs['board'] = self.board
        return super().get_context_data(**kwargs)

    def get_queryset(self):
        self.board = get_object_or_404(Board, pk=self.kwargs.get('pk'))
        queryset = self.board.topics.order_by(
            '-last_updated').annotate(replies=Count('posts')-1)
        return queryset


@login_required
def new_topic(request, pk):
    board = get_object_or_404(Board, pk=pk)
    if request.method == 'POST':
        form = NewTopicForm(request.POST)
        if form.is_valid():
            topic = form.save(commit=False)
            topic.board = board
            topic.starter = request.user
            topic.save()
            Post.objects.create(
                message=form.cleaned_data.get('message'),
                topic=topic,
                created_by=request.user
            )
            return redirect('topic_posts', pk=pk, topic_pk=topic.pk)
    else:
        form = NewTopicForm()
    return render(request, 'new_topic.html', {'board': board, 'form': form})


class PostListView(ListView):
    model = Post
    context_object_name = 'posts'
    template_name = 'topics_posts.html'
    paginate_by = 10

    def get_context_data(self, **kwargs):
        session_key= f'viewed_topic_{self.topic.pk}'
        if not self.request.session.get(session_key, False):
            self.topic.views += 1
            self.topic.save()
            self.request.session[session_key] = True

        kwargs['topic'] = self.topic
        return super().get_context_data(**kwargs)

    def get_queryset(self):
        self.topic = get_object_or_404(
            Topic, board__pk=self.kwargs.get('pk'), pk=self.kwargs.get('topic_pk'))
        queryset = self.topic.posts.order_by('created_at')
        return queryset


@login_required
def reply_topic(request, pk, topic_pk):
    topic = get_object_or_404(Topic, board__pk=pk, pk=topic_pk)
    if request.method == 'POST':
        form = PostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.topic = topic
            post.created_by = request.user
            post.save()

            topic.last_updated = timezone.now()
            topic.save()

            topic_url = reverse('topic_posts', kwargs={'pk': pk, 'topic_pk': topic_pk})
            topic_post_url = f'{topic_url}?page={topic.get_page_count()}#{post.pk}'

            return redirect(topic_post_url)
    else:
        form = PostForm()
    return render(request, 'reply_topic.html', {'topic': topic, 'form': form})


