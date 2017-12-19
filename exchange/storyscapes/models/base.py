from geonode.base.models import ResourceBase, TopicCategory
from geonode.maps.models import Map
import json
import uuid
from django.contrib.contenttypes.models import ContentType
from dialogos.models import Comment
from django.db.models import Avg
from django import core, db
from django.utils.translation import ugettext_lazy as _
from django.conf import settings
from agon_ratings.models import OverallRating


class Story(ResourceBase):

    chapters = db.models.ManyToManyField(Map, through='StoryChapter')

    def get_absolute_url(self):
        return core.urlresolvers.reverse('story_detail', None, [str(self.id)])

    def update_from_viewer(self, conf):

        if isinstance(conf, basestring):
            conf = json.loads(conf)

        self.title = conf['title']
        self.abstract = conf['abstract']
        self.is_published = conf['is_published']
        self.detail_url = self.get_absolute_url()
        if conf['category'] is not None:
            self.category = TopicCategory(conf['category'])

        if self.uuid is None or self.uuid == '':
            self.uuid = str(uuid.uuid1())

        removed_chapter_ids = conf['removed_chapters']
        if removed_chapter_ids is not None and len(removed_chapter_ids) > 0:
            for chapter_id in removed_chapter_ids:
                chapter_obj = StoryChapter.objects.get(map_id=chapter_id)
                self.chapters.get(storychapter=chapter_obj).delete()

        # self.keywords.add(*conf['map'].get('keywords', []))
        self.save()

    def viewer_json(self, user):

        about = {
            'title': self.title,
            'abstract': self.abstract,
            'owner': self.owner.name_long,
            'username': self.owner.username
        }

        config = {
            'id': self.id,
            'about': about,
            'chapters': [chapter.map.viewer_json(
                user, None) for chapter in self.chapters.all()],
            'thumbnail_url': '/static/geonode/img/missing_thumb.png'
        }

        return config

    def update_thumbnail(self, first_chapter_obj):
        if first_chapter_obj.chapter_index != 0:
            return

        chapter_base = ResourceBase.objects.get(id=first_chapter_obj.id)
        ResourceBase.objects.filter(id=self.id).update(
            thumbnail_url=chapter_base.thumbnail_url
        )

    @property
    def class_name(self):
        return self.__class__.__name__

    distribution_url_help_text = _(
        'information about on-line sources from which the dataset, '
        'specification, or community profile name and extended '
        'metadata elements can be obtained')
    distribution_description_help_text = _(
        'detailed text description of what the online resource is/does')
    distribution_url = db.models.TextField(
        _('distribution URL'),
        blank=True,
        null=True,
        help_text=distribution_url_help_text)
    distribution_description = db.models.TextField(
        _('distribution description'),
        blank=True,
        null=True,
        help_text=distribution_description_help_text)

    class Meta(ResourceBase.Meta):
        verbose_name_plural = 'Stories'
        db_table = 'maps_story'
        pass

    # elasticsearch_dsl indexing
    def indexing(self):
        if settings.ES_SEARCH:
            from elasticsearch_app.search import StoryIndex
            obj = StoryIndex(
                meta={'id': self.id},
                id=self.id,
                abstract=self.abstract,
                category__gn_description=self.prepare_category_gn_description(),  # noqa
                distribution_description=self.distribution_description,
                distribution_url=self.distribution_url,
                owner__username=self.prepare_owner(),
                popular_count=self.popular_count,
                share_count=self.share_count,
                rating=self.prepare_rating(),
                thumbnail_url=self.thumbnail_url,
                detail_url=self.get_absolute_url(),
                uuid=self.uuid,
                title=self.title,
                date=self.date,
                type=self.prepare_type(),
                title_sortable=self.prepare_title_sortable(),
                category=self.prepare_category(),
                bbox_left=self.bbox_x0,
                bbox_right=self.bbox_x1,
                bbox_bottom=self.bbox_y0,
                bbox_top=self.bbox_y1,
                temporal_extent_start=self.temporal_extent_start,
                temporal_extent_end=self.temporal_extent_end,
                keywords=self.keyword_slug_list(),
                regions=self.region_name_list(),
                num_ratings=self.prepare_num_ratings(),
                num_comments=self.prepare_num_comments(),
                num_chapters=self.prepare_num_chapters(),
                owner__first_name=self.prepare_owner_first(),
                owner__last_name=self.prepare_owner_last(),
                is_published=self.is_published,
                featured=self.featured
            )
            obj.save()
            return obj.to_dict(include_meta=True)

    # elasticsearch_dsl indexing helper functions
    def prepare_type(self):
        return "layer"

    def prepare_rating(self):
        ct = ContentType.objects.get_for_model(self)
        try:
            rating = OverallRating.objects.filter(
                object_id=self.pk,
                content_type=ct
            ).aggregate(r=Avg("rating"))["r"]
            return float(str(rating or "0"))
        except OverallRating.DoesNotExist:
            return 0.0

    def prepare_num_ratings(self):
        ct = ContentType.objects.get_for_model(self)
        try:
            return OverallRating.objects.filter(
                object_id=self.pk,
                content_type=ct
            ).all().count()
        except OverallRating.DoesNotExist:
            return 0

    def prepare_num_comments(self):
        ct = ContentType.objects.get_for_model(self)
        try:
            return Comment.objects.filter(
                object_id=self.pk,
                content_type=ct
            ).all().count()
        except:
            return 0

    def prepare_num_chapters(self):
        ct = ContentType.objects.get_for_model(self)
        try:
            return StoryChapter.objects.filter(
                object_id=self.pk,
                content_type=ct
            ).all().count()
        except:
            return 0

    def prepare_title_sortable(self):
        return self.title.lower()

    def prepare_category(self):
        if self.category:
            return self.category.identifier
        else:
            return None

    def prepare_category_gn_description(self):
        if self.category:
            return self.category.gn_description
        else:
            return None

    def prepare_owner(self):
        if self.owner:
            return self.owner.username
        else:
            return None

    def prepare_owner_first(self):
        if self.owner.first_name:
            return self.owner.first_name
        else:
            return None

    def prepare_owner_last(self):
        if self.owner.last_name:
            return self.owner.last_name
        else:
            return None


class StoryChapter(db.models.Model):
    story = db.models.ForeignKey(Story, blank=True, null=True)
    map = db.models.ForeignKey(Map, blank=True, null=True)
    chapter_index = db.models.IntegerField(
        _('chapter index'), null=True, blank=True)
    viewer_playbackmode = db.models.CharField(
        _('Viewer Playback'), max_length=32, blank=True, null=True)

    # This needs review

    def update_from_viewer(self, conf):

        if isinstance(conf, basestring):
            conf = json.loads(conf)

        self.viewer_playbackmode = conf['viewer_playbackmode'] or 'Instant'

        self.chapter_index = conf['chapter_index']
        story_id = conf.get('story_id', 0)
        story_obj = Story.objects.get(id=story_id)
        self.story = story_obj
        self.save()

    class Meta(ResourceBase.Meta):
        verbose_name_plural = 'Chapters'
        db_table = 'maps_story_bridge'
        pass
