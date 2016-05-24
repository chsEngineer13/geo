from django.shortcuts import render, render_to_response
from django.template import RequestContext
from django.conf import settings
from geonode.layers.views import _resolve_layer, _PERMISSION_MSG_METADATA
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from exchange.core.models import ThumbnailImage, ThumbnailImageForm
import os


def HomeScreen(request):
    return render(request, 'site_index.html')


def layer_metadata_detail(request, layername,
                          template='layers/metadata_detail.html'):
    if request.method == 'POST':
        thumb_form = ThumbnailImageForm(request.POST, request.FILES)
        if thumb_form.is_valid():
            new_img = ThumbnailImage(
                thumbnail_image=request.FILES['thumbnail_image']
            )
            new_img.save()

            # Redirect to the document list after POST
            return HttpResponseRedirect(reverse('views.layer_metadata_detail'))
    else:
        thumb_form = ThumbnailImageForm()

    layer = _resolve_layer(request, layername, 'view_resourcebase',
                           _PERMISSION_MSG_METADATA)
    default_thumbnail_array = layer.get_thumbnail_url().split('/')
    default_thumbnail_name = default_thumbnail_array[
        len(default_thumbnail_array) - 1
    ]
    custom_thumbnail_dir = os.path.join(settings.MEDIA_ROOT, 'thumbs')
    custom_thumbnail_name = 'custom_' + default_thumbnail_name
    custom_thumbnail = os.path.join(custom_thumbnail_dir,
                                    custom_thumbnail_name)
    if not os.path.exists(custom_thumbnail_dir):
        os.makedirs(custom_thumbnail_dir)
    if os.path.isfile(custom_thumbnail):
        thumbnail = '/uploaded/thumbs/' + custom_thumbnail_name
    else:
        thumbnail = layer.get_thumbnail_url
    return render_to_response(template, RequestContext(request, {
        "layer": layer,
        'SITEURL': settings.SITEURL[:-1],
        "thumbnail": thumbnail,
        "thumb_form": thumb_form
    }))
