"""Backfill missing MAT solved sets so all chapters have sets 1..5.

MAT chapters have zero/partial sets in the restore (sqlite held only 1).
Neon's sitemap had 5 sets per MAT chapter (20 pages). This creates the
missing set rows with topic-aware intros + sampled question_ids from the CSV.

Usage: python scripts/backfill_mat_sets.py <path-to-CEE_Quiz_question.csv>
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
            by_chapter.setdefault(int(row['chapter_id']), []).append(int(row['id']))

    # subchapter names per MAT chapter (for topic-aware intros)
    con = sqlite3.connect(r'db.sqlite3')
    cur = con.cursor()
    cur.execute('''SELECT c.id, c.name, c.slug, group_concat(sc.name, '; ')
                   FROM CEE_Quiz_chapter c
                   LEFT JOIN CEE_Quiz_subchapter sc ON sc.chapter_id = c.id
                   GROUP BY c.id ORDER BY c.id''')
    chapters = {c[0]: (c[1], c[2], c[3] or '') for c in cur.fetchall()}

    url = load_url()
    created = 0
    with psycopg.connect(url, connect_timeout=30) as conn:
        with conn.cursor() as pc:
            pc.execute('SELECT chapter_id, set_number FROM "CEE_Quiz_solutionset"')
            existing = {}
            for ch, n in pc.fetchall():
                existing.setdefault(ch, set()).add(n)

            for chid in (29, 30, 31, 32):
                name, slug, topics = chapters[chid]
                topics_list = [t.strip() for t in topics.split(';') if t.strip()][:8]
                topic_str = ', '.join(topics_list)
                pool = by_chapter.get(chid) or []
                for n in range(1, 6):
                    if n in existing.get(chid, set()):
                        continue
                    rng = random.Random(f'{chid}:mat-solved:{n}')
                    k = min(12, len(pool))
                    if k == 0:
                        continue
                    chosen = sorted(rng.sample(pool, k))
                    title = f'Solved Set {n} - {name}'
                    intro = (
                        f'A set of {k} solved {name} questions for the CEE MAT '
                        f'paper, covering {topic_str}. Read the worked solutions '
                        f'carefully to build speed and accuracy under pressure.'
                    )
                    pc.execute(
                        'INSERT INTO "CEE_Quiz_solutionset" '
                        '(set_number, title, intro_text, question_ids, chapter_id) '
                        'VALUES (%s, %s, %s, %s, %s)',
                        (n, title, intro, ','.join(str(i) for i in chosen), chid))
                    created += 1
        conn.commit()
    print('created', created, 'MAT solved sets')

    with psycopg.connect(url) as conn:
        with conn.cursor() as pc:
            pc.execute('SELECT chapter_id, set_number FROM "CEE_Quiz_solutionset" ORDER BY chapter_id, set_number')
            per = {}
            for ch, n in pc.fetchall():
                per.setdefault(ch, []).append(n)
            for ch in (29, 30, 31, 32):
                print(f'  chapter {ch}: sets {sorted(per.get(ch, []))}')
            pc.execute('SELECT count(*) FROM "CEE_Quiz_solutionset"')
            print('total solutionsets:', pc.fetchone()[0])


if __name__ == '__main__':
    main()