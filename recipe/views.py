import json
import os
import mimetypes
from functools import partial
from wsgiref.util import FileWrapper

from django.http import HttpResponse, HttpResponseForbidden, StreamingHttpResponse
from django.utils import timezone
from django.utils.crypto import get_random_string
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
    streams = Stream.objects.filter(category=category, started_at__isnull=False)
    paginator = Paginator(streams, PAGINATOR_ITEMS_PER_PAGE)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    context = {
        'page': page, 
        'paginator': paginator, 
        'category': category, 
        'username': request.user.username,
        'has_content': len(streams) > 0
    }
    return render(request, 'category_hc.html', context)


def single_stream(request, username):
    stream = Stream.objects.get(user__username=username)
    context = {'stream_url': f'{stream.key}.m3u8', 'username': request.user.username, 'live': stream.is_live}
    return render(request, 'stream_hc.html', context)


def private_stream(request, username):
    stream = Stream.objects.get(user__username=username)
    context = {'stream_url': f'{stream.key}.m3u8', 'live': stream.is_live, 'name': username}
    if request.user == stream.user or request.POST.get('secret_key') == stream.private_key:
        context['allowed'] = True
    if request.method == 'POST' and request.POST.get('secret_key') != stream.private_key:
        context['error'] = 'wrong secret key'
    return render(request, 'private_stream_hc.html', context)


def stream_settings(request, username):
    if not request.user.is_active or request.user.username != username:
        raise Exception('that\'s not your profile')
    user = get_object_or_404(User, username=username)
    stream = get_object_or_404(Stream, user=user)
    print(request.POST)
    if request.POST.get('method') == 'change_private_key':
        print(123)
        stream.private_key = partial(get_random_string, 22)()
        stream.save()
    context = {'stream': stream, 'stream_url': f'{stream.key}/index.m3u8', 'username': user.username, 'live': stream.is_live}
    return render(request, 'stream_settings_hc.html', context)


def streams(request):
    streams = Stream.objects.filter(started_at__isnull=False).order_by('started_at')
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
    print(request.POST)
    stream = get_object_or_404(Stream, key=request.POST["name"])

    # Ban streamers by setting them inactive
    if not stream.user.is_active:
        return HttpResponseForbidden("Inactive user")

    # Don't allow the same stream to be published multiple times
    if stream.started_at:
        context = {'stream': stream, 'stream_url': f'{stream.key}.m3u8', 'live': stream.is_live, 'username': request.user.username}
        if stream.private_key:
            context['priv_live'] = True
        return render(request, 'stream_settings_hc.html', context)

    stream.started_at = timezone.now()
    if request.POST.get('method') == 'PUT':
        stream.private_key = partial(get_random_string, 22)()
    stream.save()

    result_url = f'/stream/private/{stream.user.username}/' if request.POST.get('method') == 'PUT' else f'/stream/{stream.user.username}/'
    # Redirect to the streamer's public username
    return redirect(result_url)


@require_POST
@csrf_exempt
def stop_stream(request):
    """ This view is called when a stream stops.
    """
    stream = get_object_or_404(Stream, key=request.POST["name"])
    stream.started_at = None
    stream.private_key = None
    stream.save()
    context = {'stream': stream, 'stream_url': f'{stream.key}.m3u8', 'live': stream.is_live, 'username': request.user.username}
    return render(request, 'stream_settings_hc.html', context)


@csrf_exempt
@require_POST
def stream_change_key(request):
    user = request.user
    stream = get_object_or_404(Stream, user=user)
    stream_key = request.POST['key']
    print(request.FILES or None)
    form = StreamForm(request.POST or None, files=request.FILES or None, instance=stream)
    print(form)
    context = {'stream': stream, 'stream_url': f'{stream.key}.m3u8', 'username': user.username, 'form': form, 'live': stream.is_live}
    if form.is_valid() and len(stream_key) == 20:
        form.save()
    if len(stream_key) != 20:
        context['error'] = True
    context['stream_url'] = f'{stream_key}/index.m3u8'
    return render(request, 'stream_settings_hc.html', context)

