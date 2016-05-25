import exchange
from django.shortcuts import render, render_to_response
from django.template import RequestContext
from django.conf import settings
from geonode.layers.views import _resolve_layer, _PERMISSION_MSG_METADATA
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from exchange.core.models import ThumbnailImage, ThumbnailImageForm
import shutil
import os


def HomeScreen(request):
    return render(request, 'site_index.html')


def layer_metadata_detail(request, layername,
                          template='layers/metadata_detail.html'):

    layer = _resolve_layer(request, layername, 'view_resourcebase',
                           _PERMISSION_MSG_METADATA)

    if ThumbnailImage.objects.all()[0] is None:
        no_custom_thumb = True

    thumbnail_dir = os.path.join(settings.MEDIA_ROOT, 'thumbs')
    default_thumbnail_array = layer.get_thumbnail_url().split('/')
    default_thumbnail_name = default_thumbnail_array[
        len(default_thumbnail_array) - 1
    ]
    default_thumbnail = os.path.join(thumbnail_dir, default_thumbnail_name)

    if request.method == 'POST':
        thumb_form = ThumbnailImageForm(request.POST, request.FILES)
        if thumb_form.is_valid():
            new_img = ThumbnailImage(
                thumbnail_image=request.FILES['thumbnail_image']
            )
            new_img.save()
            user_upload_thumbnail = ThumbnailImage.objects.all()[0]
            user_upload_thumbnail_url = str(user_upload_thumbnail.thumbnail_image)
            user_upload_array = user_upload_thumbnail_url.split('/')
            user_upload_file_name = user_upload_array[
                len(user_upload_array) - 1
            ]
            shutil.copy(user_upload_thumbnail_url, thumbnail_dir)
            user_upload_new = os.path.join(thumbnail_dir, user_upload_file_name)
            if no_custom_thumb is True:
                os.rename(default_thumbnail, default_thumbnail_name + '.bak')
            os.rename(user_upload_new, default_thumbnail_name)

            return HttpResponseRedirect(
                reverse('layer_metadata_detail', args=[layername])
            )
    else:
        thumb_form = ThumbnailImageForm()

    thumbnail = layer.get_thumbnail_url
    return render_to_response(template, RequestContext(request, {
        "layer": layer,
        'SITEURL': settings.SITEURL[:-1],
        "thumbnail": thumbnail,
        "thumb_form": thumb_form
    }))
