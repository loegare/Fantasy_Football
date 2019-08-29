from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404, redirect, render

from .forms import NewTopicForm
from .models import Board, Post, Topic

# Create your views here.


def home(request):
    boards = Board.objects.all()
    boards_names = list()
    return render(request, 'home.html', {'boards': boards})


def board_topics(request, pk):
    # try:
    #     board = Board.objects.get(pk=pk)
    # except Board.DoesNotExist:
    #     raise(Http404)
    board = get_object_or_404(Board, pk=pk)
    return render(request, 'topics.html', {'board':  board})


def new_topic(request, pk):
    board = get_object_or_404(Board, pk=pk)
    user = User.objects.first()  # TODO get currently logged in User
    if request.method == 'POST':
        form = NewTopicForm(request.POST)
        if form.is_valid():
            topic = form.save()
            return redirect('board_topics', pk=board.pk)
    else:
        form = NewTopicForm()
    return render(request, 'new_topic.html', {'form': form})
