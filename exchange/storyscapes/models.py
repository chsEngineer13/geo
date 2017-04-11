from geonode.base.models import ResourceBase, TopicCategory
from geonode.maps.models import Map
import json
import uuid

from django import core, db
from django.db.models import signals
from django.utils.translation import ugettext_lazy as _


class Story(ResourceBase):

    chapters = db.models.ManyToManyField(Map, through='StoryChapter')

    def get_absolute_url(self):
        return ''#core.urlresolvers.reverse('mapstory.views.map_detail', None, [str(self.id)])

    def update_from_viewer(self, conf):

        if isinstance(conf, basestring):
            conf = json.loads(conf)

        self.title = conf['title']
        self.abstract = conf['abstract']
        self.is_published = conf['is_published']
        if conf['category'] is not None:
            self.category = TopicCategory(conf['category'])

        if self.uuid is None or self.uuid == '':
            self.uuid = str(uuid.uuid1())

        removed_chapter_ids = conf['removed_chapters']
        if removed_chapter_ids is not None and len(removed_chapter_ids) > 0:
            for chapter_id in removed_chapter_ids:
                map_obj = Map.objects.get(id=chapter_id)
                self.chapter_list.remove(map_obj)

        #self.keywords.add(*conf['map'].get('keywords', []))
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
            'chapters': [chapter.map.viewer_json(user, None) for chapter in self.chapters.all()],
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
        'information about on-line sources from which the dataset, specification, or '
        'community profile name and extended metadata elements can be obtained')
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


class StoryChapter(db.models.Model):
    story = db.models.ForeignKey(Story, blank=True, null=True)
    map = db.models.ForeignKey(Map, blank=True, null=True)
    chapter_index = db.models.IntegerField(_('chapter index'), null=True, blank=True)
    viewer_playbackmode = db.models.CharField(_('Viewer Playback'), max_length=32, blank=True, null=True)

    #This needs review

    def update_from_viewer(self, conf):

        if isinstance(conf, basestring):
            conf = json.loads(conf)

        #super allows us to call base class function implementation from geonode
        super(Map, self).update_from_viewer(conf)

        self.viewer_playbackmode = conf['viewer_playbackmode'] or 'Instant'

        self.chapter_index = conf['chapter_index']
        story_id = conf.get('story_id', 0)
        story_obj = Story.objects.get(id=story_id)
        self.story = story_obj
        self.save()

    def viewer_json(self, user, access_token=None, *added_layers):
        base_config = super(Map, self).viewer_json(user, access_token, *added_layers)
        base_config['viewer_playbackmode'] = self.viewer_playbackmode
        base_config['tools'] = [{'outputConfig': {'playbackMode': self.viewer_playbackmode}, 'ptype': 'gxp_playback'}]

        return base_config

    class Meta(ResourceBase.Meta):
        verbose_name_plural = 'Chapters'
        db_table = 'maps_story_bridge'
        pass

