import exchange
import shutil
import os

from django.shortcuts import render, render_to_response
from django.template import RequestContext
from django.conf import settings
from geonode.layers.views import _resolve_layer, _PERMISSION_MSG_METADATA
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from exchange.core.models import ThumbnailImage, ThumbnailImageForm
from geonode.maps.views import _resolve_map


def HomeScreen(request):
    return render(request, 'site_index.html')


def layer_metadata_detail(request, layername,
                          template='layers/metadata_detail.html'):

    layer = _resolve_layer(request, layername, 'view_resourcebase',
                           _PERMISSION_MSG_METADATA)

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
            user_upload_thumbnail_filepath = str(
                user_upload_thumbnail.thumbnail_image
            )

            # only create backup for original thumbnail
            if os.path.isfile(default_thumbnail + '.bak') is False:
                os.rename(default_thumbnail, default_thumbnail + '.bak')

            os.rename(user_upload_thumbnail_filepath, default_thumbnail)

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


def map_metadata_detail(request, mapid,
                        template='maps/metadata_detail.html'):

    map_obj = _resolve_map(request, mapid, 'view_resourcebase')

    thumbnail_dir = os.path.join(settings.MEDIA_ROOT, 'thumbs')
    default_thumbnail_array = map_obj.get_thumbnail_url().split('/')
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
            user_upload_thumbnail_filepath = str(
                user_upload_thumbnail.thumbnail_image
            )

            # only create backup for original thumbnail
            if os.path.isfile(default_thumbnail + '.bak') is False:
                os.rename(default_thumbnail, default_thumbnail + '.bak')

            os.rename(user_upload_thumbnail_filepath, default_thumbnail)

            return HttpResponseRedirect(
                reverse('map_metadata_detail', args=[mapid])
            )
    else:
        thumb_form = ThumbnailImageForm()

    thumbnail = map_obj.get_thumbnail_url
    return render_to_response(template, RequestContext(request, {
        "layer": map_obj,
        "mapid": mapid,
        'SITEURL': settings.SITEURL[:-1],
        "thumbnail": thumbnail,
        "thumb_form": thumb_form
    }))
