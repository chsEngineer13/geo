from . import ExchangeTest
from elasticsearch_dsl.connections import connections
from django.conf import settings
from elasticsearch import Elasticsearch
import pytest
from django.core.management import call_command
import subprocess


@pytest.mark.skipif(settings.ES_SEARCH is False,
                    reason="Only run if using unified search")
class GeonodeElasticsearchTest(ExchangeTest):

    def setUp(self):
        super(GeonodeElasticsearchTest, self).setUp()
        self.login()

        # connect to the ES instance
        connections.create_connection(hosts=[settings.ES_URL])

    def test_management_commands(self):
        es = Elasticsearch(settings.ES_URL)
        mappings = es.indices.get_mapping()

        # Ensure all the indices exist in our mappings upon build
        self.assertTrue('profile-index' in mappings)
        self.assertTrue('layer-index' in mappings)
        self.assertTrue('map-index' in mappings)
        self.assertTrue('document-index' in mappings)
        self.assertTrue('group-index' in mappings)
        self.assertTrue('story-index' in mappings)

        # Call the clear command and ensure the indices have been wiped
        call_command('clear_index')
        mappings = es.indices.get_mapping()
        self.assertFalse('profile-index' in mappings)
        self.assertFalse('layer-index' in mappings)
        self.assertFalse('map-index' in mappings)
        self.assertFalse('document-index' in mappings)
        self.assertFalse('group-index' in mappings)
        self.assertFalse('story-index' in mappings)

        # Rebuild the indices and ensure they return to our mappings
        call_command('rebuild_index')
        mappings = es.indices.get_mapping()
        self.assertTrue('profile-index' in mappings)
        self.assertTrue('layer-index' in mappings)
        self.assertTrue('map-index' in mappings)
        self.assertTrue('document-index' in mappings)
        self.assertTrue('group-index' in mappings)
        self.assertTrue('story-index' in mappings)

    def test_mappings(self):
        # We only want to test mappings because the rest should be covered
        # in the views_test.py for faceting and filtering
        es = Elasticsearch(settings.ES_URL)
        mappings = es.indices.get_mapping()

        profile_mappings = mappings[
            'profile-index']['mappings']['profile_index']['properties']
        profile_properties = {
            u'first_name': {
                u'type': u'string',
                u'analyzer': u'snowball'
            },
            u'id': {
                u'type': u'integer'
            },
            u'last_name': {
                u'type': u'string',
                u'analyzer': u'snowball'
            },
            u'organization': {
                u'type': u'string',
                u'analyzer': u'snowball'
            },
            u'position': {
                u'type': u'string',
                u'analyzer': u'snowball'
            },
            u'profile': {
                u'type': u'string',
                u'analyzer': u'snowball'
            },
            u'type': {
                u'type': u'string',
                u'analyzer': u'snowball'
            },
            u'username': {
                u'type': u'string',
                u'analyzer': u'snowball'
            }
        }
        print profile_mappings
        print profile_properties
        self.assertDictEqual(profile_mappings, profile_properties)

        group_mappings = mappings[
            'group-index']['mappings']['group_index']['properties']
        group_properties = {
            'description': {
                'type': 'string',
                'analyzer': 'snowball'
            },
            'id': {
                'type': 'integer'
            },
            'json': {
                'type': 'string'
            },
            'title': {
                'type': 'string',
                'analyzer': 'snowball'
            },
            'title_sortable': {
                'type': 'string'
            },
            'type': {
                'type': 'string',
                'analyzer': 'snowball'
            },
        }
        self.assertDictEqual(group_mappings, group_properties)

        document_mappings = mappings[
            'document-index']['mappings']['document_index']['properties']
        document_properties = {
            'abstract': {
                'type': 'string',
                'analyzer': 'snowball'
            },
            'bbox_bottom': {
                'type': 'float'
            },
            'bbox_left': {
                'type': 'float'
            },
            'bbox_right': {
                'type': 'float'
            },
            'bbox_top': {
                'type': 'float'
            },
            'category': {
                'type': 'string',
                'analyzer': 'snowball'
            },
            'category__gn_description': {
                'type': 'string',
                'analyzer': 'snowball'
            },
            'csw_type': {
                'type': 'string',
                'analyzer': 'snowball'
            },
            'csw_wkt_geometry': {
                'type': 'string',
                'analyzer': 'snowball'
            },
            'date': {
                'type': 'date',
                'format': 'strict_date_optional_time||epoch_millis'
            },
            'detail_url': {
                'type': 'string',
                'analyzer': 'snowball'
            },
            'id': {
                'type': 'integer'
            },
            'keywords': {
                'type': 'string',
                'analyzer': 'snowball'
            },
            'num_comments': {
                'type': 'integer'
            },
            'num_ratings': {
                'type': 'integer'
            },
            'owner__username': {
                'type': 'string',
                'analyzer': 'snowball'
            },
            'popular_count': {
                'type': 'integer'
            },
            'rating': {
                'type': 'integer'
            },
            'regions': {
                'type': 'string',
                'analyzer': 'snowball'
            },
            'share_count': {
                'type': 'integer'
            },
            'srid': {
                'type': 'string',
                'analyzer': 'snowball'
            },
            'supplemental_information': {
                'type': 'string',
                'analyzer': 'snowball'
            },
            'temporal_extent_end': {
                'type': 'date',
                'format': 'strict_date_optional_time||epoch_millis'
            },
            'temporal_extent_start': {
                'type': 'date',
                'format': 'strict_date_optional_time||epoch_millis'
            },
            'thumbnail_url': {
                'type': 'string',
                'analyzer': 'snowball'
            },
            'title': {
                'type': 'string',
                'analyzer': 'snowball'
            },
            'title_sortable': {
                'type': 'string'
            },
            'type': {
                'type': 'string',
                'analyzer': 'snowball'
            },
            'uuid': {
                'type': 'string',
                'analyzer': 'snowball'
            },
        }
        self.assertDictEqual(document_mappings, document_properties)

        layer_mappings = mappings[
            'layer-index']['mappings']['layer_index']['properties']
        layer_properties = {
            'abstract': {
                'type': 'string',
                'analyzer': 'snowball'
            },
            'bbox_bottom': {
                'type': 'float'
            },
            'bbox_left': {
                'type': 'float'
            },
            'bbox_right': {
                'type': 'float'
            },
            'bbox_top': {
                'type': 'float'
            },
            'category': {
                'type': 'string',
                'analyzer': 'snowball'
            },
            'category__gn_description': {
                'type': 'string',
                'analyzer': 'snowball'
            },
            'csw_type': {
                'type': 'string',
                'analyzer': 'snowball'
            },
            'csw_wkt_geometry': {
                'type': 'string',
                'analyzer': 'snowball'
            },
            'date': {
                'type': 'date',
                'format': 'strict_date_optional_time||epoch_millis'
            },
            'detail_url': {
                'type': 'string',
                'analyzer': 'snowball'
            },
            'featured': {
                'type': 'boolean'
            },
            'geogig_link': {
                'type': 'string',
                'analyzer': 'snowball'
            },
            'has_time': {
                'type': 'boolean'
            },
            'id': {
                'type': 'integer'
            },
            'is_published': {
                'type': 'boolean'
            },
            'keywords': {
                'type': 'string',
                'analyzer': 'snowball'
            },
            'num_comments': {
                'type': 'integer'
            },
            'num_ratings': {
                'type': 'integer'
            },
            'owner__first_name': {
                'type': 'string',
                'analyzer': 'snowball'
            },
            'owner__last_name': {
                'type': 'string',
                'analyzer': 'snowball'
            },
            'owner__username': {
                'type': 'string',
                'analyzer': 'snowball'
            },
            'popular_count': {
                'type': 'integer'
            },
            'rating': {
                'type': 'integer'
            },
            'regions': {
                'type': 'string',
                'analyzer': 'snowball'
            },
            'share_count': {
                'type': 'integer'
            },
            'srid': {
                'type': 'string',
                'analyzer': 'snowball'
            },
            'subtype': {
                'type': 'string',
                'analyzer': 'snowball'
            },
            'supplemental_information': {
                'type': 'string',
                'analyzer': 'snowball'
            },
            'temporal_extent_end': {
                'type': 'date',
                'format': 'strict_date_optional_time||epoch_millis'
            },
            'temporal_extent_start': {
                'type': 'date',
                'format': 'strict_date_optional_time||epoch_millis'
            },
            'thumbnail_url': {
                'type': 'string',
                'analyzer': 'snowball'
            },
            'title': {
                'type': 'string',
                'analyzer': 'snowball'
            },
            'title_sortable': {
                'type': 'string'
            },
            'type': {
                'type': 'string',
                'analyzer': 'snowball'
            },
            'typename': {
                'type': 'string',
                'analyzer': 'snowball'
            },
            'uuid': {
                'type': 'string',
                'analyzer': 'snowball'
            },
        }
        self.assertDictEqual(layer_mappings, layer_properties)

        map_mappings = mappings[
            'map-index']['mappings']['map_index']['properties']
        map_properties = {
            'abstract': {
                'type': 'string',
                'analyzer': 'snowball'
            },
            'bbox_bottom': {
                'type': 'float'
            },
            'bbox_left': {
                'type': 'float'
            },
            'bbox_right': {
                'type': 'float'
            },
            'bbox_top': {
                'type': 'float'
            },
            'category': {
                'type': 'string',
                'analyzer': 'snowball'
            },
            'category__gn_description': {
                'type': 'string',
                'analyzer': 'snowball'
            },
            'csw_type': {
                'type': 'string',
                'analyzer': 'snowball'
            },
            'csw_wkt_geometry': {
                'type': 'string',
                'analyzer': 'snowball'
            },
            'date': {
                'type': 'date',
                'format': 'strict_date_optional_time||epoch_millis'
            },
            'detail_url': {
                'type': 'string',
                'analyzer': 'snowball'
            },
            'id': {
                'type': 'integer'
            },
            'keywords': {
                'type': 'string',
                'analyzer': 'snowball'
            },
            'num_comments': {
                'type': 'integer'
            },
            'num_ratings': {
                'type': 'integer'
            },
            'owner__username': {
                'type': 'string',
                'analyzer': 'snowball'
            },
            'popular_count': {
                'type': 'integer'
            },
            'rating': {
                'type': 'integer'
            },
            'regions': {
                'type': 'string',
                'analyzer': 'snowball'
            },
            'share_count': {
                'type': 'integer'
            },
            'srid': {
                'type': 'string',
                'analyzer': 'snowball'
            },
            'supplemental_information': {
                'type': 'string',
                'analyzer': 'snowball'
            },
            'temporal_extent_end': {
                'type': 'date',
                'format': 'strict_date_optional_time||epoch_millis'
            },
            'temporal_extent_start': {
                'type': 'date',
                'format': 'strict_date_optional_time||epoch_millis'
            },
            'thumbnail_url': {
                'type': 'string',
                'analyzer': 'snowball'
            },
            'title': {
                'type': 'string',
                'analyzer': 'snowball'
            },
            'title_sortable': {
                'type': 'string'
            },
            'type': {
                'type': 'string',
                'analyzer': 'snowball'
            },
            'uuid': {
                'type': 'string',
                'analyzer': 'snowball'
            },
        }
        self.assertDictEqual(map_mappings, map_properties)

        story_mappings = mappings[
            'story-index']['mappings']['story_index']['properties']
        story_properties = {
            'abstract': {
                'type': 'string',
                'analyzer': 'snowball'
            },
            'bbox_bottom': {
                'type': 'float'
            },
            'bbox_left': {
                'type': 'float'
            },
            'bbox_right': {
                'type': 'float'
            },
            'bbox_top': {
                'type': 'float'
            },
            'category': {
                'type': 'string',
                'analyzer': 'snowball'
            },
            'category__gn_description': {
                'type': 'string',
                'analyzer': 'snowball'
            },
            'date': {
                'type': 'date',
                'format': 'strict_date_optional_time||epoch_millis'
            },
            'detail_url': {
                'type': 'string',
                'analyzer': 'snowball'
            },
            'distribution_description': {
                'type': 'string',
                'analyzer': 'snowball'
            },
            'distribution_url': {
                'type': 'string',
                'analyzer': 'snowball'
            },
            'featured': {
                'type': 'boolean'
            },
            'id': {
                'type': 'integer'
            },
            'is_published': {
                'type': 'boolean'
            },
            'keywords': {
                'type': 'string',
                'analyzer': 'snowball'
            },
            'num_chapters': {
                'type': 'integer'
            },
            'num_comments': {
                'type': 'integer'
            },
            'num_ratings': {
                'type': 'integer'
            },
            'owner__first_name': {
                'type': 'string',
                'analyzer': 'snowball'
            },
            'owner__last_name': {
                'type': 'string',
                'analyzer': 'snowball'
            },
            'owner__username': {
                'type': 'string',
                'analyzer': 'snowball'
            },
            'popular_count': {
                'type': 'integer'
            },
            'rating': {
                'type': 'integer'
            },
            'regions': {
                'type': 'string',
                'analyzer': 'snowball'
            },
            'share_count': {
                'type': 'integer'
            },
            'temporal_extent_end': {
                'type': 'date',
                'format': 'strict_date_optional_time||epoch_millis'
            },
            'temporal_extent_start': {
                'type': 'date',
                'format': 'strict_date_optional_time||epoch_millis'
            },
            'thumbnail_url': {
                'type': 'string',
                'analyzer': 'snowball'
            },
            'title': {
                'type': 'string',
                'analyzer': 'snowball'
            },
            'title_sortable': {
                'type': 'string'
            },
            'type': {
                'type': 'string',
                'analyzer': 'snowball'
            },
            'uuid': {
                'type': 'string',
                'analyzer': 'snowball'
            },
        }
        self.assertDictEqual(story_mappings, story_properties)
