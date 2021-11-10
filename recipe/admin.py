from django.contrib import admin

from .models import Preview, Category, Stream



class PreviewAdmin(admin.ModelAdmin):
    list_display = ('pk', 'user', 'name')
    list_filter = ('name', )
    search_fields = ('name', )


class CategoryAdmin(admin.ModelAdmin):
    list_display = ('pk', 'name', 'description')
    list_filter = ('name', )
    search_fields = ('name', )


class StreamAdmin(admin.ModelAdmin):
    list_display = ("__str__", "started_at", "is_live")
    readonly_fields = ("hls_url",)


admin.site.register(Preview, PreviewAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Stream, StreamAdmin)