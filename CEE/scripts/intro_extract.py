"""Extract CEE_Quiz_Intro_Content_Kit.xlsx into JSON work files.

Writes scripts/intros/kit_*.json (metadata + prompt per page) and
scripts/intros/db_rows.json (current DB row inventory for alignment).
"""
import json
import os
import re

import openpyxl
import psycopg

KIT = r'C:\Users\ASUS\Downloads\CEE_Quiz_Intro_Content_Kit.xlsx'
OUT = os.path.join(os.path.dirname(__file__), 'intros')
URL = os.environ.get('SUPABASE_DATABASE_URL') or os.environ.get('DATABASE_URL') or ''
if not URL:
    raise SystemExit('Set SUPABASE_DATABASE_URL (or DATABASE_URL) first.')


def norm(s):
    if not s:
        return ''
    s = re.sub(r'\s+', ' ', str(s)).strip().lower()
    s = re.sub(r'[/\\]+', ' ', s)
    return s


def main():
    os.makedirs(OUT, exist_ok=True)
    wb = openpyxl.load_workbook(KIT, read_only=True, data_only=True)

    def rows(name):
        ws = wb[name]
        it = ws.iter_rows(values_only=True)
        header = [str(h).strip() if h else h for h in next(it)]
        out = []
        for r in it:
            if not any(v is not None and str(v).strip() for v in r):
                continue
            out.append(dict(zip(header, r)))
        return out

    subjects = rows('Subjects')
    units = rows('Units')
    subchapters = rows('Subchapters')
    sets = rows('Solution Sets')

    with open(os.path.join(OUT, 'kit_subjects.json'), 'w', encoding='utf-8') as f:
        json.dump(subjects, f, ensure_ascii=False, indent=1)
    with open(os.path.join(OUT, 'kit_units.json'), 'w', encoding='utf-8') as f:
        json.dump(units, f, ensure_ascii=False, indent=1)
    with open(os.path.join(OUT, 'kit_subchapters.json'), 'w', encoding='utf-8') as f:
        json.dump(subchapters, f, ensure_ascii=False, indent=1)
    with open(os.path.join(OUT, 'kit_sets.json'), 'w', encoding='utf-8') as f:
        json.dump(sets, f, ensure_ascii=False, indent=1)

    # DB inventory
    db = {'subjects': [], 'chapters': [], 'subchapters': [], 'sets': []}
    with psycopg.connect(URL, connect_timeout=30) as conn, conn.cursor() as cur:
        cur.execute('SELECT id, name, intro_text FROM "CEE_Quiz_subject" ORDER BY id')
        for sid, name, itext in cur.fetchall():
            db['subjects'].append({'id': sid, 'name': name,
                                   'intro_len': len(itext or ''), 'has_intro': bool(itext)})
        cur.execute('SELECT id, subject_id, name FROM "CEE_Quiz_chapter" ORDER BY id')
        for cid, subj, name in cur.fetchall():
            db['chapters'].append({'id': cid, 'subject_id': subj, 'name': name})
        cur.execute('SELECT id, chapter_id, name FROM "CEE_Quiz_subchapter" ORDER BY id')
        for sid, cid, name in cur.fetchall():
            db['subchapters'].append({'id': sid, 'chapter_id': cid, 'name': name})
        cur.execute('SELECT id, chapter_id, set_number FROM "CEE_Quiz_solutionset" ORDER BY chapter_id, set_number')
        for sid, cid, n in cur.fetchall():
            db['sets'].append({'id': sid, 'chapter_id': cid, 'set_number': n})

    with open(os.path.join(OUT, 'db_rows.json'), 'w', encoding='utf-8') as f:
        json.dump(db, f, ensure_ascii=False, indent=1)

    print('subjects:', len(subjects))
    print('units:', len(units))
    print('subchapters:', len(subchapters))
    print('solution-set prompts:', len(sets))
    print('db subjects:', len(db['subjects']), 'chapters:', len(db['chapters']),
          'subchapters:', len(db['subchapters']), 'sets:', len(db['sets']))

    # Alignment report
    print('\n--- kit unit <-> db chapter (by id) ---')
    dbch = {c['id']: c for c in db['chapters']}
    for u in units:
        cid = u['Chapter ID']
        d = dbch.get(cid)
        match = (d is not None and norm(d['name']) == norm(u['Unit Name']))
        print(f"  {cid}: kit='{u['Unit Name']}' db='{d['name'] if d else 'MISSING'}' match={match}")

    print('\n--- subchapter alignment (kit row count vs db count per chapter) ---')
    from collections import Counter
    dbsc = Counter(sc['chapter_id'] for sc in db['subchapters'])
    ksc = Counter(sc['Chapter ID'] for sc in subchapters)
    for cid in sorted(set(dbsc) | set(ksc)):
        if dbsc[cid] != ksc[cid]:
            print(f"  chapter {cid}: db={dbsc[cid]} kit={ksc[cid]}")
            kit_names = [norm(sc['Subchapter']) for sc in subchapters if sc['Chapter ID'] == cid]
            db_names = [norm(sc['name']) for sc in db['subchapters'] if sc['chapter_id'] == cid]
            for n in kit_names:
                if n and n not in db_names:
                    print(f"    kit-only: {n}")
            for n in db_names:
                if n and n not in kit_names:
                    print(f"    db-only : {n}")


if __name__ == '__main__':
    main()