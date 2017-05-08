import os
import re


from django.shortcuts import render, render_to_response
from django.template import RequestContext
from django.conf import settings
from geonode.layers.views import _resolve_layer, _PERMISSION_MSG_METADATA
from django.http import HttpResponseRedirect, HttpResponse, JsonResponse
from django.core.urlresolvers import reverse
from django.core.serializers import serialize
from django.contrib.admin.views.decorators import staff_member_required
from exchange.core.models import ThumbnailImage, ThumbnailImageForm, CSWRecordForm, CSWRecord
from geonode.base.models import TopicCategory
from exchange.tasks import create_new_csw, load_service_layers
from geonode.maps.views import _resolve_map
import requests
import logging

logger = logging.getLogger(__name__)


def home_screen(request):
    categories = TopicCategory.objects.filter(is_choice=True).order_by('pk')
    return render(request, 'index.html', {'categories': categories})


def documentation_page(request):
    return HttpResponseRedirect('/static/docs/index.html')


def layer_metadata_detail(request, layername,
                          template='layers/metadata_detail.html'):

    layer = _resolve_layer(request, layername, 'view_resourcebase',
                           _PERMISSION_MSG_METADATA)

    return render_to_response(template, RequestContext(request, {
        "layer": layer,
        'SITEURL': settings.SITEURL[:-1]
    }))


def map_metadata_detail(request, mapid,
                        template='maps/metadata_detail.html'):

    map_obj = _resolve_map(request, mapid, 'view_resourcebase')
    return render_to_response(template, RequestContext(request, {
        "layer": map_obj,
        "mapid": mapid,
        'SITEURL': settings.SITEURL[:-1],
    }))


def geoserver_reverse_proxy(request):
    url = settings.OGC_SERVER['default']['LOCATION'] + 'wfs/WfsDispatcher'
    data = request.body
    headers = {'Content-Type': 'application/xml',
               'Data-Type': 'xml'}

    req = requests.post(url, data=data, headers=headers,
                        cookies=request.COOKIES)
    return HttpResponse(req.content, content_type='application/xml')


@staff_member_required
def insert_csw(request):
    if request.method == 'POST':
        form = CSWRecordForm(request.POST)
        if form.is_valid():
            new_record = form.save()
            new_record.user = request.user
            new_record.save()
            create_new_csw.delay(new_record.id)
            return HttpResponseRedirect(reverse('csw_status'))
    else:
        form = CSWRecordForm()

    return render_to_response("csw/new.html",
                              {"form": form,
                               },
                              context_instance=RequestContext(request))


@staff_member_required
def csw_arcgis_search(request):
    default_response = HttpResponse(status=404)
    if request.method == 'GET':
        return default_response
    elif request.method == 'POST':
        url = request.POST.get("url", None)
        if url and request.user.is_superuser:
            load_service_layers.delay(url + '/arcgis/rest/services/', request.user.id)
            return HttpResponse(status=201)
        else:
            return default_response


@staff_member_required
def csw_status(request):
    format = request.GET.get('format', "")
    records = CSWRecord.objects.filter(user=request.user)
    if records.count() == 0:
        records=[]

    if format.lower() == 'json':
        return HttpResponse(serialize('json', records),
                            content_type="application/json")
    else:
        return render_to_response("csw/status.html",
                                  context_instance=RequestContext(request))


@staff_member_required
def csw_status_table(request):
    records = CSWRecord.objects.filter(user=request.user)

    return render_to_response("csw/status_fill.html",
                              {
                                  "records": records,
                               },
                              context_instance=RequestContext(request))

# Reformat objects for use in the results.
#
# The ES objects need some reformatting in order to be useful
# for output to the client.
#
def get_unified_search_result_objects(hits):
    objects = []
    for hit in hits:
        try:
            source = hit.get('_source')
        except:  # No source
            pass
        result = {}
        result['index'] = hit.get('_index', None)
        for key, value in source.iteritems():
            if key == 'bbox':
                result['bbox_left'] = value[0]
                result['bbox_bottom'] = value[1]
                result['bbox_right'] = value[2]
                result['bbox_top'] = value[3]
                bbox_str = ','.join(map(str,value))
            elif key == 'links':
                # Get source link from Registry
                xml = value['xml']
                js = '%s/%s' % (settings.REGISTRYURL,
                                re.sub(r"xml$", "js", xml))
                png = '%s/%s' % (settings.REGISTRYURL,
                                value['png'])
                result['registry_url'] = js
                result['thumbnail_url'] = png

            else:
                result[key] = source.get(key, None)
        objects.append(result)

    return objects


