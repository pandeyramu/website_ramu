"""Import CEE_Quiz_question.csv into Supabase's CEE_Quiz_question table.

Keeps the original ids (same id-space as db.sqlite3 / solved-set references),
maps empty sub_chapter_id to NULL.

Usage:
    python scripts/import_questions_csv.py C:\\Users\\ASUS\\Downloads\\CEE_Quiz_question.csv
"""
import argparse

import csv

COLS = ['id', 'question_text', 'option_a', 'option_b', 'option_c', 'option_d',
        'correct_option', 'chapter_id', 'sub_chapter_id', 'solution', 'verified']

INT_COLS = {'id', 'chapter_id', 'sub_chapter_id'}
BOOL_COLS = {'verified'}


def load_url():
    for line in open('scripts/.env', encoding='utf-8'):
        if line.startswith('SUPABASE_DATABASE_URL='):
            return line.split('=', 1)[1].strip()
    raise SystemExit('SUPABASE_DATABASE_URL not found in scripts/.env')


def esc(val):
    if val is None:
        return '\\N'
    if isinstance(val, bool):
        val = str(val).lower()
    val = str(val)
    return val.replace('\\', '\\\\').replace('\t', '\\t').replace('\n', '\\n').replace('\r', '\\r')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('csv', help='path to CEE_Quiz_question.csv')
    args = ap.parse_args()

    url = load_url()
    import psycopg

    rows = 0
    with open(args.csv, encoding='utf-8') as fr, psycopg.connect(url, connect_timeout=30) as conn:
        with conn.cursor() as cur:
            copy_sql = 'COPY "CEE_Quiz_question" ("%s") FROM STDIN' % '", "'.join(COLS)
            with cur.copy(copy_sql) as cp:
                for raw in csv.DictReader(fr):
                    vals = []
                    for col in COLS:
                        v = raw.get(col, '')
                        if v == '' and col in INT_COLS:
                            v = None
                        elif col in BOOL_COLS:
                            v = str(v).strip().lower() in ('true', '1', 't')
                        elif v == '':
                            v = ''
                        vals.append(esc(v))
                    cp.write(('\t'.join(vals) + '\n').encode('utf-8'))
                    rows += 1
        conn.commit()
    print(f'COMMITTED {rows} question rows.')


if __name__ == '__main__':
    main()