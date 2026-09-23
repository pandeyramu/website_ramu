"""Compile authored page content into final intro_text documents, validate
word counts and pairwise similarity, and push to the database.

Usage:
  python scripts/compile_content.py            # build + check only (no DB)
  python scripts/compile_content.py --push     # build + check + write to DB
"""
import argparse
import hashlib
import re
import sys
from difflib import SequenceMatcher

import psycopg

sys.path.insert(0, 'scripts')
import content_data  # noqa: E402

URL = ''
for line in open('scripts/.env', encoding='utf-8'):
    if line.startswith('SUPABASE_DATABASE_URL='):
        URL = line.split('=', 1)[1].strip()


def words(text):
    return len(re.findall(r"[A-Za-z0-9']+", text))


def norm(text):
    return re.sub(r'\s+', ' ', text.lower())


def shingles(text, n=9):
    t = re.sub(r'[^a-z0-9 ]', ' ', norm(text))
    toks = t.split()
    return set(' '.join(toks[i:i + n]) for i in range(len(toks) - n + 1))


def similarity(a, b):
    sa, sb = shingles(a), shingles(b)
    if not sa or not sb:
        return 0.0
    return len(sa & sb) / len(sa | sb)


def build_pages():
    pages = {}  # slug -> text

    for slug, sub in content_data.SUBJECTS.items():
        intro = '\n\n'.join(sub['core'])
        pages[f'subject:{slug}'] = intro

    for slug, ch in content_data.CHAPTERS.items():
        intro = '\n\n'.join(ch['core'])
        pages[f'chapter:{slug}'] = intro

    return pages


def check(pages, target_words=1000):
    errors = []
    min_word = min(words(t) for t in pages.values())
    print(f'pages: {len(pages)} | min words: {min_word} | target: {target_words}')
    for slug, text in pages.items():
        if words(text) < target_words:
            errors.append(f'{slug}: only {words(text)} words')
    slugs = sorted(pages)
    worst = []
    for i in range(len(slugs)):
        for j in range(i + 1, len(slugs)):
            sim = similarity(pages[slugs[i]], pages[slugs[j]])
            if sim > 0.05:
                worst.append((sim, slugs[i], slugs[j]))
    worst.sort(reverse=True)
    print(f'pairs compared: {len(slugs) * (len(slugs) - 1) // 2}')
    if worst:
        print(f'PAIRS ABOVE 5%: {len(worst)}')
        for sim, a, b in worst[:10]:
            print(f'   {sim:.2%}  {a} <-> {b}')
    else:
        print('similarity: all pairs <= 5%  OK')
    return errors, worst


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--push', action='store_true')
    args = ap.parse_args()

    pages = build_pages()
    errors, _ = check(pages)
    if errors:
        print('BLOCKING: word count failures:')
        for e in errors:
            print('  ', e)
        sys.exit(1)

    if not args.push:
        print('CHECK ONLY - no database writes. Pass --push to apply.')
        return

    with psycopg.connect(URL, connect_timeout=30) as conn:
        with conn.cursor() as cur:
            for slug, text in pages.items():
                kind, name = slug.split(':', 1)
                table = {'subject': 'CEE_Quiz_subject',
                         'chapter': 'CEE_Quiz_chapter'}[kind]
                cur.execute(f'UPDATE "{table}" SET intro_text=%s WHERE slug=%s',
                            (text, name))
                print(f'updated {kind} {name}: {words(text)} words')
        conn.commit()
    print('PUSHED. Now verifying from database...')
    with psycopg.connect(URL) as conn:
        with conn.cursor() as cur:
            for kind, table, slugcol in [('subject', 'CEE_Quiz_subject', 'slug'),
                                         ('chapter', 'CEE_Quiz_chapter', 'slug')]:
                cur.execute(f'SELECT {slugcol}, intro_text FROM "{table}"')
                for slug, text in cur.fetchall():
                    pages[f'{kind}:{slug}'] = text
            errors, _ = check(pages)
    if errors:
        sys.exit(1)
    print('ALL VERIFIED OK')


if __name__ == '__main__':
    main()