import json
import os
import mimetypes
from wsgiref.util import FileWrapper

from django.http import HttpResponse, HttpResponseForbidden, StreamingHttpResponse
from django.utils import timezone
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_http_methods

from foodgram.settings import PAGINATOR_ITEMS_PER_PAGE

from .models import Preview, Category, Stream, User
from .forms import StreamForm
# from .utils import (BREAKFAST, DINNER, LUNCH, parse_recipe, parse_tags,
#                     validate_tags_ingredients)


def index(request):
    previews = Preview.objects.all()
    print(previews)
    paginator = Paginator(previews, PAGINATOR_ITEMS_PER_PAGE)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    context = {
        'page': page, 
        'paginator': paginator,
        'username': request.user.username,
        'index': True
    }
    print(context)
    return render(request, 'full_hc.html', context)


def categories(request):
    print(request)
    categories = Category.objects.all()[:10]
    context = {'categories': categories, 'username': request.user.username, 'cat': True}
    return render(request, 'categories_hc.html', context)


def category(request, pk):
    category = Category.objects.get(pk=pk)
    context = {'category': category, 'username': request.user.username}
    return render(request, 'category_hc.html', context)


def single_stream(request, username):
    user = User.objects.get(username=username)
    print(user, user.is_active)
    stream = Stream.objects.get(user=user)
    context = {'stream_url': f'{stream.key}/index.m3u8', 'username': request.user.username}
    return render(request, 'stream_hc.html', context)


def stream_settings(request, username):
    if not request.user.is_active or request.user.username != username:
        raise Exception('that\'s not your profile')
    user = get_object_or_404(User, username=username)
    stream = get_object_or_404(Stream, user=user)
    context = {'stream': stream, 'stream_url': f'{stream.key}/index.m3u8', 'username': user.username}
    return render(request, 'stream_settings_hc.html', context)


def streams(request):
    streams = Stream.objects.filter(started_at__isnull=False)
    print(streams)
    paginator = Paginator(streams, PAGINATOR_ITEMS_PER_PAGE)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    context = {'username': request.user.username, 'page': page, 'paginator': paginator}
    return render(request, 'streams_hc.html', context)


@require_POST
@csrf_exempt
def start_stream(request):
    """ This view is called when a stream starts.
    """
    stream = get_object_or_404(Stream, key=request.POST["name"])

    # Ban streamers by setting them inactive
    if not stream.user.is_active:
        return HttpResponseForbidden("Inactive user")

    # Don't allow the same stream to be published multiple times
    if stream.started_at:
        return HttpResponseForbidden("Already streaming")

    stream.started_at = timezone.now()
    stream.save()

    # Redirect to the streamer's public username
    return redirect('/' + stream.user.username)


@require_POST
@csrf_exempt
def stop_stream(request):
    """ This view is called when a stream stops.
    """
    Stream.objects.filter(key=request.POST["name"]).update(started_at=None)
    return HttpResponse("OK")


@csrf_exempt
def stream_change_key(request):
    user = request.user
    stream = get_object_or_404(Stream, user=user)
    stream_key = request.POST['key']
    form = StreamForm(request.POST or None, files=request.FILES or None, instance=stream)
    print(form)
    context = {'stream': stream, 'stream_url': f'{stream.key}/index.m3u8', 'username': user.username, 'form': form}
    if form.is_valid() and len(stream_key) == 20:
        form.save()
    if len(stream_key) != 20:
        context['error'] = True
    context['stream_url'] = f'{stream_key}/index.m3u8'
    return render(request, 'stream_settings_hc.html', context)