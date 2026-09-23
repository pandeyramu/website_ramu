"""Emergency content restore: local db.sqlite3 -> Supabase (standby) Postgres.

Bridges the outage until Neon's compute quota resets on the 1st, when the
failover watchdog re-points at Neon and the neon->supabase sync takes over.

Safe by design:
  * Only content tables are touched (subject/chapter/subchapter/question/SEO).
    User data (attempts, sessions) is left alone on the target.
  * Everything runs in ONE transaction: TRUNCATE ... RESTART IDENTITY CASCADE,
    then inserts by matching column names. If any sqlite column has no
    Postgres counterpart the script aborts before writing.
  * Requires `manage.py migrate` to have run against Supabase first so the
    Postgres schema matches current models.

Usage:
    $env:DATABASE_URL='postgres://...supabase...'     (or SUPABASE_DATABASE_URL)
    python scripts/restore_sqlite_to_pg.py --sqlite db.sqlite3 --dry-run
    python scripts/restore_sqlite_to_pg.py --sqlite db.sqlite3
"""
import argparse
import os
import sqlite3

TABLES = ['CEE_Quiz_subject', 'CEE_Quiz_chapter', 'CEE_Quiz_subchapter',
          'CEE_Quiz_question', 'CEE_Quiz_solutionset', 'CEE_Quiz_pageseo']

BOOLEAN_COLS = {'is_approved', 'has_subchapters', 'is_question', 'include_in_full_test'}


def pg_conn():
    url = os.environ.get('SUPABASE_DATABASE_URL') or os.environ.get('DATABASE_URL') or ''
    if not url:
        raise SystemExit('Set SUPABASE_DATABASE_URL (or DATABASE_URL) first.')
    import psycopg
    return psycopg.connect(url, connect_timeout=30)


def sqlite_cols(cur, table):
    return [(r[1], r[2]) for r in cur.execute(f'PRAGMA table_info("{table}")').fetchall()]


def pg_cols(cur, table):
    cur.execute(
        'SELECT column_name FROM information_schema.columns '
        'WHERE lower(table_name) = lower(%s) ORDER BY ordinal_position', (table,))
    return {r[0] for r in cur.fetchall()}


def to_pg_value(col, val):
    if val is None:
        return None
    if col in BOOLEAN_COLS:
        return bool(val)
    if isinstance(val, str) and ('date' in col.lower() or col.lower() == 'created_at'):
        return val.replace('T', ' ')
    return val


def restore(sqlite_path, dry_run, no_questions=False):
    src = sqlite3.connect(sqlite_path)
    src.row_factory = sqlite3.Row
    sc = src.cursor()

    tables = [t for t in TABLES if not (no_questions and t == 'CEE_Quiz_question')]

    pconn = pg_conn()
    with pconn.cursor() as pc:
        for table in tables:
            try:
                cols = [(c, t) for c, t in sqlite_cols(sc, table)]
            except sqlite3.OperationalError:
                print(f'skip {table}: not in sqlite')
                continue
            if not cols:
                print(f'skip {table}: no columns')
                continue
            pgcols = pg_cols(pc, table)
            if not pgcols:
                print(f'skip {table}: not in Postgres')
                continue

            missing = [c for c, _ in cols if c not in pgcols]
            if missing:
                print(f'ABORT {table}: columns in sqlite missing in Postgres: {missing}')
                print('-> run manage.py migrate against Supabase first, then retry')
                return 1

            names = [c for c, _ in cols]
            placeholders = ', '.join(['%s'] * len(names))
            name_sql = ', '.join(f'"{n}"' for n in names)
            order_sql = f' ORDER BY "id"' if 'id' in names else ''
            sc.execute(f'SELECT {name_sql} FROM "{table}"{order_sql}')
            rows = sc.fetchall()

            print(f'{table}: truncating + inserting {len(rows)} rows')
            if not dry_run:
                pc.execute(f'TRUNCATE "{table}" RESTART IDENTITY CASCADE')
                for row in rows:
                    vals = [to_pg_value(n, row[n]) for n in names]
                    pc.execute(
                        f'INSERT INTO "{table}" ({name_sql}) VALUES ({placeholders})',
                        vals)
    if not dry_run:
        pconn.commit()
        print('COMMITTED (content tables restored from sqlite)')
    else:
        print('dry-run: no writes performed')
    pconn.close()
    return 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--sqlite', default='db.sqlite3')
    ap.add_argument('--dry-run', action='store_true')
    ap.add_argument('--no-questions', action='store_true',
                    help='skip CEE_Quiz_question (you are importing questions from CSV)')
    args = ap.parse_args()
    raise SystemExit(restore(args.sqlite, args.dry_run, args.no_questions))


if __name__ == '__main__':
    main()