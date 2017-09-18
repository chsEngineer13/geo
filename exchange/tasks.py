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

    def getTypes(server_type):

        if server_type == 'ImageServer':
            layer_type = 'ESRI:ArcGIS:ImageServer'
        elif server_type == 'MapServer':
            layer_type = 'ESRI:ArcGIS:MapServer'
        elif 'WMS' in server_type:
            layer_type = 'OGC:WMS'
        else:
            layer_type = 'OGC:WMS'#server_type

        return layer_type

    catalogue = get_catalogue()
    service = Service.objects.get(pk=id)
        #catalogue.create_record(service)
    for record in service.servicelayer_set.all():
        item = Record({
            'uuid': record.uuid,
            'title': record.title.encode('ascii', 'xmlcharrefreplace'),
            'creator': record.title,
            'record_type': 'dataset',
            'modified': datetime.datetime.now(),
            'typename': record.typename,
            'date': service.date,
            'abstract': record.description.encode('ascii', 'xmlcharrefreplace'),
            'format': getTypes(service.type),
            'base_url': service.base_url,
            'references': '',#.join(reference_element),
            'category': escape(service.category.gn_description if service.category else ''),
            'contact': record.title,
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
        catalogue.create_record(item)


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
