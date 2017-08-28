#
# There is only one view for the Thumbnail API.
#
# When the view is called with a GET request it returns
# either a blank image *or* the image stored in the database.
#


from django.http import HttpResponse

from base64 import b64decode
import imghdr
import os

from .models import Thumbnail, save_thumbnail

# cache the blank gif for missing images.
TEST_DIR = os.path.dirname(__file__)
BLANK_GIF = open(os.path.join(TEST_DIR, 'static/blank.gif'), 'r').read()


def thumbnail_view(request, objectType, objectId):
    global BLANK_GIF, ID_PATTERN

    thumb = None
    try:
        thumb = Thumbnail.objects.get(object_type=objectType,
                                      object_id=objectId)
    except Thumbnail.DoesNotExist:
        # move along, the code tests for None later.
        pass

    if(request.method == 'GET'):
        # if the thumb is not None, return it.
        if(thumb is not None):
            return HttpResponse(thumb.thumbnail_img,
                                content_type=thumb.thumbnail_mime)

        # else return the blank gif.
        return HttpResponse(BLANK_GIF, content_type='image/gif')
    elif(request.method == 'POST'):
        body_len = len(request.body)

        # ensure the thumbnail is < 400kb.
        # This is an arbitrary check I've added, it could be
        # adjusted easily.
        max_bytes = 400000
        if(body_len > max_bytes):
            return HttpResponse(status=400, content='Thumbnail too large.')

        image_bytes = request.body
        # check to see if the image has been uploaded as a base64
        #  image.
        if(request.body[0:22] == 'data:image/png;base64,'):
            image_bytes = b64decode(request.body[22:])

        image_type = imghdr.what('', h=image_bytes)
        if(image_type is None):
            return HttpResponse(status=400, content='Bad thumbnail format.')

        # if the thumbnail does not exist, create a new one.
        save_thumbnail(objectType, objectId, 'image/'+image_type, image_bytes, False)

        # return a success message.
        return HttpResponse(status=201)
