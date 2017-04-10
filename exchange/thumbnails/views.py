#
# There is only one view for the Thumbnail API.
# 
# When the view is called with a GET request it returns
# either a blank image *or* the image stored in the database.
#


from django.http import HttpResponse

import imghdr
import os
import re

# cache the blank gif for missing images.
BLANK_GIF = open(os.path.join(os.path.dirname(__file__), 'static/blank.gif'),'r').read()

from .models import Thumbnail

def thumbnail_view(request, objectType, objectId):
    global BLANK_GIF, ID_PATTERN

    if(request.method == 'GET'):
        # check the database for a matching object type/id

        try:
            thumb = Thumbnail.objects.get(object_type=objectType, object_id=objectId)
            # if the image exists, return it.
            return HttpResponse(thumb.thumbnail_img, content_type=thumb.thumbnail_mime)
        except Thumbnail.DoesNotExist:
            # just move on to returning the blank image.
            pass

        # else return the blank gif.
        return HttpResponse(BLANK_GIF, content_type='image/gif')
    elif(request.method == 'POST'):
        # check to ensure an image has been uploaded.

        if('thumbnail' not in request.FILES):
            return HttpResponse(status=400, content='Missing "thumbnail".')

        # ensure the thumbnail is < 400kb.
        # This is an arbitrary check I've added, it could be 
        # adjusted easily.
        max_bytes = 400000

        if(request.FILES['thumbnail'].size > max_bytes):
            return HttpResponse(status=400, content='Thumbnail too large.')

        image_bytes = request.FILES['thumbnail'].read()

        image_type = imghdr.what('', h=image_bytes)

        if(image_type is None):
            return HttpResponse(status=400, content='Bad thumbnail format.')

        try:
            thumb = Thumbnail.objects.get(object_type=objectType, object_id=objectId)
            # update the thumbnail
            thumb.thumbnail_mime = 'image/'+image_type
            thumb.thumbnail_img = image_bytes
        except Thumbnail.DoesNotExist:
            thumb = Thumbnail(object_type=objectType, object_id=objectId,
                      thumbnail_mime='image/'+image_type, thumbnail_img=image_bytes)

        thumb.save()

        # return a success message.
        return HttpResponse(status=201)

