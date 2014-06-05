import os
import sys
import inspect

from django.core.management.base import BaseCommand

import mod_wsgi.server

class Command(BaseCommand):
    option_list = BaseCommand.option_list + mod_wsgi.server.option_list
    args = '[options]'
    help = 'Starts Apache/mod_wsgi web server.'

    def handle(self, *args, **options):
        self.stdout.write('Successfully ran command.')

        from django.conf import settings
        wsgi_application = settings.WSGI_APPLICATION

        fields = wsgi_application.split('.')

        module_name = '.'.join(fields[:-1])
        callable_object = fields[-1]

        __import__(module_name)

        script_file = inspect.getsourcefile(sys.modules[module_name])

        args = [script_file]
        options['callable_object'] = callable_object

        options['working_directory'] = settings.BASE_DIR

        url_aliases = options.setdefault('url_aliases') or []

        try:
            if settings.STATIC_URL and settings.STATIC_URL.startswith('/'):
                if settings.STATIC_ROOT:
                    url_aliases.insert(0,
                            (settings.STATIC_URL.rstrip('/') or '/',
                            settings.STATIC_ROOT))
        except AttributeError:
            pass

        options['url_aliases'] = url_aliases

        options = mod_wsgi.server._cmd_setup_server(args, options)

        executable = os.path.join(options['server_root'], 'apachectl')
        name = executable.ljust(len(options['process_name']))
        os.execl(executable, name, 'start', '-DNO_DETACH')
