"""Regenerate CEE_Quiz_solutionset.question_ids from the CSV's id space.

sqlite's stored question_ids belong to a different (Neon) lineage, so they
resolve in neither db.sqlite3 nor CEE_Quiz_question.csv. This rebuilds each
set's question_ids by deterministically sampling questions FROM ITS OWN
chapter in the CSV, keeping the set_number/title/intro_text, so every solved-
set page works immediately. Oct-1 Neon sync will replace these with the
authoritative sets.

Usage: python scripts/fix_solutionsets.py <path-to-CEE_Quiz_question.csv>
"""
import argparse
import csv
import random
import sqlite3

import psycopg


def load_url():
    for line in open('scripts/.env', encoding='utf-8'):
        if line.startswith('SUPABASE_DATABASE_URL='):
            return line.split('=', 1)[1].strip()
    raise SystemExit('SUPABASE_DATABASE_URL not found in scripts/.env')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('csv')
    args = ap.parse_args()

    by_chapter = {}
    with open(args.csv, encoding='utf-8') as f:
        for row in csv.DictReader(f):
            ch = int(row['chapter_id'])
            by_chapter.setdefault(ch, []).append(int(row['id']))
    print('chapters with questions in CSV:', len(by_chapter))

    con = sqlite3.connect(r'db.sqlite3')
    cur = con.cursor()
    cur.execute('SELECT id, chapter_id, set_number, title, intro_text, question_ids '
                'FROM CEE_Quiz_solutionset ORDER BY id')
    rows = cur.fetchall()
    print('sqlite solutionsets:', len(rows))

    url = load_url()
    fixed = 0
    with psycopg.connect(url, connect_timeout=30) as conn:
        with conn.cursor() as pc:
            for sid, ch, setno, title, intro, qids in rows:
                if setno == 0:
                    # fallback for any row w/o set number
                    setseed = sid
                else:
                    setseed = setno or sid
                rng = random.Random(f'{ch}:{setseed}')
                pool = by_chapter.get(ch) or []
                want = len([x for x in (qids or '').split(',') if x.strip()])
                want = max(10, want) if want else 10
                if len(pool) < want:
                    want = len(pool)
                chosen = rng.sample(pool, want)
                chosen = sorted(chosen)
                new_qids = ','.join(str(i) for i in chosen)
                pc.execute(
                    'UPDATE "CEE_Quiz_solutionset" SET question_ids=%s WHERE id=%s',
                    (new_qids, sid))
                fixed += 1
        conn.commit()
    print('updated', fixed, 'solutionsets with regenerated question_ids')

    # verify all now resolve
    with psycopg.connect(url) as conn:
        with conn.cursor() as pc:
            pc.execute('SELECT id, chapter_id, question_ids FROM "CEE_Quiz_solutionset"')
            bad = 0
            for sid, ch, qids in pc.fetchall():
                for x in (qids or '').split(','):
                    if x.strip() and int(x) not in by_chapter.get(ch, []):
                        bad += 1
            print('unresolved refs after fix:', bad)


if __name__ == '__main__':
    main()