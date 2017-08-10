from urlparse import urljoin
from celery.task import task
from celery.utils.log import get_task_logger
from django.conf import settings
import requests
from lxml import etree
import arcrest
from exchange.core.utils import process_service
from exchange.core.models import CSWRecord
from django.contrib.auth import get_user_model
from xml.sax.saxutils import escape

import time

logger = get_task_logger(__name__)


class UpstreamServiceImpairment(Exception):
    pass


@task
def load_service_layers(url, user_id):
    folder = arcrest.Folder(url)

    services = []

    for item in folder.folders:
        for s in item.services:
            if hasattr(s, 'MapServer') or hasattr(s, 'ImageServer'):
                    services.append(s)

    logger.info('Found {} services to process!'.format(str(len(services))))

    for i, service in enumerate(services):
        if i % 5 == 0:
            logger.info('Service Processing will sleep for 30 seconds.')
            time.sleep(30)
        data = process_service(service)
        if data is not None:
            for j, layer in enumerate(data['layers']):
                if j % 5 == 0:
                    logger.info('Layer Processing will sleep for 30 seconds.')
                    time.sleep(30)
                try:
                    user = get_user_model().objects.get(id=user_id)
                    record = CSWRecord()
                    record.user = user
                    record.id = layer['identifier']
                    record.title = layer['title']
                    record.record_type = layer['type']
                    record.source = layer['source']
                    record.creator = layer['creator']
                    record.abstract = layer['abstract']
                    record.relation = data['name']
                    record.alternative = layer['title_alternate']
                    record.contact_information = user.email
                    record.status = 'Incomplete'
                    record.bbox_upper_corner = '{0} {1}'.format(str(layer['ymin']), str(layer['xmin']))
                    record.bbox_lower_corner = '{0} {1}'.format(str(layer['ymax']), str(layer['xmax']))
                    record.save()
                except Exception, e:
                    logger.error(e)


# Raise when there is a failure in the CSW
#  operation, flag the record as having an error,
#  with the error message and then retry.
def csw_fail(self, record, message):
    record.status = "Error"
    record.status_message = message
    record.save()
    logger.error(message)
    error = UpstreamServiceImpairment(message)
    raise self.retry(exc=error)

# Execute a CSW operation
#
def csw_post(self, record, post_data):
    namespaces = {
        "csw": "http://www.opengis.net/cat/csw/2.0.2",
        "dc": "http://purl.org/dc/elements/1.1/",
        "ows": "http://www.opengis.net/ows",
    }

    registry_url = settings.REGISTRY_LOCAL_URL
    catalog = settings.REGISTRY_CAT
    csw_url = urljoin(registry_url, "catalog/{}/csw".format(catalog))
    response = requests.post(csw_url, data=post_data)

    if response.status_code != 200:
        message = "{} during CSW record creation: {}".format(
            response.status_code,
            response.content,
        )
        return csw_fail(self, record, message)

    try:
        parsed = etree.fromstring(response.content)
    except (ValueError, etree.XMLSyntaxError):
        return csw_fail(self, record, "Error while parsing response from registry")

    exceptiontext = parsed.xpath("//ows:ExceptionText", namespaces=namespaces)

    if exceptiontext:
        # we're going to consider this an "error" even if registry returns a
        # positive TransactionSummary/totalInserted value along with the error
        return csw_fail(self, record, "Error(s) during record creation" + ", ".join(
            x.text for x in exceptiontext
        ))

    keys = ['Inserted', 'Updated', 'Deleted']

    results = {}
    for key in keys:
        total_key = '//csw:total'+key
        total = parsed.xpath(total_key, namespaces=namespaces)

        # default the count to 0
        results[key] = 0
        if total and len(total) > 0:
            results[key] = int(total[0].text)

    return results


