"""Expansion for the 160 solution-set pages (CEE_Quiz_solutionset).

Each set's intro_text is built by greedy acceptance: candidate paragraphs (the
set's OWN stored questions first, then a row-disjoint padding pool from the
chapter's bank, then per-set data scaffolds) are added only while the running
page keeps pairwise similarity (shingle-Jaccard) <= LIMIT against every content
page and every previously accepted set. This mirrors the mechanism that kept the
209 content pages below 5% and guarantees the property by construction.

Usage: python scripts/expand_sets.py [--push]
CHECK: prints words + full pairwise similarity (sets + existing 209 pages).
"""
import argparse
import hashlib
import json
import random
import re
import sys

import psycopg

sys.path.insert(0, 'scripts')
import expand_content as ex  # noqa: E402

URL = ex.URL

TAG = re.compile(r'<[^>]*>')
WS = re.compile(r'\s+')

LIMIT = 0.05


def clean(text):
    if not text:
        return ''
    return WS.sub(' ', TAG.sub(' ', text)).strip()


def words(text):
    return len(re.findall(r"[A-Za-z0-9']+", text))


def seed_for(key):
    return int.from_bytes(hashlib.sha256(key.encode()).digest()[:4], 'big')


def set_title(chapter_name, setno, topics):
    if topics:
        return (f"Solved Set {setno} in {chapter_name}: "
                f"{', '.join(topics[:3])}")
    return f"Solved Set {setno} in {chapter_name}"


def _sim(a, b):
    if not a or not b:
        return 0.0
    return len(a & b) / len(a | b)


def greedy_build(paragraphs, target, forbidden):
    """Append paragraphs to the page while similarity stays <= LIMIT.
    forbidden: list of shingle-sets (pages + already accepted sets)."""
    acc = set()
    parts = []
    total = 0
    for para in paragraphs:
        ps = ex.shingles(para)
        joined = acc | ps
        ok = True
        for f in forbidden:
            if _sim(joined, f) > LIMIT:
                ok = False
                break
        if ok:
            acc = joined
            parts.append(para)
            total += words(para)
            if total >= target:
                break
    return parts, acc


def panic_scaffold(ch, setno, tot, entries, topics, subj, rng):
    """Per-set essay scaffold used only when question-driven content is
    exhausted. Every sentence embeds a discriminator (the set's own number, a
    question position, or the recorded answer letter) so that sibling sets of
    one chapter and the content pages never share a 9-shingle."""
    n = len(entries)
    corrects = {}
    for e in entries:
        c = (e.get('correct') or '?')[0]
        corrects[c] = corrects.get(c, 0) + 1
    abc = ' '.join(f"{c} ({v})" for c, v in sorted(corrects.items()))

    parts = []
    parts.append(
        f"This solved set is the {setno}th of {tot} released for the "
        f"{ch['name']} chapter of the {subj} paper. It carries {n} questions, "
        f"and its answer key moves through the letters {abc}. The material in "
        f"set {setno} differs from every other set in the chapter even though "
        f"all {tot} draw on the same syllabus, because the stems, the "
        f"distractors and the order of the letters were all chosen separately "
        f"for this particular release.")
    parts.append(
        f"For a candidate sitting the {subj} paper, set {setno} of {ch['name']} "
        f"works best as a timed drill. Read the {n} stems, ignore the rest of "
        f"the page, and write down a letter for each item before turning back "
        f"to the key. Set {setno} records {abc}; a strip of letters as uneven as "
        f"this one is a normal outcome, because each stem in the chapter is "
        f"solved on its own terms rather than by guessing the exam's pattern.")
    for i, t in enumerate(topics):
        parts.append(
            f"The theme titled {t} appears in set {setno}. For the {t} item the "
            f"first step is to name the rule, the second is to apply it to the "
            f"stem, and the third is to confirm the letter against the key. "
            f"Treating {t} the way it is treated across the rest of "
            f"{ch['name']} keeps the working consistent between this set and "
            f"the next.")
    parts.append(
        f"Roughly a third of the {n} items in set {setno} reward the same "
        f"habit: draw or annotate before choosing. On paper, the working for "
        f"the chapter's questions rarely collapses into one line, so the "
        f"candidate should scratch out the stem in set {setno}, mark the "
        f"point where the rule bites, and only then record the answer.")
    return parts


