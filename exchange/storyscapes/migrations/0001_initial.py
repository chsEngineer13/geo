# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('maps', '24_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Story',
            fields=[
                ('resourcebase_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='base.ResourceBase')),
                ('distribution_url', models.TextField(help_text='information about on-line sources from which the dataset, specification, or community profile name and extended metadata elements can be obtained', null=True, verbose_name='distribution URL', blank=True)),
                ('distribution_description', models.TextField(help_text='detailed text description of what the online resource is/does', null=True, verbose_name='distribution description', blank=True)),
            ],
            options={
                'abstract': False,
                'db_table': 'maps_story',
                'verbose_name_plural': 'Stories',
            },
            bases=('base.resourcebase',),
        ),
        migrations.CreateModel(
            name='StoryChapter',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('chapter_index', models.IntegerField(null=True, verbose_name='chapter index', blank=True)),
                ('viewer_playbackmode', models.CharField(max_length=32, null=True, verbose_name='Viewer Playback', blank=True)),
                ('map', models.ForeignKey(blank=True, to='maps.Map', null=True)),
                ('story', models.ForeignKey(blank=True, to='storyscapes.Story', null=True)),
            ],
            options={
                'abstract': False,
                'db_table': 'maps_story_bridge',
                'verbose_name_plural': 'Chapters',
            },
        ),
        migrations.AddField(
            model_name='story',
            name='chapters',
            field=models.ManyToManyField(to='maps.Map', through='storyscapes.StoryChapter'),
        ),
    ]