# Insert/Update CSW Record to registry.
#
def csw_write(self, record_id, operation):
    """
    Attempt to create a new CSW record in Registry
    """

    record = CSWRecord.objects.get(id=record_id)
    record.status = "Pending"
    record.save()

    csw_record_template = """
        <csw:Transaction xmlns:csw="http://www.opengis.net/cat/csw/2.0.2"
        xmlns:ows="http://www.opengis.net/ows"
        xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
        xsi:schemaLocation="http://www.opengis.net/cat/csw/2.0.2
        http://schemas.opengis.net/csw/3.0.0/CSW-publication.xsd"
        service="CSW" version="2.0.2"
        xmlns:dc="http://purl.org/dc/elements/1.1/"
        xmlns:dct="http://purl.org/dc/terms/"
        xmlns:registry="http://gis.harvard.edu/HHypermap/registry/0.1" >
        <csw:{operation}>

            <csw:Record xmlns:registry="http://gis.harvard.edu/HHypermap/registry/0.1">
            <dc:identifier>{uuid}</dc:identifier>
            <dc:title>{title}</dc:title>
            <dc:creator>{creator}</dc:creator>
            <dc:type>{record_type}</dc:type>
            <dct:alternative>{alternative}</dct:alternative>
            <dct:modified>{modified}</dct:modified>
            <dct:abstract>{abstract}</dct:abstract>
            <dc:format>{record_format}</dc:format>
            <dc:source>{source}</dc:source>
            <dc:relation>{relation}</dc:relation>
            <dc:gold>{gold}</dc:gold>
            {references}
            <registry:property name="category" value="{category}"/>
            <registry:property
            name="ContactInformation/Primary/organization"
            value="{contact}" />
            <ows:BoundingBox
            crs="http://www.opengis.net/def/crs/EPSG/0/4326"
            dimensions="2">
                <ows:LowerCorner>{bbox_l}</ows:LowerCorner>
                <ows:UpperCorner>{bbox_u}</ows:UpperCorner>
            </ows:BoundingBox>
            </csw:Record>

        </csw:{operation}>
        </csw:Transaction>"""

    csw_record_reference_template = """<dct:references scheme="{scheme}">{url}</dct:references>"""

    reference_element = []
    for reference in record.references.all():
        reference_element.append(csw_record_reference_template.format(scheme=reference.scheme, url=escape(reference.url)))

    post_data = csw_record_template.format(
        operation=operation,
        uuid=record_id,
        title=record.title.encode('ascii', 'xmlcharrefreplace'),
        creator=record.creator,
        record_type=record.record_type,
        alternative=record.alternative,
        modified=record.modified,
        abstract=record.abstract.encode('ascii', 'xmlcharrefreplace'),
        record_format=record.record_format,
        source=record.source,
        references=''.join(reference_element),
        relation=record.relation,
        gold=record.gold,
        category=record.topic_category.gn_description,
        contact=record.contact_information,
        bbox_l=record.bbox_lower_corner,
        bbox_u=record.bbox_upper_corner,
    )


    results = csw_post(self, record, post_data)

    past_tense = {
        'Insert' : 'Inserted',
        'Update' : 'Updated'
    }

    if(results[past_tense[operation]] > 0):
        record.status = "Complete"
        record.status_message = results[past_tense[operation]]
        record.save()
        #logger.info("Record successfully created/changed: {}".format(response.content))
        return
    else:
        # Fell through, no totalinserted or it was 0
        csw_fail(self, record, "No record created or updated, but no error reported ")

@task(
    bind=True,
    max_retries=1,
)
def create_new_csw(self, record_id):
    csw_write(self, record_id, 'Insert')

@task(
    bind=True,
    max_retries=1,
)
def update_csw(self, record_id):
    csw_write(self, record_id, 'Update')

@task(
    bind=True,
    max_retries=1,
)
def delete_csw(self, record_id):
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

    results = csw_post(self, record, post_data)
    #results = { 'Deleted' : 0 }

    # ensure the record is removed from CSW,
    #  if it is, then delete it.
    if(results['Deleted'] != 1):
        csw_fail(self, record, "Failed to remove CSW record")
    else:
        record.delete()
