"""Sync/inventory between the primary (Neon) and standby (Supabase) Postgres DBs.

Usage (set env vars first -- see .env.example):
    python scripts/db_sync.py --inventory
    python scripts/db_sync.py --health
    python scripts/db_sync.py --sync-table CEE_Quiz_question --mode replace --direction neon-to-supabase
    python scripts/db_sync.py --sync-all --mode replace --direction neon-to-supabase

--mode replace : TRUNCATE target table, then COPY master rows (standby refresh).
                 ONLY safe when the target is a read-only standby that never
                 receives writes (that is how this failover setup works).
--mode append  : COPY without truncate (use only for tables you are sure about).

Env vars:
    NEON_DATABASE_URL       postgres://... (primary, source of truth)
    SUPABASE_DATABASE_URL   postgres://... (standby)
Use psycopg (pip install "psycopg[binary]") or PostgreSQL psql binaries.
"""
import argparse
import os
import shutil
import sys

NONE, P1, P2 = 'no-client', 'psycopg', 'psql'


def client_kind():
    try:
        import psycopg  # noqa: F401
        return P2
    except ImportError:
        pass
    try:
        import psycopg2  # noqa: F401
        return P2
    except ImportError:
        pass
    if shutil.which('psql'):
        return P1
    return NONE


def dsn(name, eng):
    url = os.environ.get(name, '')
    if not url:
        sys.exit(f'{name} is not set (see scripts/.env.example)')
    if eng == P2:
        return url


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--inventory', action='store_true')
    ap.add_argument('--health', action='store_true')
    ap.add_argument('--sync-table')
    ap.add_argument('--sync-all', action='store_true')
    ap.add_argument('--mode', choices=['replace', 'append'], default='replace')
    ap.add_argument('--direction', choices=['neon-to-supabase', 'supabase-to-neon'], default='neon-to-supabase')
    args = ap.parse_args()

    eng = client_kind()
    if eng == NONE:
        sys.exit('No Postgres client found. Run: pip install "psycopg[binary]"')

    tables = [
        'CEE_Quiz_attempt',
        'CEE_Quiz_attemptanswer',
        'CEE_Quiz_chapter',
        'CEE_Quiz_fbresult',
        'CEE_Quiz_question',
        'CEE_Quiz_subchapter',
        'CEE_Quiz_subject',
        'CEE_Quiz_pageSEO',
        'django_session',
        'django_migrations',
    ]

    if args.inventory:
        for side, var in (('neon', 'NEON_DATABASE_URL'), ('supabase', 'SUPABASE_DATABASE_URL')):
            print(f'--- {side} ({var}) ---')
            for t in tables:
                row = _query_one(var, eng, f'SELECT count(*) FROM "{t}"')
                print(f'  {t}: {row}')
        return

    if args.health:
        ok_p = _query_one('NEON_DATABASE_URL', eng, 'SELECT 1')
        ok_s = _query_one('SUPABASE_DATABASE_URL', eng, 'SELECT 1')
        print(f'neon  (primary)  : {"OK" if ok_p == 1 else "FAIL / unreachable"}')
        print(f'supabase (standby): {"OK" if ok_s == 1 else "FAIL / unreachable"}')
        return

    src_var = 'NEON_DATABASE_URL' if args.direction == 'neon-to-supabase' else 'SUPABASE_DATABASE_URL'
    dst_var = 'SUPABASE_DATABASE_URL' if args.direction == 'neon-to-supabase' else 'NEON_DATABASE_URL'
    if not (args.sync_all or args.sync_table):
        ap.error('provide --sync-table <name> or --sync-all')

    targets = tables if args.sync_all else [args.sync_table]
    for t in targets:
        _sync_table(src_var, dst_var, eng, t, args.mode)
    print('done')


def _run_sql(url, eng, sql, fetch=False):
    if eng == P2:
        import psycopg
        with psycopg.connect(url, connect_timeout=15) as conn:
            with conn.cursor() as cur:
                cur.execute(sql)
                return cur.fetchall() if fetch else None
    # psql fallback
    import subprocess
    out = subprocess.run(
        ['psql', url, '-t', '-A', '-c', sql], capture_output=True, text=True, timeout=60
    )
    if out.returncode != 0:
        raise RuntimeError(out.stderr)
    return out.stdout


def _query_one(url, eng, sql):
    try:
        rows = _run_sql(url, eng, sql, fetch=True)
        return rows[0][0]
    except Exception:
        return None


def _copy_table(src_url, dst_url, eng, table, mode):
    if eng != P2:
        raise RuntimeError('--sync-* requires a Python Postgres driver (pip install "psycopg[binary]")')
    import tempfile
    import psycopg
    fd, path = tempfile.mkstemp(suffix='.copy')
    try:
        with psycopg.connect(src_url, connect_timeout=30) as sconn, \
             psycopg.connect(dst_url, connect_timeout=30) as dconn:
            if mode == 'replace':
                with dconn.cursor() as dc:
                    dc.execute(f'TRUNCATE "{table}"')
                dconn.commit()
            with sconn.cursor() as sc, open(path, 'wb') as f:
                sc.copy(f'COPY "{table}" TO STDOUT', f)
            with dconn.cursor() as dc, open(path, 'rb') as f:
                dc.copy(f'COPY "{table}" FROM STDIN', f)
            dconn.commit()
        print(f'  synced "{table}" ({mode}) -> merged into standby')
    finally:
        os.close(fd)
        os.remove(path)


def _sync_table(src_var, dst_var, eng, table, mode):
    src = os.environ.get(src_var, '')
    dst = os.environ.get(dst_var, '')
    if not src or not dst:
        print(f'  SKIP "{table}" (missing {src_var} or {dst_var})')
        return
    print(f'  -- {table} ({src_var} -> {dst_var})')
    _copy_table(src, dst, eng, table, mode)


if __name__ == '__main__':
    main()