import os

from django.core.management.base import BaseCommand

from django.contrib.sites.models import Site

from allauth.socialaccount.models import SocialApp

def env(name, default=''):

    return os.environ.get(name, default).strip()

class Command(BaseCommand):

    help = 'Настраивает TypeWorld: Site, Google OAuth, VK OAuth из переменных окружения/.env.'

    def add_arguments(self, parser):

        parser.add_argument('--domain', default=env('TYPEWORLD_SITE_DOMAIN', '127.0.0.1:8000'))

        parser.add_argument('--name', default=env('TYPEWORLD_SITE_NAME', 'TypeWorld local'))

        parser.add_argument('--google-client-id', default=env('GOOGLE_CLIENT_ID'))

        parser.add_argument('--google-secret', default=env('GOOGLE_CLIENT_SECRET'))

        parser.add_argument('--vk-client-id', default=env('VK_CLIENT_ID'))

        parser.add_argument('--vk-secret', default=env('VK_CLIENT_SECRET'))

    def handle(self, *args, **options):

        site, _ = Site.objects.get_or_create(id=1)

        site.domain = options['domain']

        site.name = options['name']

        site.save()

        self.stdout.write(self.style.SUCCESS(f'Site настроен: {site.domain}'))

        configured = 0

        configured += self.configure_app(

            provider='google',

            name='Google',

            client_id=options['google_client_id'],

            secret=options['google_secret'],

            site=site,

        )

        configured += self.configure_app(

            provider='vk',

            name='VK',

            client_id=options['vk_client_id'],

            secret=options['vk_secret'],

            site=site,

        )

        if configured == 0:

            self.stdout.write(self.style.WARNING('OAuth ключи не указаны. Почтовый вход будет работать, Google/VK появятся после заполнения .env и повторного запуска команды.'))

        else:

            self.stdout.write(self.style.SUCCESS(f'OAuth приложений настроено: {configured}'))

        self.stdout.write('Callback Google: http://127.0.0.1:8000/accounts/google/login/callback/')

        self.stdout.write('Callback VK:     http://127.0.0.1:8000/accounts/vk/login/callback/')

    def configure_app(self, provider, name, client_id, secret, site):

        if not client_id or not secret:

            self.stdout.write(self.style.WARNING(f'{name}: пропущено, нет CLIENT_ID/SECRET'))

            return 0

        app = SocialApp.objects.filter(provider=provider).first()

        if not app:

            app = SocialApp(provider=provider, name=name)

        app.name = name

        app.client_id = client_id

        app.secret = secret

        app.save()

        app.sites.set([site])

        self.stdout.write(self.style.SUCCESS(f'{name}: SocialApp создан/обновлен'))

        return 1
