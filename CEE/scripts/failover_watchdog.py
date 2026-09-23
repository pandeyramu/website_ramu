"""Failover watchdog: keep the site on a healthy DB, flipping DATABASE_URL on
Render when the current primary fails.

Recommended usage -- locally every 5-15 min (Task Scheduler / cron) or as a
GitHub Actions scheduled job:

    python scripts/failover_watchdog.py --once     # check + act once
    python scripts/failover_watchdog.py            # loop every --interval s

Env vars (see scripts/.env.example):
    NEON_DATABASE_URL       primary connection string (also the value we PATCH into Render)
    SUPABASE_DATABASE_URL   standby connection string
    RENDER_API_KEY, RENDER_SERVICE_ID
    SITE_URL                homepage to verify after a flip (default https://pandeyramu.com.np/)
    FAILURES_BEFORE_FLIP    default 3

Safety: when serving from the standby, writes are blocked by the Django
"StandbyReadOnlyMiddleware" (env DB_STANDBY=1). So the standby never drifts,
and flipping back is always safe with no merge needed.
"""
import argparse
import json
import os
import sys

import db_sync
import render_ops

STATE_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), '.db_state')


def load_state():
    try:
        with open(STATE_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        return {'current': 'neon', 'fails': 0}


def save_state(state):
    with open(STATE_FILE, 'w', encoding='utf-8') as f:
        json.dump(state, f, indent=2)


def db_ok(var):
    return db_sync._query_one(var, db_sync.client_kind(), 'SELECT 1') == 1


def flip(service_id, active_url, standby_url, standby_flag):
    print(f'  flipping DATABASE_URL -> {"STANDBY" if standby_flag else "PRIMARY"}')
    code = render_ops.upsert_env_var(service_id, 'DATABASE_URL', active_url, trigger_deploy=True)
    print(f'  DATABASE_URL env update: http {code}')
    code = render_ops.upsert_env_var(service_id, 'DB_STANDBY', '1' if standby_flag else '0', trigger_deploy=False)
    print(f'  DB_STANDBY env update: http {code}')
    code, deploy_id = render_ops.trigger_deploy(service_id)
    print(f'  deploy triggered: http {code}, id={deploy_id}')
    if deploy_id:
        status = render_ops.wait_for_deploy(service_id, deploy_id)
        print(f'  deploy status: {status}')
    ok = render_ops.verify_site(os.environ.get('SITE_URL', 'https://pandeyramu.com.np/'))
    print(f'  site verified: {"OK" if ok else "FAIL"}')


def print_status():
    print(f'neon    (primary):  {"OK" if db_ok("NEON_DATABASE_URL") else "FAIL/unreachable"}')
    print(f'supabase (standby): {"OK" if db_ok("SUPABASE_DATABASE_URL") else "FAIL/unreachable"}')


def run_once(run_sync_hook=True):
    service_id = os.environ.get('RENDER_SERVICE_ID', '')
    client = db_sync.client_kind()
    if client == db_sync.NONE:
        sys.exit('No Postgres client: pip install "psycopg[binary]"')

    state = load_state()
    current = state.get('current', 'neon')
    primary_ok = db_ok('NEON_DATABASE_URL')
    standby_ok = db_ok('SUPABASE_DATABASE_URL')

    if primary_ok and standby_ok:
        state['fails'] = 0
        if current != 'neon' and run_sync_hook:
            sync_hook = os.environ.get('SYNC_HOOK_ON_FLIP_BACK', '')
            if sync_hook:
                print(f'  running post-recovery sync hook: {sync_hook}')
                os.system(sync_hook)
        save_state(state)
        print('all healthy; keep PRIMARY')
        return 0

    if current == 'neon':
        if not primary_ok and standby_ok:
            state['fails'] += 1
            fails_required = int(os.environ.get('FAILURES_BEFORE_FLIP', '3'))
            print(f'primary FAIL ({state["fails"]}/{fails_required})')
            if state['fails'] >= fails_required:
                flip(service_id, os.environ['SUPABASE_DATABASE_URL'], os.environ['NEON_DATABASE_URL'], True)
                state = {'current': 'supabase', 'fails': 0}
            save_state(state)
            return 0
        print('primary OK or standby unreachable; no action')

    else:  # current == 'supabase'
        if not standby_ok and primary_ok:
            state['fails'] += 1
            fails_required = int(os.environ.get('FAILURES_BEFORE_FLIP', '3'))
            print(f'standby FAIL ({state["fails"]}/{fails_required})')
            if state['fails'] >= fails_required:
                flip(service_id, os.environ['NEON_DATABASE_URL'], os.environ['SUPABASE_DATABASE_URL'], False)
                state = {'current': 'neon', 'fails': 0}
            save_state(state)
            return 0
        print('standby OK or primary unreachable; no action')

    save_state(state)
    return 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--once', action='store_true')
    ap.add_argument('--interval', type=int, default=300)
    ap.add_argument('--status', action='store_true')
    args = ap.parse_args()

    if args.status:
        print_status()
        return

    if args.once:
        sys.exit(run_once())
    else:
        import time
        while True:
            try:
                run_once()
            except Exception as exc:
                print(f'watchdog error: {exc}')
            time.sleep(args.interval)


if __name__ == '__main__':
    main()