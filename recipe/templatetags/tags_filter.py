from django import template

register = template.Library()


@register.filter
def make_tags(request, tag):
    tags = request.GET.getlist('tags')
    if tag in tags:
        tags.remove(tag)
    else:
        tags.append(tag)
    if not tags:
        return ''
    result = '?tags=' + '&tags='.join(tags)
    return result
