import os
import re
import urllib
import json
import requests
import logging
import datetime
from geonode.base.models import TopicCategory
from django.conf import settings
from django.core.urlresolvers import reverse, reverse_lazy
from django.core.serializers import serialize
from django.contrib.admin.views.decorators import staff_member_required
from django.db import transaction
from django.shortcuts import render, render_to_response, redirect
from django.template import RequestContext
from django.http import HttpResponseRedirect, HttpResponse, JsonResponse
from django.views.generic import CreateView, UpdateView, ListView
from exchange.core.models import ThumbnailImage, ThumbnailImageForm, CSWRecord, CSWRecordReference
from exchange.core.forms import CSWRecordReferenceFormSet, CSWRecordReferenceForm, CSWRecordForm
from exchange.version import get_version
from exchange.tasks import create_new_csw, update_csw, delete_csw, load_service_layers, write_xml
from geonode.maps.views import _resolve_map
from geonode.layers.views import _resolve_layer, _PERMISSION_MSG_METADATA
from geonode.base.models import TopicCategory
from pip._vendor import pkg_resources
from six import iteritems

logger = logging.getLogger(__name__)


def home_screen(request):
    categories = TopicCategory.objects.filter(is_choice=True).order_by('pk')
    return render(request, 'index.html', {'categories': categories})


def documentation_page(request):
    return HttpResponseRedirect('/static/docs/index.html')


def get_pip_version(project):
    version = [
        p.version for p in pkg_resources.working_set
        if p.project_name == project
    ]
    if version != []:
        pkg_version = version[0][:-8] if version[0][:-8] else version[0][-7:]
        commit_hash = version[0][-7:] if version[0][:-8] else version[0][:-8]
        return {'version': pkg_version, 'commit': commit_hash}
    else:
        return {'version': '', 'commit': ''}


def about_page(request, template='about.html'):
    exchange_version = get_pip_version('geonode-exchange')
    if not exchange_version['version'].strip():
        version = get_version()
        pkg_version = version[:-8] if version[:-8] else version[-7:]
        commit_hash = version[-7:] if version[:-8] else version[:-8]
        exchange_version = {'version': pkg_version, 'commit': commit_hash}
    try:
        exchange_releases = requests.get(
            'https://api.github.com/repos/boundlessgeo/exchange/releases'
        ).json()
    except:
        exchange_releases = []
    release_notes = 'No release notes available.'
    for release in exchange_releases:
        if release['tag_name'] == 'v{}'.format(exchange_version['version']):
            release_notes = release['body'].replace(' - ', '\n-')

    try:
        ogc_server = settings.OGC_SERVER['default']
        geoserver_url = '{}/rest/about/version.json'.format(ogc_server['LOCATION'].strip('/'))
        resp = requests.get(geoserver_url, auth=(ogc_server['USER'], ogc_server['PASSWORD']))
        version = resp.json()['about']['resource'][0]
        geoserver_version = {'version': version['Version'], 'commit': version['Git-Revision'][:7]}
    except:
        geoserver_version = {'version': '', 'commit': ''}

    geonode_version = get_pip_version('GeoNode')
    maploom_version = get_pip_version('django-exchange-maploom')
    importer_version = get_pip_version('django-osgeo-importer')
    react_version = get_pip_version('django-geonode-client')

    projects = [{
        'name': 'Boundless Exchange',
        'website': 'https://boundlessgeo.com/boundless-exchange/',
        'repo': 'https://github.com/boundlessgeo/exchange',
        'version': exchange_version['version'],
        'commit': exchange_version['commit']
    }, {
        'name': 'GeoNode',
        'website': 'http://geonode.org/',
        'repo': 'https://github.com/GeoNode/geonode',
        'boundless_repo': 'https://github.com/boundlessgeo/geonode',
        'version': geonode_version['version'],
        'commit': geonode_version['commit']
    }, {
        'name': 'GeoServer',
        'website': 'http://geoserver.org/',
        'repo': 'https://github.com/geoserver/geoserver',
        'boundless_repo': 'https://github.com/boundlessgeo/geoserver',
        'version': geoserver_version['version'],
        'commit': geoserver_version['commit']
    }, {
        'name': 'MapLoom',
        'website': 'http://prominentedge.com/projects/maploom.html',
        'repo': 'https://github.com/ROGUE-JCTD/MapLoom',
        'boundless_repo': 'https://github.com/boundlessgeo/'
                          + 'django-exchange-maploom',
        'version': maploom_version['version'],
        'commit': maploom_version['commit']
    }, {
        'name': 'OSGeo Importer',
        'repo': 'https://github.com/GeoNode/django-osgeo-importer',
        'version': importer_version['version'],
        'commit': importer_version['commit']
    }, {
        'name': 'React Viewer',
        'website': 'http://client.geonode.org',
        'repo': 'https://github.com/GeoNode/geonode-client',
        'version': react_version['version'],
        'commit': react_version['commit']
    }]

    return render_to_response(template, RequestContext(request, {
        'projects': projects,
        'exchange_version': exchange_version['version'],
        'exchange_release': release_notes
    }))


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


