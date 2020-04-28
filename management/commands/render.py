from django.core.management.base import BaseCommand, CommandError
from render_static.utils import RenderStatic

#------------------------------------------------------------------------------

class Command(BaseCommand):

    help = 'Renders all views for url patterns as static html files'

    def add_arguments(self, parser):
        parser.add_argument(
            '--html',
            action='store_true',
            help='Prefer internal links ending with .html instead of slash',
        )

    def handle(self, *args, **options):
        rs = RenderStatic(options['html'])
        if rs.urlpatterns:
            rs.render_static()
            log = f"\r\nSuccessfully rendered site to:\r\n{rs.savepath}"
            self.stdout.write(self.style.SUCCESS(log))
        else:
            self.stderr.write(self.style.ERROR("Could not render site"))

#------------------------------------------------------------------------------