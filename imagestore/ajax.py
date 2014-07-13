from django.http import HttpResponse
from django.utils import simplejson as json
from django.utils.safestring import mark_safe

from .models import Image


def get_image_thumbs(request):
    try:
        images = Image.objects.all()
        thumbs = {}
        for image in images:
            thumbs[image.pk] = mark_safe(image.admin_thumbnail_path())
        success = True
    except:
        success = False
    return HttpResponse(json.dumps({'success': success, 'thumbs': thumbs}), mimetype="application/json")