def csw_arcgis_search(request):
    default_response = HttpResponse(status=404)
    if request.method == 'GET':
        return default_response
    elif request.method == 'POST':
        url = request.POST.get("url", None)
        if url:
            response = urllib.urlopen(url + '?f=pjson')
            data = json.loads(response.read())
            return JsonResponse(data)
        else:
            return default_response


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
        registry_url = settings.REGISTRYURL.rstrip('/')
        for key, value in source.iteritems():
            if key == 'bbox':
                result['bbox_left'] = value[0]
                result['bbox_bottom'] = value[1]
                result['bbox_right'] = value[2]
                result['bbox_top'] = value[3]
                bbox_str = ','.join(map(str, value))
            elif key == 'links':
                # Get source link from Registry
                xml = value['xml']
                js = '%s/%s' % (registry_url,
                                re.sub(r"xml$", "js", xml))
                png = '%s/%s' % (registry_url,
                                 value['png'])
                result['registry_url'] = js
                result['thumbnail_url'] = png

            else:
                result[key] = source.get(key, None)
        objects.append(result)

    return objects

# Function returns a generator searching recursively for a key in a dict
def gen_dict_extract(key, var):
    if hasattr(var,'iteritems'):
        for k, v in var.iteritems():
            if k == key:
                yield v
            if isinstance(v, dict):
                for result in gen_dict_extract(key, v):
                    yield result
            elif isinstance(v, list):
                for d in v:
                    for result in gen_dict_extract(key, d):
                        yield result

# Checks if key is present in dictionary
def key_exists(key, var):
    return any(True for _ in gen_dict_extract(key, var))