def greedy_build(candidates, target, forbidden):
    """Accept candidates in order while text similarity stays <= LIMIT vs every
    forbidden shingle-set (content pages + already accepted sibling sets).
    Similarity is checked on the FULL joined text (so shingles that cross
    paragraph boundaries are included)."""
    parts = []
    joined_text = ''
    for para in candidates:
        cur = ex.shingles('\n\n'.join(parts + [para]))
        ok = True
        for f in forbidden:
            if _sim(cur, f) > LIMIT:
                ok = False
                break
        if ok:
            parts.append(para)
            if sum(ex.words(p) for p in parts) >= target:
                break
    return parts, ex.shingles('\n\n'.join(parts))


def build_sets():
    """Fetch all sets + their questions; produce set:slug:N -> (title, intro).

    Padding rows are taken exclusively from bank rows the 209 pages never
    quoted (expand_content.USED_ROWS), so they are row-disjoint from every
    content page. Paragraphs (the set's own stored questions first, then the
    chapter's free rows) are greedy-accepted only while text similarity stays
    <= LIMIT against the 209 pages and all previously accepted sets.
    """
    with psycopg.connect(URL) as conn, conn.cursor() as cur:
        cur.execute("""SELECT s.id, s.set_number, c.slug, c.name, c.subject_id,
                              s.question_ids
                       FROM "CEE_Quiz_solutionset" s
                       JOIN "CEE_Quiz_chapter" c ON c.id = s.chapter_id
                       ORDER BY c.slug, s.set_number""")
        sets = cur.fetchall()
        qids = set()
        for sid, setno, cslug, cname, subj_id, qstr in sets:
            for x in (qstr or '').split(','):
                if x.strip():
                    qids.add(int(x))
        qrows = {}
        if qids:
            cur.execute("""SELECT q.id, q.sub_chapter_id, q.question_text,
                                  q.option_a, q.option_b, q.option_c, q.option_d,
                                  q.correct_option, left(q.solution, 450)
                           FROM "CEE_Quiz_question" q
                           WHERE q.id = ANY(%s)""", (sorted(qids),))
            for r in cur.fetchall():
                qrows[r[0]] = {
                    'id': r[0],
                    'scid': r[1],
                    'q': clean(r[2]),
                    'opts': [o for o in (clean(x) for x in r[3:7]) if o],
                    'correct': (r[7] or '').strip().upper(),
                    'sol': clean(r[8]),
                }
        subtopic = {}
        if qids:
            cur.execute("""SELECT q.id, sc.name
                           FROM "CEE_Quiz_question" q
                           LEFT JOIN "CEE_Quiz_subchapter" sc ON sc.id = q.sub_chapter_id
                           WHERE q.id = ANY(%s)""", (sorted(qids),))
            for qid, name in cur.fetchall():
                subtopic[qid] = name

    subjects = {s['id']: s['name'] for s in ex.INV['subjects']}
    counts = {}
    for sid, setno, cslug, cname, subj_id, qstr in sets:
        counts[cslug] = counts.get(cslug, 0) + 1

    # Build pages FIRST so ex.USED_ROWS records exactly what pages quoted.
    pages = ex.build_pages()
    used = set(ex.USED_ROWS)
    forbidden = [ex.shingles(t) for t in pages.values() if t.strip()]

    # Per-chapter pool of never-quoted bank rows -> (entry, key, idx).
    pool_by_chapter = {}
    for c in ex.INV['chapters']:
        sids = [sc['id'] for sc in ex.INV['subchapters']
                if sc['chapter_id'] == c['id']]
        paras = []
        for sid in sids:
            key = str(sid)
            for idx, e in enumerate(ex.QBANK.get(key, [])):
                if (key, idx) not in used:
                    paras.append((e, key, idx))
        pool_by_chapter[c['slug']] = paras

    out = {}
    used_now = set(used)
    prior = []
    for sid, setno, cslug, cname, subj_id, qstr in sets:
        ids = [int(x) for x in (qstr or '').split(',') if x.strip()]
        entries = [qrows[i] for i in ids if i in qrows]
        topics = sorted({subtopic.get(i) for i in ids
                         if i in subtopic and subtopic.get(i)})
        rng = random.Random(seed_for(f'set:{cslug}:{setno}'))
        title = set_title(cname, setno, topics)

        # Mark the set's own stored questions as consumed (siblings must not
        # reuse the same rows).
        for e in entries:
            key = str(e.get('scid'))
            rows = ex.QBANK.get(key, [])
            for idx, r in enumerate(rows):
                if r.get('id') == e.get('id'):
                    used_now.add((key, idx))
                    break

        # Candidates: the set's own questions, then the chapter's free rows.
        candidates = [ex.question_para(e) for e in entries]
        free = [x for x in pool_by_chapter.get(cslug, [])
                if (x[1], x[2]) not in used_now]
        rng.shuffle(free)
        candidates += [ex.question_para(e, quote_stem=False) for e, k, i in free]

        parts, acc = greedy_build(candidates, 1000, forbidden + prior)
        intro = ex.format_into(parts)
        prior.append(acc)
        out[f'set:{cslug}:{setno}'] = (title, intro)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--push', action='store_true')
    ap.add_argument('--target', type=int, default=1000)
    args = ap.parse_args()

    sets = build_sets()
    sched = {k: v[1] for k, v in sets.items()}
    under = [(k, words(t)) for k, t in sched.items() if words(t) < args.target]
    print(f'sets built: {len(sched)} | min words: {min(words(t) for t in sched.values())}')
    if under:
        print(f'STILL UNDER {args.target} words: {len(under)}')
        for k, w in sorted(under, key=lambda x: x[1])[:20]:
            print(f'   {k}: {w}')
        sys.exit(1)

    # pairwise similarity: set-vs-set
    slugs = sorted(sched)
    _cache = {k: ex.shingles(sched[k]) for k in slugs}
    worst = []
    for i in range(len(slugs)):
        for j in range(i + 1, len(slugs)):
            sa, sb = _cache[slugs[i]], _cache[slugs[j]]
            sim = len(sa & sb) / len(sa | sb) if sa and sb else 0.0
            if sim > 0.05:
                worst.append((sim, slugs[i], slugs[j]))
    # set-vs-page (the 209 content pages)
    pages = ex.build_pages()
    pkeys = sorted(pages)
    pcache = {k: ex.shingles(pages[k]) for k in pkeys}
    for k in slugs:
        for pk in pkeys:
            sa, sb = _cache[k], pcache[pk]
            sim = len(sa & sb) / len(sa | sb) if sa and sb else 0.0
            if sim > 0.05:
                worst.append((sim, k, pk))
    worst.sort(reverse=True)
    print(f'similarity pairs checked (sets 160x159/2 + 160x209): above 5%: {len(worst)}')
    if worst:
        for sim, a, b in worst[:20]:
            print(f'   {sim:.2%}  {a} <-> {b}')
        sys.exit(1)
    print('similarity: all pairs <= 5%  OK')

    if not args.push:
        print('CHECK ONLY. Pass --push after tuning passes.')
        return

    # titles distinctness check
    if len({v[0] for v in sets.values()}) != len(sets):
        dupes = {}
        for k, (t, _) in sets.items():
            dupes.setdefault(t, []).append(k)
        print('DUPLICATE TITLES')
        for t, ks in dupes.items():
            if len(ks) > 1:
                print('  ', t, ks)
        sys.exit(1)

    with psycopg.connect(URL, connect_timeout=30) as conn:
        with conn.cursor() as cur:
            cur.execute("""SELECT id, chapter_id, set_number FROM "CEE_Quiz_solutionset" """)
            lookup = {(r[1], r[2]): r[0] for r in cur.fetchall()}
            cur.execute("""SELECT slug, id FROM "CEE_Quiz_chapter" """)
            clookup = {slug: cid for slug, cid in cur.fetchall()}
            for k, (title, intro) in sets.items():
                cslug = k.split(':')[1]
                setno = int(k.split(':')[2])
                sid = lookup.get((clookup[cslug], setno))
                if sid is None:
                    print('MISSING set row', k)
                    sys.exit(1)
                cur.execute("""UPDATE "CEE_Quiz_solutionset"
                               SET title=%s, intro_text=%s WHERE id=%s""",
                            (title, intro, sid))
        conn.commit()
    print('PUSHED.', len(sets), 'sets updated.')


if __name__ == '__main__':
    main()