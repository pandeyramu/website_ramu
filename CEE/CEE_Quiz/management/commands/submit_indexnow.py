import json
import time

import requests
from django.conf import settings
from django.core.management.base import BaseCommand

from CEE_Quiz.models import Subject, Chapter, SubChapter, SolutionSet


class Command(BaseCommand):
    help = "Submit all site URLs to Bing/Yandex/Seznam via the IndexNow API."

    def add_arguments(self, parser):
        parser.add_argument('--chunk', type=int, default=1000,
                            help='Max URLs per request (IndexNow hard cap).')
        parser.add_argument('--quiet', action='store_true',
                            help='Only print errors.')

    def handle(self, *args, **options):
        chunk_size = options['chunk']
        quiet = options['quiet']
        key = getattr(settings, 'INDEXNOW_KEY', '')
        host = settings.SITE_URL.replace('https://', '').replace('http://', '').rstrip('/')

        if not key:
            self.stdout.write(self.style.ERROR(
                'INDEXNOW_KEY is not set in settings/environment. Skipping.'))
            return

        urls = self._build_url_list()
        self.stdout.write(self.style.MIGRATE_HEADING(
            f"IndexNow: {len(urls)} URLs for host {host}"))

        for start in range(0, len(urls), chunk_size):
            batch = urls[start:start + chunk_size]
            payload = {
                'host': host,
                'key': key,
                'keyLocation': f'https://{host}/{key}.txt',
                'urlList': batch,
            }
            success = self._post_batch(payload, quiet)
            if not success:
                self.stdout.write(self.style.ERROR(
                    f"  Failed submitting {len(batch)} URLs (batch {start // chunk_size + 1})."))
            elif not quiet:
                self.stdout.write(self.style.SUCCESS(
                    f"  ✓ Submitted {len(batch)} URLs."))
            time.sleep(1)

    def _build_url_list(self):
        base = settings.SITE_URL.strip('/')
        urls = [f'{base}/']

        from CEE_Quiz.views import BLOG_POST_ORDER
        for name in ['about', 'contact', 'privacy_policy', 'disclaimer', 'terms_of_service', 'blog']:
            urls.append(f'{base}/{name}/')
        urls.append(f'{base}/all-subjects/')
        urls.append(f'{base}/full-test/')

        for obj in Subject.objects.order_by('id'):
            urls.append(f'{base}/subject/{obj.slug}/')
        for obj in Chapter.objects.order_by('id'):
            urls.append(f'{base}/chapter/{obj.slug}/')
            urls.append(f'{base}/chapter/{obj.slug}/subchapters/')
        for obj in SubChapter.objects.order_by('id'):
            urls.append(f'{base}/mcq/{obj.slug}/')
        for obj in SolutionSet.objects.select_related('chapter').order_by('id'):
            urls.append(f'{base}/chapter/{obj.chapter.slug}/solved-set/{obj.set_number}/')
        for slug in BLOG_POST_ORDER:
            urls.append(f'{base}/blog/{slug}/')

        seen = set()
        return [u for u in urls if not (u in seen or seen.add(u))]

    def _post_batch(self, payload, quiet):
        for endpoint in ('https://api.indexnow.org/indexnow',
                         'https://www.bing.com/indexnow'):
            try:
                resp = requests.post(endpoint, json=payload, timeout=30)
                if resp.status_code in (200, 202):
                    return True
                if not quiet:
                    self.stdout.write(
                        f"  {endpoint}: HTTP {resp.status_code} {resp.text[:200]}")
            except requests.RequestException as exc:
                if not quiet:
                    self.stdout.write(
                        self.style.WARNING(f"  {endpoint}: {exc}"))
        return False