def unified_elastic_search(request, resourcetype='base'):
    import requests
    import collections
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
    mappings = es.indices.get_mapping()

    # Set base fields to search
    fields = ['title', 'text', 'abstract', 'title_alternate']



    # This configuration controls what fields will be added to faceted search
    # there is some special exception code later that combines the subtype search
    # and facet with type
    facet_fields = ['type', 'subtype',
              'owner__username', 'keywords', 'regions', 
              'category', 'source_host', 'classification']
    
    categories = TopicCategory.objects.all()
    category_lookup = {}
    for c in categories:
        category_lookup[c.identifier] = {
            'display': c.description,
            'icon': c.fa_class
        }

    facet_lookups = {
        'category': category_lookup,
        'type': {
            'OGC:WMS': {'display': 'ESRI MapServer'},
            'OGC:WFS': {'display': 'ESRI MapServer'},
            'OGC:WCS': {'display': 'ESRI MapServer'},
            'ESRI:ArcGIS:MapServer': {'display': 'ArcGIS MapServer'},
            'ESRI:ArcGIS:ImageServer': {'display': 'ArcGIS ImageServer'}
        }
    }

    # Allows settings that can be used by a client for display of the facets
    # 'open' is used by exchange client side to determine if a facet menu shows
    # up open or closed by default
    default_facet_settings = {'open': False, 'show': True}
    facet_settings = {
        'category': {'open': True},
        'source_host': {'open': False, 'display': 'Host'},
        'owner__username': {'open': True, 'display': 'Owner'},
        'type': {'open': True, 'display': 'Type'},
        'keywords': {'show': True},
        'regions': {'show': False},
        'classification': {'open': False, 'display': 'Classification'}
    }

    
    # This configuration controls what fields will be searchable by range
    range_fields = ['extent', 'date']

    search_fields = []

    # Get paging parameters
    offset = int(parameters.get('offset', '0'))
    limit = int(parameters.get('limit', settings.API_LIMIT_PER_PAGE))


    # Text search
    query = parameters.get('q', None)

    offset = int(parameters.get('offset', '0'))
    limit = int(parameters.get('limit', settings.API_LIMIT_PER_PAGE))

    # Sort order
    sort = parameters.get("order_by", "relevance")

    # Geospatial Elements
    bbox = parameters.get("extent", None)

    # get has_time element not used with facets
    has_time = parameters.get("has_time", None)

    # get max number of facets to return
    nfacets = parameters.get("nfacets", 15)

    # Build base query
    # The base query only includes filters relevant to what the user 
    # is allowed to see and the overall types of documents to search.
    # This provides the overall counts and all fields for faceting

    # only show registry, documents, layers, stories, and maps
    q = Q({"match": {"_type": "layer"}}) | Q(
          {"match": {"type_exact": "layer"}}) | Q(
          {"match": {"type_exact": "story"}}) | Q(
          {"match": {"type_exact": "document"}}) | Q(
          {"match": {"type_exact": "map"}})
    search = search.query(q)

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

    # Checks first if there is an [fieldname]_exact field and returns that 
    # otherwise checks if [fieldname] is present
    # if neither returns None
    def field_name(field, mappings):
        field_exact = '%s_exact' % field
        if key_exists(field_exact, mappings):
            return field_exact
        elif key_exists(field, mappings):
            return field
        else:
            return None

    # Add facets to search
    # add filters to facet_filters to be used *after* initial overall search
    valid_facet_fields = [];
    facet_filters = []
    for f in facet_fields:
        fn = field_name(f, mappings)
        if fn:
            valid_facet_fields.append(f)
            search.aggs.bucket(f, 'terms', field=fn, order={"_count": "desc"}, size=nfacets)
            # if there is a filter set in the parameters for this facet
            # add to the filters
            fp = parameters.getlist(f)
            if not fp:
                fp = parameters.getlist("%s__in"%(f))
            if fp:
                fq = Q({'terms': {fn: fp}})
                if fn == 'type_exact': # search across both type_exact and subtype
                    fq = fq | Q({'terms': {'subtype_exact': fp}})
                facet_filters.append(fq)
    
    # run search only filtered by what a particular user is able to see
    # this makes sure to get every item that is possible in the facets
    # in order for a UI to build the choices
    overall_results = search[0:0].execute()

    # build up facets dict which contains all the options for a facet along
    # with overall count and any display name or icon that should be used in UI
    aggregations = overall_results.aggregations
    facet_results = {}
    for k in aggregations:
        buckets = aggregations[k]['buckets']
        if len(buckets)>0:
            lookup = None
            if k in facet_lookups:
                lookup = facet_lookups[k]
            fsettings = default_facet_settings.copy()
            fsettings['display'] = k
            # Default display to the id of the facet in case none is set
            if k in facet_settings:
                fsettings.update(facet_settings[k])
            if parameters.getlist(k): # Make sure list starts open when a filter is set
                fsettings['open'] = True
            facet_results[k] = {'settings': fsettings, 'facets':{}}
                
            for bucket in buckets:
                bucket_key = bucket.key
                bucket_count = bucket.doc_count
                bucket_dict = {'global_count': bucket_count, 'count': 0, 'display': bucket.key}
                if lookup:
                    if bucket_key in lookup:
                        bucket_dict.update(lookup[bucket_key])
                facet_results[k]['facets'][bucket_key] = bucket_dict

    # filter by resourcetype
    if resourcetype == 'documents':
        search = search.query("match", type_exact="document")
    elif resourcetype == 'layers':
        search = search.query("match", type_exact="layer")
    elif resourcetype == 'maps':
        search = search.query("match", type_exact="map")

    # Build main query to search in fields[]
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


    # Add the facet queries to the main search
    for fq in facet_filters:
        search = search.query(fq)

    # Add in has_time filter if set
    if has_time and has_time == 'true':
        search = search.query(Q({'match':{'has_time': True}}))

    # Add in Bounding Box filter
    if bbox:
        left, bottom, right, top = bbox.split(',')
        leftq = Q({'range': {'bbox_left': {'gte': float(left)}}})
        bottomq = Q({'range': {'bbox_bottom': {'gte': float(bottom)}}})
        rightq = Q({'range': {'bbox_right': {'lte': float(right)}}})
        topq = Q({'range': {'bbox_top': {'lte': float(top)}}})
        q = leftq & bottomq & rightq & topq
        search = search.query(q)

    # Add in Range Queries
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
    
    # Add range filters to the search
    if date_start:
        q = Q({'range': {'date': {'gte': date_start}}})
        search = search.query(q)

    if date_end:
        q = Q({'range': {'date': {'lte': date_end}}})
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
        

     # Apply sort
    if sort.lower() == "-date":
        search = search.sort({"date":
                              {"order": "desc",
                               "missing": "_last",
                               "unmapped_type": "date"
                               }})
    elif sort.lower() == "date":
        search = search.sort({"date":
                              {"order": "asc",
                               "missing": "_last",
                               "unmapped_type": "date"
                               }})
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
                               }})

    # Run the search using the offset and limit
    search = search[offset:offset + limit]
    results = search.execute()
    
    logger.debug('search: %s, results: %s', search, results)

    # get facets based on search criteria, add to overall facets
    aggregations = results.aggregations
    for k in aggregations:
        buckets = aggregations[k]['buckets']
        if len(buckets)>0:
            for bucket in buckets:
                bucket_key = bucket.key
                bucket_count = bucket.doc_count
                try:
                    facet_results[k]['facets'][bucket_key]['count'] = bucket_count
                except Exception as e:
                    facet_results['errors'] = "%s %s %s" % (k, bucket_key, e)

    # combine buckets for type and subtype and get rid of subtype bucket
    if 'subtype' in facet_results:
        facet_results['type']['facets'].update(facet_results['subtype']['facets'])
        del facet_results['subtype']

    # Sort Facets
    

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
    

