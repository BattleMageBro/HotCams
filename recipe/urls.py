from django.urls import path

from .views import index, categories, category, start_stream, stop_stream, single_stream, stream_settings, stream_change_key, streams


def fake_view(*args, **kwargs):
    """ This view should never be called because the URL paths
        that map here will be served by nginx directly.
    """
    raise Exception("This should never be called!")


urlpatterns = [
    path('', index, name='index'),
    path('categories/', categories, name='categories'),
    path('category/<int:pk>/', category, name='category'),
    path("start_stream/", start_stream, name="start-stream"),
    path("stop_stream/", stop_stream, name="stop-stream"),
    path("<str:username>/index.m3u8/", fake_view, name="hls-url"),
    path("stream/<str:username>/", single_stream, name="streaming"),
    path("streams/", streams, name='streams'),
    path("profile/<str:username>/", stream_settings, name="profile"),
    path("change_key/", stream_change_key, name="change_key"),
]
