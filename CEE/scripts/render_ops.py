"""Minimal Render REST API helpers (env-var swap + deploy + verify).

No third-party deps -- stdlib urllib only.

Env vars needed:
    RENDER_API_KEY      personal API key from dashboard.render.com
    RENDER_SERVICE_ID   your web service id (dashboard URL: .../services/srv-xxx)
"""
import os
import time
import urllib.request
import json


API_BASE = 'https://api.render.com/v1'


def _headers():
    key = os.environ['RENDER_API_KEY']
    return {
        'Authorization': f'Bearer {key}',
        'Accept': 'application/json',
        'Content-Type': 'application/json',
    }


def api(method, path, body=None):
    req = urllib.request.Request(
        f'{API_BASE}{path}',
        method=method,
        headers=_headers(),
        data=json.dumps(body).encode() if body is not None else None,
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            raw = r.read().decode()
            return r.status, (json.loads(raw) if raw else None)
    except urllib.error.HTTPError as e:
        return e.code, None


def get_env_vars(service_id):
    code, data = api('GET', f'/services/{service_id}/env-vars')
    return data or []


def upsert_env_var(service_id, key, value, trigger_deploy=True):
    """Create or update an env var. Render masks secret values on read, so we
    always write our known value. skipDeploy handles the auto-redeploy."""
    skip = 'false' if trigger_deploy else 'true'
    vars_ = get_env_vars(service_id)
    match = next((v for v in vars_ if v.get('envVar', {}).get('key') == key), None)
    if match:
        path = f'/services/{service_id}/env-vars/{match["id"]}?skipDeploy={skip}'
        code, _ = api('PATCH', path, {'envVar': {'value': value}})
    else:
        path = f'/services/{service_id}/env-vars?skipDeploy={skip}'
        code, _ = api('POST', path, {'envVar': {'key': key, 'value': value}})
    return code


def trigger_deploy(service_id):
    code, data = api('POST', f'/services/{service_id}/deploys')
    return code, (data or {}).get('id') if data else None


def wait_for_deploy(service_id, deploy_id, timeout=600):
    deadline = time.time() + timeout
    while time.time() < deadline:
        code, data = api('GET', f'/services/{service_id}/deploys')
        deploys = data or []
        for d in deploys:
            if d.get('id') == deploy_id:
                if d.get('status') in ('live', 'deactivated', 'canceled'):
                    return d.get('status')
        time.sleep(10)
    return 'timeout'


def verify_site(url, timeout_seconds=600, interval=15):
    deadline = time.time() + timeout_seconds
    import urllib.error
    while time.time() < deadline:
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'failover-watchdog'})
            with urllib.request.urlopen(req, timeout=20) as r:
                if r.status == 200:
                    return True
        except Exception:
            pass
        time.sleep(interval)
    return False