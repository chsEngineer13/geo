import arcrest

import datetime
import json
import uuid

from osgeo import ogr, osr
from pycsw.core.util import bbox2wktpolygon
from shapely.wkt import loads


def transform_projection(layer, srs):
    bbox = layer.extent.bbox
    wkt = bbox2wktpolygon(bbox)

    source = osr.SpatialReference()
    source.ImportFromEPSG(srs)

    target = osr.SpatialReference()
    target.ImportFromEPSG(4326)

    transform = osr.CoordinateTransformation(source, target)

    point = ogr.CreateGeometryFromWkt(wkt)
    point.Transform(transform)

    wkt = point.ExportToWkt()
    bbox = loads(wkt).bounds
    bbox = [str(val) for val in bbox]

    return bbox


def create_layer_dict(service, layer, server_type):
    if server_type == 'ImageServer':
        srs = layer['spatialReference']['wkid']
        bbox = (layer['extent']['xmin'],
                layer['extent']['ymin'],
                layer['extent']['xmax'],
                layer['extent']['ymax'])
    else:
        srs = service.spatialReference.wkid
        bbox = (layer.extent.xmin,
                layer.extent.ymin,
                layer.extent.xmax,
                layer.extent.ymax)

    if srs == 102100:
        srs = 3857

    if srs != 4326:
        bbox = transform_projection(layer, srs)

    if server_type == 'ImageServer':
        layer_type = 'ESRI:ArcGIS:ImageServer'
        layer_name = layer['name']
        layer_id = None
        source = service.url

    if server_type == 'MapServer':
        layer_type = 'ESRI:ArcGIS:MapServer'
        layer_name = layer.name
        layer_id = layer.id
        source = layer.url
    xmin, ymin, xmax, ymax = bbox

    parsed_url = source.split(server_type)[0] + server_type

    layer_dict = {
        'identifier': str(uuid.uuid4()),
        'title': layer_name,
        'creator': layer.copyrightText,
        'type': layer_type,
        'title_alternate': layer_id,
        'modified': datetime.datetime.now(),
        'abstract': service.serviceDescription,
        'source': parsed_url,
        'xmin': xmin,
        'ymin': ymin,
        'xmax': xmax,
        'ymax': ymax
    }
    return layer_dict


def create_layers_list(service, server_type):
    if server_type == 'ImageServer':
        layers = [json.loads(service._contents)]
    elif server_type == 'MapServer':
        layers = service.layers

    layers_list = []

    for layer in layers:
        try:
            layers_list.append(create_layer_dict(service, layer, server_type))
        except Exception, e:
            print e

    return layers_list


def get_service_metadata(service):
    service_info = service.url.split('/rest/services/')[1].split('/')
    return {'folder': service_info[0], 'name': service_info[1], 'type': service_info[2]}


def process_service(service):
    service_data = get_service_metadata(service)
    print "Processing service {0}".format(service_data['name'])
    try:
        service.spatialReference
    except Exception, e:
        print e
        return None
    layers_list = create_layers_list(service, service_data['type'])
    service_data['layers'] = layers_list

    return service_data
