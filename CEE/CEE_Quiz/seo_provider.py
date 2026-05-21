import logging
import os
from functools import lru_cache
from urllib.parse import quote

import requests


logger = logging.getLogger(__name__)


@lru_cache(maxsize=1024)
def get_supabase_page_seo(page_slug):
    """Fetch SEO row by slug from Supabase REST API.

    Returns a dict with SEO fields or None when not found/unconfigured.
    """
    slug = (page_slug or '').strip()
    if not slug:
        return None

    supabase_url = (os.environ.get('SUPABASE_URL') or '').strip().rstrip('/')
    supabase_key = (
        (os.environ.get('SUPABASE_SERVICE_ROLE_KEY') or '').strip()
        or (os.environ.get('SUPABASE_ANON_KEY') or '').strip()
    )
    table_name = (os.environ.get('SUPABASE_PAGE_SEO_TABLE') or 'page seo').strip()

    if not supabase_url or not supabase_key or not table_name:
        return None

    endpoint = f"{supabase_url}/rest/v1/{quote(table_name, safe='')}"
    headers = {
        'apikey': supabase_key,
        'Authorization': f'Bearer {supabase_key}',
        'Accept': 'application/json',
    }
    params = {
        'select': 'page_slug,meta_title,meta_description,meta_keywords,og_title,og_description',
        'page_slug': f'eq.{slug}',
        'limit': '1',
    }

    try:
        response = requests.get(endpoint, headers=headers, params=params, timeout=6)
        if response.status_code >= 400:
            logger.warning('Supabase SEO lookup failed (%s): %s', response.status_code, response.text[:240])
            return None

        payload = response.json()
        if isinstance(payload, list) and payload:
            return payload[0]
        return None
    except Exception as exc:
        logger.warning('Supabase SEO lookup error: %s', exc)
        return None