def unified_elastic_search(request, resourcetype='base'):
    import requests
    from elasticsearch import Elasticsearch
    from six import iteritems
    from guardian.shortcuts import get_objects_for_user

    # elasticsearch_dsl overwrites any double underscores with a .
    # this changes the default to not overwrite
    import elasticsearch_dsl as edsl

    def newDSLBaseInit(self, _expand__to_dot=False, **params):
        self._params = {}
        for pname, pvalue in iteritems(params):
            if '__' in pname and _expand__to_dot:
                pname = pname.replace('__', '.')
            self._setattr(pname, pvalue)
    edsl.utils.DslBase.__init__ = newDSLBaseInit
    Search = edsl.Search
    Q = edsl.query.Q

    parameters = request.GET
    es = Elasticsearch(settings.ES_URL)
    search = Search(using=es)

    # Set base fields to search
    fields = ['title', 'text', 'abstract', 'title_alternate']
    facets = ['_index', 'type', 'subtype',
              'owner__username', 'keywords', 'regions', 'category', 'has_time']

    # Text search
    query = parameters.get('q', None)

    offset = int(parameters.get('offset', '0'))
    limit = int(parameters.get('limit', settings.API_LIMIT_PER_PAGE))

    # Make sure Category search works with either category__in or category__identifier__in
    categories = parameters.getlist('category__in',
                                    parameters.getlist('category__identifier__in', None))

    keywords = parameters.getlist('keywords__in',
                                  parameters.getlist('keywords__slug__in', None))

    # Publication date range (start,end)
    date_range = parameters.get("date__range", None)
    date_end = parameters.get("date__lte", None)
    date_start = parameters.get("date__gte", None)
    if date_range is not None:
        dr = date_range.split(',')
        date_start = dr[0]
        date_end = dr[1]

    # Time Extent range (start, end)
    extent_range = parameters.get("extent__range", None)
    extent_end = parameters.get("extent__lte", None)
    extent_start = parameters.get("extent__gte", None)
    if extent_range is not None:
        er = extent_range.split(',')
        extent_start = er[0]
        extent_end = er[1]

    # Sort order
    sort = parameters.get("order_by", "relevance")

    # Geospatial Elements
    bbox = parameters.get("extent", None)

    # filter by resource type if included by path
    logger.debug('-------------------------------------------------------------')
    logger.debug('>>>>>>>>> Filtering by Resource Type %s <<<<<<<<<<<<<' % resourcetype)
    logger.debug('-------------------------------------------------------------')

    if resourcetype == 'documents':
        search = search.query("match", type_exact="document")
    elif resourcetype == 'layers':
        search = search.query("match", type_exact="layer")
    elif resourcetype == 'maps':
        search = search.query("match", type_exact="map")

    # Filter geonode layers by permissions
    if not settings.SKIP_PERMS_FILTER:
        # Get the list of objects the user has access to
        filter_set = get_objects_for_user(
            request.user, 'base.view_resourcebase')
        if settings.RESOURCE_PUBLISHING:
            filter_set = filter_set.filter(is_published=True)

        filter_set_ids = map(str, filter_set.values_list('id', flat=True))
        # Do the query using the filterset and the query term. Facet the
        # results
        q = Q({"match": {"_type": "layer"}})
        if len(filter_set_ids) > 0:
            q = Q({"terms": {"id": filter_set_ids}}) | q

        search = search.query(q)

    # Filter by Query Params
    if query:
        if query.startswith('"') or query.startswith('\''):
            # Match exact phrase
            phrase = query.replace('"', '')
            search = search.query(
                "multi_match", type='phrase_prefix', query=phrase, fields=fields)
        else:
            words = [
                w for w in re.split(
                    '\W',
                    query,
                    flags=re.UNICODE) if w]
            for i, search_word in enumerate(words):
                if i == 0:
                    word_query = Q(
                        "multi_match", type='phrase_prefix', query=search_word, fields=fields)
                elif search_word.upper() in ["AND", "OR"]:
                    pass
                elif words[i - 1].upper() == "OR":
                    word_query = word_query | Q(
                        "multi_match", type='phrase_prefix', query=search_word, fields=fields)
                else:  # previous word AND this word
                    word_query = word_query & Q(
                        "multi_match", type='phrase_prefix', query=search_word, fields=fields)
            # logger.debug('******* WORD_QUERY %s', word_query.to_dict())
            search = search.query(word_query)

    if bbox:
        left, bottom, right, top = bbox.split(',')
        leftq = Q({'range': {'bbox_left': {'gte': left}}}) | Q(
            {'range': {'min_x': {'gte': left}}})
        bottomq = Q({'range': {'bbox_bottom': {'gte': bottom}}}) | Q(
            {'range': {'min_y': {'gte': bottom}}})
        rightq = Q({'range': {'bbox_right': {'lte': right}}}) | Q(
            {'range': {'max_x': {'lte': right}}})
        topq = Q({'range': {'bbox_top': {'lte': top}}}) | Q(
            {'range': {'max_y': {'lte': top}}})
        q = leftq & bottomq & rightq & topq
        search = search.query(q)

    # filter by date
    if date_start:
        q = Q({'range': {'date': {'gte': date_start}}}) | Q(
            {'range': {'layer_date': {'gte': date_start}}})
        search = search.query(q)

    if date_end:
        q = Q({'range': {'date': {'lte': date_end}}}) | Q(
            {'range': {'layer_date': {'lte': date_end}}})
        search = search.query(q)

    if extent_start:
        q = Q(
                {'range': {'temporal_extent_end': {'gte': extent_start}}}
            )
        search = search.query(q)

    if extent_end:
        q = Q(
                {'range': {'temporal_extent_start': {'lte': extent_end}}}
            )
        search = search.query(q)

    if categories:
        q = Q({'terms': {'category_exact': categories}})
        search = search.query(q)

    if keywords:
        q = Q({'terms': {'keywords_exact': keywords}})
        search = search.query(q)

    def facet_search(search, parameters, paramfield, esfield=None):
        if esfield is None:
            esfield = paramfield.replace('__in', '')
        if esfield != '_index':
            esfield = esfield + '_exact'
        getparams = parameters.getlist(paramfield)
        if not getparams:
            getparams = parameters.getlist(paramfield.replace('__in',''))

        if getparams:
            q = Q({'terms': {esfield: getparams}})
            if esfield == 'type_exact':
                q = q | Q({'terms': {'subtype_exact': getparams}})
            return search.query(q)
        return search

    # Setup aggregations and filters for faceting
    for f in facets:
        param = '%s__in' % f
        if f not in ['category', 'keywords']:
            search = facet_search(search, parameters, param)
        search.aggs.bucket(f, 'terms', field=f + '_exact')

    # Apply sort
    if sort.lower() == "-date":
        search = search.sort({"date":
                              {"order": "desc",
                               "missing": "_last",
                               "unmapped_type": "date"
                               }},
                             {"layer_date":
                              {"order": "desc",
                               "missing": "_last",
                               "unmapped_type": "date"}})
    elif sort.lower() == "date":
        search = search.sort({"date":
                              {"order": "asc",
                               "missing": "_last",
                               "unmapped_type": "date"
                               }},
                             {"layer_date":
                              {"order": "asc",
                               "missing": "_last",
                               "unmapped_type": "date"}})
    elif sort.lower() == "title":
        search = search.sort('title')
    elif sort.lower() == "-title":
        search = search.sort('-title')
    elif sort.lower() == "-popular_count":
        search = search.sort('-popular_count')
    else:
        search = search.sort({"date":
                              {"order": "desc",
                               "missing": "_last",
                               "unmapped_type": "date"
                               }},
                             {"layer_date":
                              {"order": "desc",
                               "missing": "_last",
                               "unmapped_type": "date"}})

    # print search.to_dict()
    search = search[offset:offset + limit]
    results = search.execute()

    # Get facet counts
    facet_results = {}
    for f in facets:
        facet_results[f] = {}
        for bucket in results.aggregations[f].buckets:
            facet_results[f][bucket.key] = bucket.doc_count
    # create alias for owners
    facet_results['owners']=facet_results['owner__username']
    # Get results
    objects = get_unified_search_result_objects(results.hits.hits)

    object_list = {
        "meta": {
            "limit": limit,
            "next": None,
            "offset": offset,
            "previous": None,
            "total_count": results.hits.total,
            "facets": facet_results,
        },
        "objects": objects,
    }

    return JsonResponse(object_list)

def empty_page(request):
    return HttpResponse('')
        
