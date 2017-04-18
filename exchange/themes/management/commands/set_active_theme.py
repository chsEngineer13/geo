# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand, CommandError
from exchange.themes.models import Theme

error = ('An interger id is required to set the theme as active, use the '
         '--list to get the available theme id numbers.')

class Command(BaseCommand):
    help = 'Set a specific Theme as the active Theme.'


    def add_arguments(self, parser):
        parser.add_argument('--list',
            action='store_true',
            dest='list',
            default=False,
            help='List available themes')
        parser.add_argument('theme_id', type=int, nargs='?', default=None,)


    def handle(self, *args, **options):
        if options['list']:
            try:
                themes = all_entries = Theme.objects.all()
            except Theme.DoesNotExist:
                raise CommandError('Please run migrate to create themes')

            self.stdout.write("Available Themes:")

            for theme in themes:
                self.stdout.write("- %s [%s]" % (theme.name, theme.id))
        else:
            theme_id = options['theme_id']
            if not theme_id:
                raise CommandError(error)
            try:
                theme = Theme.objects.get(id=theme_id)
            except Theme.DoesNotExist:
                raise CommandError('Theme id "%s" does not exist' % theme_id)

            theme.active_theme = True
            theme.save()

            self.stdout.write('Successfully activated theme "%s"' % theme.name)
