"""Dump each solution set's subtopic spread (+ counts) to guide unique intros."""
import json
import os
import re
import sys

import psycopg

URL = os.environ.get('SUPABASE_DATABASE_URL') or os.environ.get('DATABASE_URL') or ''
if not URL:
    raise SystemExit('Set SUPABASE_DATABASE_URL (or DATABASE_URL) first.')


def norm(s):
    return re.sub(r'\s+', ' ', str(s or '')).strip()


def main():
    out = {}
    with psycopg.connect(URL, connect_timeout=30) as conn, conn.cursor() as cur:
        cur.execute("""SELECT s.chapter_id, s.set_number, c.name, s.question_ids
                       FROM "CEE_Quiz_solutionset" s
                       JOIN "CEE_Quiz_chapter" c ON c.id = s.chapter_id
                       ORDER BY s.chapter_id, s.set_number""")
        sets = cur.fetchall()
        qids = set()
        for _, _, _, qstr in sets:
            for x in (qstr or '').split(','):
                if x.strip():
                    qids.add(int(x))
        subtop = {}
        if qids:
            cur.execute("""SELECT q.id, sc.name
                           FROM "CEE_Quiz_question" q
                           LEFT JOIN "CEE_Quiz_subchapter" sc ON sc.id = q.sub_chapter_id
                           WHERE q.id = ANY(%s)""", (sorted(qids),))
            for qid, name in cur.fetchall():
                subtop[qid] = name
        for cid, setno, cname, qstr in sets:
            ids = [int(x) for x in (qstr or '').split(',') if x.strip()]
            topics = sorted({norm(subtop.get(i))
                             for i in ids if i in subtop and norm(subtop.get(i))})
            out[f'{cid}|{setno}'] = {'chapter': norm(cname), 'n': len(ids), 'topics': topics}

    with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'set_topics.json'),
              'w', encoding='utf-8') as f:
        json.dump(out, f, ensure_ascii=False, indent=1)
    for k in sorted(out, key=lambda x: int(x.split('|')[0]) * 10 + int(x.split('|')[1])):
        print(k, '|', out[k]['chapter'], '| n=', out[k]['n'], '|', ', '.join(out[k]['topics']))


if __name__ == '__main__':
    main()