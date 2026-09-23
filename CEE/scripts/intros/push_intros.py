"""Push rewritten intros from scripts/intros/intros.json into Supabase.

intros.json layout:
{
  "subjects":    {"<subject name>": "text", ...}               # Physics, Chemistry, Zoology, Botany, MAT
  "chapters":    {"<chapter_id>": "text", ...}                 # 1..32
  "subchapters": {"<chapter_id>|<subchapter name>": "text", ...}
  "sets":        {"<chapter_id>|<set_number>": "text", ...}    # set_number 1..5
}

Usage: python scripts/intros/push_intros.py [--check-only]
"""
import argparse
import json
import os
import re
import sys

import psycopg

URL = os.environ.get('SUPABASE_DATABASE_URL') or os.environ.get('DATABASE_URL') or ''
if not URL:
    raise SystemExit('Set SUPABASE_DATABASE_URL (or DATABASE_URL) first.')
BASE = os.path.dirname(os.path.abspath(__file__))
INTROS = os.path.join(BASE, 'intros.json')


def norm(s):
    if not s:
        return ''
    return re.sub(r'\s+', ' ', str(s)).strip().lower()


def words(t):
    return len(re.findall(r"[A-Za-z0-9']+", t or ''))


def load():
    if not os.path.exists(INTROS):
        return {}

    def _got(d):
        return {k: v for k, v in d.items() if v and str(v).strip()}

    with open(INTROS, encoding='utf-8') as f:
        data = json.load(f)
    return {k: _got(data.get(k) or {}) for k in ('subjects', 'chapters', 'subchapters', 'sets')}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--check-only', action='store_true')
    args = ap.parse_args()

    data = load()
    n_sub = len(data['subjects'])
    n_ch = len(data['chapters'])
    n_sc = len(data['subchapters'])
    n_set = len(data['sets'])
    print(f'intros ready: subjects={n_sub}/5 chapters={n_ch}/32 subchapters={n_sc}/172 sets={n_set}/160')

    with psycopg.connect(URL, connect_timeout=30) as conn, conn.cursor() as cur:
        # --- resolve subjects by name ---
        cur.execute('SELECT id, name FROM "CEE_Quiz_subject"')
        subj_by_name = {norm(n): sid for sid, n in cur.fetchall()}
        subj_id = {}
        for key in data['subjects']:
            sid = subj_by_name.get(norm(key))
            if sid is None:
                print('MISSING subject', key)
                sys.exit(1)
            subj_id[key] = sid

        # --- resolve chapters by id ---
        cur.execute('SELECT id FROM "CEE_Quiz_chapter"')
        valid_ids = {r[0] for r in cur.fetchall()}
        for key in data['chapters']:
            if int(key) not in valid_ids:
                print('MISSING chapter', key)
                sys.exit(1)

        # --- resolve subchapters by chapter_id + name ---
        cur.execute('SELECT id, chapter_id, name FROM "CEE_Quiz_subchapter"')
        scmap = {}
        for sid, cid, name in cur.fetchall():
            scmap[(cid, norm(name))] = sid
        sc_id = {}
        for key in data['subchapters']:
            cid, name = key.split('|', 1)
            sid = scmap.get((int(cid), norm(name)))
            if sid is None:
                print('MISSING subchapter', key)
                print('  close matches:', [k for k in scmap if k[0] == int(cid)][:10])
                sys.exit(1)
            sc_id[key] = sid

        # --- resolve sets by chapter_id + set_number ---
        cur.execute('SELECT id, chapter_id, set_number FROM "CEE_Quiz_solutionset"')
        setmap = {}
        for sid, cid, n in cur.fetchall():
            setmap[(cid, n)] = sid
        set_id = {}
        for key in data['sets']:
            cid, n = key.split('|', 1)
            sid = setmap.get((int(cid), int(n)))
            if sid is None:
                print('MISSING set', key)
                sys.exit(1)
            set_id[key] = sid

        if args.check_only:
            print('CHECK ONLY — all rows resolved.')
            return

        for key, text in data['subjects'].items():
            cur.execute('UPDATE "CEE_Quiz_subject" SET intro_text=%s WHERE id=%s',
                        (text, subj_id[key]))
        for key, text in data['chapters'].items():
            cur.execute('UPDATE "CEE_Quiz_chapter" SET intro_text=%s WHERE id=%s',
                        (text, int(key)))
        for key, text in data['subchapters'].items():
            cur.execute('UPDATE "CEE_Quiz_subchapter" SET intro_text=%s WHERE id=%s',
                        (text, sc_id[key]))
        for key, text in data['sets'].items():
            cur.execute('UPDATE "CEE_Quiz_solutionset" SET intro_text=%s WHERE id=%s',
                        (text, set_id[key]))
        conn.commit()
    print('PUSHED.')


if __name__ == '__main__':
    main()