class CSWRecordList(ListView):
    model = CSWRecord
    paginate_by = '20'
    context_object_name = "records"
    template_name = 'csw/record_list.html'

    def get_queryset(self):
        order = self.request.GET.get('sort_by', 'title')
        context = CSWRecord.objects.filter().order_by(order)
        return context

    def get_context_data(self, **kwargs):
        context = super(CSWRecordList, self).get_context_data(**kwargs)
        context['sort_by'] = self.request.GET.get('sort_by', 'title')
        return context


class CSWRecordCreate(CreateView):
    model = CSWRecord
    form_class = CSWRecordForm
    template_name = 'csw/new.html'
    success_url = reverse_lazy('csw-record-list')

    def get_context_data(self, **kwargs):
        data = super(CSWRecordCreate, self).get_context_data(**kwargs)
        if self.request.POST:
            data['cswrecordreference'] = CSWRecordReferenceFormSet(self.request.POST)
        else:
            data['cswrecordreference'] = CSWRecordReferenceFormSet()
        return data

    def form_valid(self, form):
        context = self.get_context_data()
        cswrecordreference = context['cswrecordreference']
        with transaction.atomic():
            self.object = form.save()
            self.object.user = self.request.user
            self.object.save()

            if cswrecordreference.is_valid():
                cswrecordreference.instance = self.object
                cswrecordreference.save()

            create_new_csw.delay(self.object.id)
        return super(CSWRecordCreate, self).form_valid(form)


class CSWRecordUpdate(UpdateView):
    model = CSWRecord
    form_class = CSWRecordForm
    template_name = 'csw/new.html'
    
    success_url = reverse_lazy('csw-record-list')

    def get_context_data(self, **kwargs):
        data = super(CSWRecordUpdate, self).get_context_data(**kwargs)
        if self.request.POST:
            data['cswrecordreference'] = CSWRecordReferenceFormSet(self.request.POST, instance=self.object)
        else:
            data['cswrecordreference'] = CSWRecordReferenceFormSet(instance=self.object)
        return data

    def form_valid(self, form):
        context = self.get_context_data()
        cswrecordreference = context['cswrecordreference']
        with transaction.atomic():
            self.object = form.save()
            self.object.user = self.request.user
            self.object.save()

            if cswrecordreference.is_valid():
                cswrecordreference.instance = self.object
                cswrecordreference.save()

            update_csw.delay(self.object.id)
        return super(CSWRecordUpdate, self).form_valid(form)


def xml_csw_view(request, pk):
    xml = write_xml(pk, 'INSERT')
    return HttpResponse(xml, content_type="text/xml")


# Attempt to delete the record.
#
def delete_csw_view(request, pk):
    # trigger the CSW delete task
    delete_csw.delay(pk)

    # bounce the user back to the index.
    return redirect('csw-record-list')
