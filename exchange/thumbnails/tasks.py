import time
import logging
from celery.task import task

from django.db.models.signals import post_save
from geonode.layers.models import Layer
from geonode.maps.models import Map
from geonode.utils import http_client

from .models import is_automatic
from .models import save_thumbnail

logger = logging.getLogger(__name__)


# Get a thumbnail image generated from GeoServer
#
# This is based on the function in GeoNode but gets
# the image bytes instead.
#
# @return PNG bytes.
#
def get_gs_thumbnail(instance):
    from geonode.geoserver.helpers import ogc_server_settings

    if instance.class_name == 'Map':
        local_layers = []
        for layer in instance.layers:
            if layer.local:
                local_layers.append(layer.name)
        layers = ",".join(local_layers).encode('utf-8')
        if(len(local_layers) == 0):
            return None
    else:
        layers = instance.typename.encode('utf-8')

    params = {
        'layers': layers,
        'format': 'image/png8',
        'width': 200,
        'height': 150,
        'TIME': '-99999999999-01-01T00:00:00.0Z/99999999999-01-01T00:00:00.0Z'
    }

    # Avoid using urllib.urlencode here because it breaks the url.
    # commas and slashes in values get encoded and then cause trouble
    # with the WMS parser.
    p = "&".join("%s=%s" % item for item in params.items())

    thumbnail_create_url = ogc_server_settings.LOCATION + \
        "wms/reflect?" + p

    tries = 0
    max_tries = 30
    while tries < max_tries:
        logger.debug(
            'Thumbnail: Requesting thumbnail from GeoServer. '
            'Attempt %d of %d',
            tries + 1, max_tries)
        resp, image = http_client.request(thumbnail_create_url)
        if 200 <= resp.status <= 299:
            if 'ServiceException' not in image:
                return image
        else:
            # Unexpected Error Code, Stop Trying
            logger.debug(
                'Thumbnail: Encountered unexpected status code: %d.  '
                'Aborting.',
                resp.status)
            logger.debug(resp)
            break

        # Layer not ready yet, try again
        tries += 1
        time.sleep(1)

    return None


@task(
    max_retries=1,
)
def generate_thumbnail_task(instance_id, class_name):
    obj_type = None
    if class_name == 'Layer':
        try:
            instance = Layer.objects.get(typename=instance_id)
            obj_type = 'layers'
        except Layer.DoesNotExist:
            # Instance not saved yet, nothing more we can do
            logger.debug(
                'Thumbnail: Layer \'%s\' does not yet exist, cannot '
                'generate thumbnail.',
                instance_id)
            return
    elif class_name == 'Map':
        try:
            instance = Map.objects.get(id=instance_id)
            obj_type = 'maps'
        except Map.DoesNotExist:
            # Instance not saved yet, nothing more we can do
            logger.debug(
                'Thumbnail: Map \'%s\' does not yet exist, cannot '
                'generate thumbnail.',
                instance_id)
            return
    else:
        logger.debug(
            'Thumbnail: Unsupported class: %s. Aborting.', class_name)
        return

    logger.debug(
        'Thumbnail: Generating thumbnail for \'%s\' of type %s.',
        instance_id, class_name)
    if(instance_id is not None and is_automatic(obj_type, instance_id)):
        # have geoserver generate a preview png and return it.
        thumb_png = get_gs_thumbnail(instance)

        if(thumb_png is not None):
            logger.debug(
                'Thumbnail: Thumbnail successfully generated for \'%s\'.',
                instance_id)
            save_thumbnail(obj_type, instance_id, 'image/png', thumb_png, True)
        else:
            logger.debug(
                'Thumbnail: Unable to get thumbnail image from '
                'GeoServer for \'%s\'.',
                instance_id)


# This is used as a post-save signal that will
# automatically geneirate a new thumbnail if none existed
# before it.
def generate_thumbnail(instance, sender, **kwargs):
    instance_id = None
    obj_type = None
    if instance.class_name == 'Layer':
        instance_id = instance.typename
        obj_type = 'layers'
    elif instance.class_name == 'Map':
        instance_id = instance.id
        obj_type = 'maps'

    if instance_id is not None:
        if instance.is_published:
            logger.debug(
                'Thumbnail: Issuing generate thumbnail task for \'%s\'.',
                instance_id)
            generate_thumbnail_task.delay(
                instance_id=instance_id, class_name=instance.class_name)
        else:
            logger.debug(
                'Thumbnail: Instance \'%s\' is not published, skipping '
                'generation.',
                instance_id)
    else:
        logger.debug(
            'Thumbnail: Unsupported class: \'%s\'. Unable to generate '
            'thumbnail.',
            instance.class_name)


def register_post_save_functions():
    # Disconnect first in case this function is called twice
    logger.debug('Thumbnail: Registering post_save functions.')
    post_save.disconnect(generate_thumbnail, sender=Layer)
    post_save.connect(generate_thumbnail, sender=Layer, weak=False)
    post_save.disconnect(generate_thumbnail, sender=Map)
    post_save.connect(generate_thumbnail, sender=Map, weak=False)


register_post_save_functions()
