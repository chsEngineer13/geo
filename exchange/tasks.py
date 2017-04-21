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


@task(
    bind=True,
    max_retries=1,
)
def create_new_csw(self, record_id):
    """
    Attempt to create a new CSW record in Registry
    """

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
        <csw:Insert>

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

        </csw:Insert>
        </csw:Transaction>"""

    namespaces = {
        "csw": "http://www.opengis.net/cat/csw/2.0.2",
        "dc": "http://purl.org/dc/elements/1.1/",
        "ows": "http://www.opengis.net/ows",
    }

    record = CSWRecord.objects.get(id=record_id)
    record.status = "Pending"
    record.save()

    def fail(message):
        record.status = "Error"
        record.save()
        logger.error(message)
        error = UpstreamServiceImpairment(message)
        raise self.retry(exc=error)

    registry_url = settings.REGISTRY_LOCAL_URL
    catalog = settings.REGISTRY_CAT
    csw_url = urljoin(registry_url, "catalog/{}/csw".format(catalog))
    post_data = csw_record_template.format(
        uuid=record_id,
        title=record.title,
        creator=record.creator,
        record_type=record.record_type,
        alternative=record.alternative,
        modified=record.modified,
        abstract=record.abstract,
        record_format=record.record_format,
        source=record.source,
        relation=record.relation,
        gold=record.gold,
        category=record.category,
        contact=record.contact_information,
        bbox_l=record.bbox_lower_corner,
        bbox_u=record.bbox_upper_corner,
    )

    logger.info("Creating new CSW with: \n{}".format(post_data))
    response = requests.post(csw_url, data=post_data)

    if response.status_code != 200:
        message = "{} during CSW record creation: {}".format(
            response.status_code,
            response.content,
        )
        return fail(message)

    try:
        parsed = etree.fromstring(response.content)
    except (ValueError, etree.XMLSyntaxError):
        return fail("Error while parsing response from registry")

    exceptiontext = parsed.xpath("//ows:ExceptionText", namespaces=namespaces)
    totalinserted = parsed.xpath("//csw:totalInserted", namespaces=namespaces)

    if exceptiontext:
        # we're going to consider this an "error" even if registry returns a
        # positive TransactionSummary/totalInserted value along with the error
        return fail("Error(s) during record creation" + ", ".join(
            x.text for x in exceptiontext
        ))

    elif not totalinserted or len(totalinserted) != 1:
        return fail("response XML did not contain one //csw:totalInserted")

    elif int(totalinserted[0].text) > 0:
        record.status = "Complete"
        record.save()
        logger.info("Record successfully created: {}".format(response.content))
        return

    # Fell through, no totalinserted or it was 0
    fail("No record created but no error reported")
