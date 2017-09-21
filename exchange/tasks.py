from celery.task import task
from celery.utils.log import get_task_logger
from exchange.core.models import CSWRecord
from geonode.catalogue import get_catalogue
from xml.sax.saxutils import escape
from geonode.services.models import Service
import datetime

import time

logger = get_task_logger(__name__)


class UpstreamServiceImpairment(Exception):
    pass


class Record(dict):
    """dot.notation access to dictionary attributes"""
    __getattr__ = dict.get
    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__


@task(
    bind=True,
    max_retries=1,
)
def create_record(self, id):

    scheme_choices = (('ESRI:AIMS--http-get-map', 'MapServer'),
                      ('ESRI:AIMS--http-get-feature', 'FeatureServer'),
                      ('ESRI:AIMS--http-get-image', 'ImageServer'),
                      ('WWW:LINK-1.0-http--json', 'JSON'),
                      ('OGC:KML', 'KML'),
                      ('WWW:LINK-1.0-http--rss', 'RSS'),
                      ('WWW:DOWNLOAD', 'SHAPE'),
                      ('WWW:LINK-1.0-http--soap', 'SOAP'),
                      ('OGC:WCS', 'WCS'),
                      ('OGC:WFS', 'WFS'),
                      ('OGC:CS-W', 'CSW'),
                      ('OGC:WMS', 'WMS'),
                      ('OGC:WPS', 'WPS'))


    def build_service_url(service, type):
        url = service.base_url;
        if type == 'WMSServer':
            url = url.replace('rest/services', 'services')
            url += 'WMSServer?request=GetCapabilities&amp;service=WMS'
        elif type == 'KmlServer':
            url += 'generateKml';
        elif type == 'FeatureServer':
            url = url.replace('MapServer', 'FeatureServer')
        elif type == 'WFSServer':
            url = url.replace('rest/services', 'services')
            url += 'WFSServer?request=GetCapabilities&amp;service=WFS';

        return { 'scheme': get_types(type.lower()), 'url': url}

    def get_refs(service):
        values = []
        references = service.service_refs.split(',')
        for reference in references:
           values.append(build_service_url(service, reference.strip()))

        return values

    def get_types(server_type):

        if 'REST' in server_type or 'mapserver' in server_type:
            layer_type = 'ESRI:ArcGIS:MapServer'
        elif 'kml' in server_type:
            layer_type = 'OGC:KML'
        elif 'wfs' in server_type:
            layer_type = 'OGC:WFS'
        else:
            layer_type = 'OGC:WMS'

        return layer_type

    catalogue = get_catalogue()
    service = Service.objects.get(pk=id)
    if service.type in ["WMS", "OWS"]:
        for record in service.servicelayer_set.all():
            item = Record({
                'uuid': record.uuid,
                'title': record.title.encode('ascii', 'xmlcharrefreplace'),
                'creator': service.owner.username,
                'record_type': 'dataset',
                'modified': datetime.datetime.now(),
                'typename': record.typename,
                'date': service.date,
                'abstract': record.description.encode('ascii', 'xmlcharrefreplace') if record.description else '',
                'format': get_types(service.type),
                'base_url': service.base_url,
                'references': [{ 'scheme': "OGC:WMS", 'url': service.base_url}],#.join(reference_element),
                'category': escape(service.category.gn_description if service.category else ''),
                'contact': 'registry',
                'bbox_l': '{} {}'.format(record.bbox_y1, record.bbox_x1),
                'bbox_u': '{} {}'.format(record.bbox_y0, record.bbox_x0),
                'classification': service.classification,
                'caveat': service.caveat,
                'fees': service.fees,
                'provenance': service.provenance,
                'maintenance_frequency': service.maintenance_frequency,
                'license': service.license,
                'keywords': record.keywords,
                'title_alternate': record.typename
            })
            resp = catalogue.create_record(item)
            logger.debug(resp)
    else:
        item = Record({
                'uuid': service.uuid,
                'title': service.title.encode('ascii', 'xmlcharrefreplace'),
                'creator': service.owner.username,
                'record_type': 'dataset',
                'modified': datetime.datetime.now(),
                'typename': service.servicelayer_set.all()[0].typename,
                'date': service.date,
                'abstract': service.description.encode('ascii', 'xmlcharrefreplace') if service.description else '',
                'format': get_types(service.type),
                'base_url': service.base_url,
                'references': get_refs(service) if service.service_refs else [],
                'category': escape(service.category.gn_description if service.category else ''),
                'contact': 'registry',
                'bbox_l': '-85.0 -180',#.format(record.bbox_y1, record.bbox_x1),
                'bbox_u': '85.0 180',#.format(record.bbox_y0, record.bbox_x0),
                'classification': service.classification,
                'caveat': service.caveat,
                'fees': service.fees,
                'provenance': service.provenance,
                'maintenance_frequency': service.maintenance_frequency,
                'license': service.license,
                #'keywords': service.keywords,
                'title_alternate': service.servicelayer_set.all()[0].typename
            })
        resp = catalogue.create_record(item)
        logger.debug(resp)


@task(
    bind=True,
    max_retries=1,
)
def delete_record(self, record_id):
    """
    Remove a CSW record from CSW then the database.
    """

    record = CSWRecord.objects.get(id=record_id)
    record.status = "Pending"
    record.save()

    # Why write XML when there are strings?
    # This is a CSW delete request, it uses any filter
    # but this one specifys using the identifier.
    csw_delete = """
        <csw:Transaction xmlns:ogc="http://www.opengis.net/ogc"
                         xmlns:csw="http://www.opengis.net/cat/csw/2.0.2"
                         xmlns:ows="http://www.opengis.net/ows"
                         xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
                         xsi:schemaLocation="http://www.opengis.net/cat/csw/2.0.2 http://schemas.opengis.net/csw/2.0.2/CSW-publication.xsd"

                         xmlns:dc="http://purl.org/dc/elements/1.1/"
                         xmlns:dct="http://purl.org/dc/terms/"
                         service="CSW"
                         version="2.0.2">
          <csw:Delete>
            <csw:Constraint version="1.1.0">
              <ogc:Filter>
                <ogc:PropertyIsEqualTo>
                  <ogc:PropertyName>dc:identifier</ogc:PropertyName>
                  <ogc:Literal>{record_id}</ogc:Literal>
                </ogc:PropertyIsEqualTo>
              </ogc:Filter>
            </csw:Constraint>
          </csw:Delete>
        </csw:Transaction>
    """


    post_data = csw_delete.format(
        record_id=record_id
    )
    print post_data 

    #results = csw_post(self, record, post_data)
    #results = { 'Deleted' : 0 }

    # ensure the record is removed from CSW,
    #  if it is, then delete it.
    #if(results['Deleted'] != 1):
      #  csw_fail(self, record, "Failed to remove CSW record")
    #else:
        #record.delete()
