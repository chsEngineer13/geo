# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = []

    operations = [
        migrations.CreateModel(
            name='LoginEvent',
            fields=[
                ('id', models.AutoField(
                    verbose_name='ID',
                    serialize=False,
                    auto_created=True,
                    primary_key=True
                )),
                ('event', models.SmallIntegerField(
                    choices=[
                        (0, b'Login'),
                        (1, b'Logout'),
                        (2, b'Failed login')
                    ]
                )),
                ('username', models.CharField(
                    max_length=255,
                    null=False,
                    blank=False
                )),
                ('ip', models.GenericIPAddressField(null=True, blank=True)),
                ('email', models.EmailField(null=True, blank=True)),
                ('fullname', models.CharField(
                    max_length=255,
                    null=True,
                    blank=True
                )),
                ('superuser', models.NullBooleanField()),
                ('staff', models.NullBooleanField()),
                ('datetime', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'ordering': ['-datetime'],
                'verbose_name': 'login event',
                'verbose_name_plural': 'login events',
            },
        ),
    ]
