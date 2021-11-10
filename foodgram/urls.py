from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

from .views import page_not_found, server_error

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('recipe.urls')),
    path('users/', include('users.urls')),
    path('users/', include('django.contrib.auth.urls')),
]


urlpatterns += staticfiles_urlpatterns()
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


handler404 = page_not_found
handler500 = server_error
