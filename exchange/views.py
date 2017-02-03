import os

from django.shortcuts import render, render_to_response
from django.template import RequestContext
from django.conf import settings
from geonode.layers.views import _resolve_layer, _PERMISSION_MSG_METADATA
from django.http import HttpResponseRedirect, HttpResponse, JsonResponse
from django.core.urlresolvers import reverse
from django.core.serializers import serialize
from exchange.core.models import ThumbnailImage, ThumbnailImageForm, CSWRecordForm, CSWRecord
from exchange.tasks import create_new_csw
from geonode.maps.views import _resolve_map
import requests
import logging

logger = logging.getLogger(__name__)


def home_screen(request):
    return render(request, 'index.html')


def documentation_page(request):
    return HttpResponseRedirect('/static/docs/index.html')


def layer_metadata_detail(request, layername,
                          template='layers/metadata_detail.html'):

    layer = _resolve_layer(request, layername, 'view_resourcebase',
                           _PERMISSION_MSG_METADATA)

    thumbnail_dir = os.path.join(settings.MEDIA_ROOT, 'thumbs')
    default_thumbnail_array = layer.get_thumbnail_url().split('/')
    default_thumbnail_name = default_thumbnail_array[
        len(default_thumbnail_array) - 1
    ]
    default_thumbnail = os.path.join(thumbnail_dir, default_thumbnail_name)

    if request.method == 'POST':
        thumb_form = ThumbnailImageForm(request.POST, request.FILES)
        if thumb_form.is_valid():
            new_img = ThumbnailImage(
                thumbnail_image=request.FILES['thumbnail_image']
            )
            new_img.save()
            user_upload_thumbnail = ThumbnailImage.objects.all()[0]
            user_upload_thumbnail_filepath = str(
                user_upload_thumbnail.thumbnail_image
            )

            # only create backup for original thumbnail
            if os.path.isfile(default_thumbnail + '.bak') is False:
                os.rename(default_thumbnail, default_thumbnail + '.bak')

            os.rename(user_upload_thumbnail_filepath, default_thumbnail)

            return HttpResponseRedirect(
                reverse('layer_metadata_detail', args=[layername])
            )
    else:
        thumb_form = ThumbnailImageForm()

    thumbnail = layer.get_thumbnail_url
    return render_to_response(template, RequestContext(request, {
        "layer": layer,
        'SITEURL': settings.SITEURL[:-1],
        "thumbnail": thumbnail,
        "thumb_form": thumb_form
    }))


def map_metadata_detail(request, mapid,
                        template='maps/metadata_detail.html'):

    map_obj = _resolve_map(request, mapid, 'view_resourcebase')

    thumbnail_dir = os.path.join(settings.MEDIA_ROOT, 'thumbs')
    default_thumbnail_array = map_obj.get_thumbnail_url().split('/')
    default_thumbnail_name = default_thumbnail_array[
        len(default_thumbnail_array) - 1
    ]
    default_thumbnail = os.path.join(thumbnail_dir, default_thumbnail_name)

    if request.method == 'POST':
        thumb_form = ThumbnailImageForm(request.POST, request.FILES)
        if thumb_form.is_valid():
            new_img = ThumbnailImage(
                thumbnail_image=request.FILES['thumbnail_image']
            )
            new_img.save()
            user_upload_thumbnail = ThumbnailImage.objects.all()[0]
            user_upload_thumbnail_filepath = str(
                user_upload_thumbnail.thumbnail_image
            )

            # only create backup for original thumbnail
            if os.path.isfile(default_thumbnail + '.bak') is False:
                os.rename(default_thumbnail, default_thumbnail + '.bak')

            os.rename(user_upload_thumbnail_filepath, default_thumbnail)

            return HttpResponseRedirect(
                reverse('map_metadata_detail', args=[mapid])
            )
    else:
        thumb_form = ThumbnailImageForm()

    thumbnail = map_obj.get_thumbnail_url
    return render_to_response(template, RequestContext(request, {
        "layer": map_obj,
        "mapid": mapid,
        'SITEURL': settings.SITEURL[:-1],
        "thumbnail": thumbnail,
        "thumb_form": thumb_form
    }))


def geoserver_reverse_proxy(request):
    url = settings.OGC_SERVER['default']['LOCATION'] + 'wfs/WfsDispatcher'
    data = request.body
    headers = {'Content-Type': 'application/xml',
               'Data-Type': 'xml'}

    req = requests.post(url, data=data, headers=headers,
                        cookies=request.COOKIES)
    return HttpResponse(req.content, content_type='application/xml')


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


def csw_status(request):
    format = request.GET.get('format', "")
    records = CSWRecord.objects.filter(user=request.user)

    if format.lower() == 'json':
        return HttpResponse(serialize('json', records),
                            content_type="application/json")
    else:
        return render_to_response("csw/status.html",
                                  context_instance=RequestContext(request))


def csw_status_table(request):
    records = CSWRecord.objects.filter(user=request.user)

    return render_to_response("csw/status_fill.html",
                              {
                                  "records": records,
                               },
                              context_instance=RequestContext(request))


def unified_elastic_search(request):
    import re
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
              'owner__username', 'keywords', 'regions', 'category']

    # Text search
    query = parameters.get('q', None)

    offset = int(parameters.get('offset', '0'))
    limit = int(parameters.get('limit', settings.API_LIMIT_PER_PAGE))

    # Publication date range (start,end)
    date_end = parameters.get("date__lte", None)
    date_start = parameters.get("date__gte", None)

    # Sort order
    sort = parameters.get("order_by", "relevance")

    # Geospatial Elements
    bbox = parameters.get("extent", None)

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
                "multi_match", type='phrase', query=phrase, fields=fields)
        else:
            words = [
                w for w in re.split(
                    '\W',
                    query,
                    flags=re.UNICODE) if w]
            for i, search_word in enumerate(words):
                if i == 0:
                    word_query = Q(
                        "multi_match", query=search_word, fields=fields)
                elif search_word.upper() in ["AND", "OR"]:
                    pass
                elif words[i - 1].upper() == "OR":
                    word_query = word_query | Q(
                        "multi_match", query=search_word, fields=fields)
                else:  # previous word AND this word
                    word_query = word_query & Q(
                        "multi_match", query=search_word, fields=fields)
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

    def facet_search(search, parameters, paramfield, esfield=None):
        if esfield is None:
            esfield = paramfield.replace('__in', '')
        getparams = parameters.getlist(paramfield)
        if getparams:
            q = Q({'terms': {esfield: getparams}})
            return search.query(q)
        return search

    # Setup aggregations and filters for faceting
    for f in facets:
        param = '%s__in' % f
        search = facet_search(search, parameters, param)
        search.aggs.bucket(f, 'terms', field=f)

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

    # Get results
    objects = []

    for hit in results.hits.hits:
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
