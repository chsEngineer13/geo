#
# Common functions for thumbnail handling.
#

from geonode.utils import http_client


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

    resp, image = http_client.request(thumbnail_create_url)

    if('ServiceException' in image or resp.status < 200 or resp.status > 299):
        return None

    return image
