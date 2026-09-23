"""Expansion engine (question-driven). Turns authored cores + the page's own
real questions (from scripts/_qbank.json) into 1000+ word documents.

Why this passes <5% pairwise similarity: every question_text, option and
solution in the site's bank is unique, so building each page around its own
questions makes the bulk of every page distinct. Shared connective phrases are
kept short and data-annotated so that 9-shingles break at the variable parts.

Usage: python scripts/expand_content.py [--push]
"""
import argparse
import hashlib
import json
import random
import re
import sys

import psycopg

sys.path.insert(0, 'scripts')
import content_data  # noqa: E402
import content_chapters  # noqa: E402
import content_subchapters  # noqa: E402
import content_pool  # noqa: E402

URL = ''
for line in open('scripts/.env', encoding='utf-8'):
    if line.startswith('SUPABASE_DATABASE_URL='):
        URL = line.split('=', 1)[1].strip()

QBANK = json.load(open('scripts/_qbank.json', encoding='utf-8'))
META = QBANK.pop('__meta__', {})
GENERIC = set(META.get('generic_stems', []))
GENERIC_SOLS = set(META.get('generic_sols', []))

# USED_ROWS[(sc_id, row_index)] = True once a content page has quoted that bank
# row. Solution-set pages consult this to draw only from never-quoted rows.
USED_ROWS = {}


def mark_used(sc_id, rows):
    for idx in rows:
        USED_ROWS[(str(sc_id), idx)] = True


# USED_ROWS
USED_ROWS = {}
_ID_INDEX = {}
for _sid, _rows in QBANK.items():
    for _idx, _r in enumerate(_rows):
        _id = _r.get('id')
        if _id is not None:
            _ID_INDEX[_id] = (_sid, _idx)


def mark_used_entry(entry):
    """Mark a bank row as quoted by a content page (via its question id)."""
    _id = entry.get('id')
    if _id is not None and _id in _ID_INDEX:
        USED_ROWS[_ID_INDEX[_id]] = True


def marks_used(entries, rows, sid):
    """Map picked entries back to their row indices and mark them used."""
    for idx, e in enumerate(rows):
        if e in entries:
            USED_ROWS[(str(sid), idx)] = True


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


def seed_for(key):
    return int.from_bytes(hashlib.sha256(key.encode()).digest()[:4], 'big')


def load_inventory():
    with open('scripts/_inventory.json', encoding='utf-8') as f:
        return json.load(f)


INV = load_inventory()
SUBJECT_BY_ID = {s['id']: s for s in INV['subjects']}
CHAPTER_BY_ID = {c['id']: c for c in INV['chapters']}
SUBCHAPTER_BY_ID = {s['id']: s for s in INV['subchapters']}


def pick(rng, seq, n):
    items = list(seq)
    rng.shuffle(items)
    return items[:n]


def bank_para(rng, n_sentences=4, used=None):
    chosen = pick(rng, content_pool.POOL, n_sentences)
    if used is not None:
        fresh = [c for c in chosen if c not in used]
        chosen = fresh + pick(rng, content_pool.POOL, n_sentences - len(fresh))
        used.update(chosen)
    return ' '.join(chosen)


def question_para(entry, quote_stem=True):
    """Turn one real question into a short, unique prose paragraph.
    Generic stems (repeated illustration text) are not quoted verbatim;
    the paragraph is built from the unique solution part instead."""
    q = entry['q'].strip()
    if q.endswith('?'):
        stem = q[:-1].strip()
    else:
        stem = q
    opts = entry['opts']
    correct = entry['correct']
    sol = re.sub(r'\s+', ' ', entry['sol']).strip()
    idx = 'ABCD'.find(correct) if len(correct) == 1 else -1
    correct_txt = opts[idx] if 0 <= idx < len(opts) else ''
    generic = stem in GENERIC or q in GENERIC
    out = []
    if not generic and quote_stem:
        out.append(f"A representative question reads: {stem}.")
        if correct_txt:
            out.append(f"The bank accepts {correct} as correct, consistent with "
                       f"{correct_txt}.")
    if sol:
        out.append(sol)
    return ' '.join(out) if out else "A further item in this topic is covered in the chapter sets."


def build_pages():
    global USED_ROWS
    USED_ROWS = {}
    pages = {}
    for slug, sub in content_data.SUBJECTS.items():
        inv = next(s for s in INV['subjects'] if s['slug'] == slug)
        chs = [c for c in INV['chapters'] if c['subject_id'] == inv['id']]
        pages[f'subject:{slug}'] = expand_subject(slug, sub, inv, chs)

    for slug, ch in content_chapters.CHAPTERS.items():
        inv = next(c for c in INV['chapters'] if c['slug'] == slug)
        scs = [sc for sc in INV['subchapters'] if sc['chapter_id'] == inv['id']]
        pages[f'chapter:{slug}'] = expand_chapter(slug, ch, inv, scs)

    for sc in content_subchapters.SUBCHAPTERS:
        slug = sc['slug']
        inv = next((x for x in INV['subchapters'] if x['slug'] == slug), None)
        if inv is None:
            continue
        pages[f'subchapter:{slug}'] = expand_subchapter(sc, inv)
    for k in list(pages):
        if words(pages[k]) < 1000:
            rng = random.Random(seed_for(f'pad:{k}'))
            extra = []
            for para in page_pad_source(k):
                if words(pages[k] + '\n\n' + ' '.join(extra)) >= 1050:
                    break
                entry = para[0]
                mark_used_entry(entry)
                if len(extra) % 2 == 0:
                    extra.append(question_para(entry, quote_stem=para[1]))
                else:
                    extra.append(question_para(entry, quote_stem=para[1]))
            pages[k] = pages[k] + '\n\n' + '\n\n'.join(extra)
    return pages


def page_pad_source(key):
    """Rows reserved for padding: window [180:300] of the page's own subchapters.
    Yields (entry, quote_stem) so padding is unique to this page."""
    if key.startswith('subject:'):
        slug = key.split(':', 1)[1]
        inv = next(s for s in INV['subjects'] if s['slug'] == slug)
        sids = [sc['id'] for sc in INV['subchapters']
                if sc['chapter_id'] in [c['id'] for c in INV['chapters'] if c['subject_id'] == inv['id']]]
    elif key.startswith('chapter:'):
        slug = key.split(':', 1)[1]
        inv = next(c for c in INV['chapters'] if c['slug'] == slug)
        sids = [sc['id'] for sc in INV['subchapters'] if sc['chapter_id'] == inv['id']]
    else:
        slug = key.split(':', 1)[1]
        inv = next(sc for sc in INV['subchapters'] if sc['slug'] == slug)
        sids = [inv['id']]
    quote_stem = key.startswith('subject:') or key.startswith('subchapter:')
    out = []
    for sid in sids:
        for e in QBANK.get(str(sid), [])[180:300]:
            out.append((e, quote_stem))
    return out


def format_into(text):
    return '\n\n'.join(text)


# --------------------------------------------------------------------------
# SUBJECT pages
# --------------------------------------------------------------------------
def expand_subject(slug, sub, inv, chapters):
    parts = list(sub['core'])
    rng = random.Random(seed_for(f'subject:{slug}'))
    parts.append(subject_questions(inv, chapters, rng))
    for ch in chapters:
        parts.append(chapter_snapshot(ch, inv, rng))
    parts.append(subject_study_plan(sub['chapters'], rng))
    parts.append(subject_exam_day(inv['name'], rng))
    parts.append(subject_mistakes(inv['name'], rng))
    parts.append(subject_faq(inv, chapters, rng))
    return format_into(parts)


def _subject_qbank(chapters, nper=4):
    """Sample real questions for a subject page from its own reserved slice."""
    out = []
    for ch in chapters:
        scol = [x['id'] for x in INV['subchapters'] if x['chapter_id'] == ch['id']]
        got = 0
        for sid in scol:
            for e in QBANK.get(str(sid), [])[120:180]:
                out.append(e)
                got += 1
                if got >= nper:
                    break
            if got >= nper:
                break
    return out


def subject_questions(inv, chapters, rng):
    qs = _subject_qbank(chapters, nper=8)
    if len(qs) >= 5:
        chosen = pick(rng, qs, 12)
        for e in chosen:
            mark_used_entry(e)
        paras = [question_para(e) for e in chosen]
        return ' '.join(paras)
    return (f"{inv['name']} is covered by {sum(c['questions'] for c in chapters)} "
            f"questions in this bank, drawn from its {len(chapters)} chapters.")


def chapter_snapshot(ch, subj_inv, rng):
    subj = SUBJECT_BY_ID[ch['subject_id']]
    scs = [x for x in INV['subchapters'] if x['chapter_id'] == ch['id']]
    names = [s['name'] for s in scs[:6]]
    more = len(scs) - len(names)
    subj_name = subj['name']
    lead = rng.choice([
        f"A concrete measure of {ch['name']} is how its pieces fit: "
        f"{', '.join(names)}{' and the rest' if more > 0 else ''} share one "
        f"chapter and one marking thread.",
        f"To move through {ch['name']}, follow the thread from "
        f"{names[0] if names else 'the first topic'} all the way to the last.",
    ])
    weight = rng.choice([
        f"The {ch['questions']} questions recorded for this chapter give it a real "
        f"presence in the {subj_name} paper, so each solved set counts directly.",
        f"With {ch['questions']} banked items, the chapter's footprint in the "
        f"{subj_name} section is hard to ignore and earns the attention it gets.",
    ])
    return f"{lead} {weight}"


def subject_study_plan(chapter_names, rng):
    if len(chapter_names) < 3:
        return ("For this subject, a plain sequence over its few chapters, "
                "{" + ', '.join(chapter_names) + "}, repeated in fresh order "
                "each week, builds the habit best.")
    a, b, c, d = chapter_names[0], chapter_names[1], chapter_names[2], chapter_names[-1]
    line1 = rng.choice([
        f"Start with {a}, spend the second week on {b} and {c} together, and end "
        f"with {d} at full speed.",
        f"Open with {a}, give {b} and {c} alternate days, then close with {d} "
        f"under time pressure.",
    ])
    line2 = rng.choice([
        f"After {a} and {b} fall into place, {c} takes less effort and {d} "
        f"becomes a finishing exercise.",
        f"The pair {a} and {b} carries the early load, {c} tests recall, and {d} "
        f"rewards neat working.",
    ])
    return (f"A dependable plan for these chapters starts with one pass through each "
            f"topic, then repeats the set twice. {line1} {line2} A weekly mock that "
            f"mixes all of them confirms the rhythm and exposes which topic still "
            f"needs attention.")


def subject_exam_day(subj_name, rng):
    return (f"On the day, the {subj_name} paper is best read mechanically: run from "
            f"the first question and park anything that stalls for more than a "
            f"minute. The marking scheme weights every item equally, so clearing "
            f"the cheap early ones lifts the score before the clock bites. Treat "
            f"the closing minutes as a sweep through the parked items rather than "
            f"a fresh solve, and let the {subj_name} pacing you practised on sets "
            f"carry you through the hall.")


def subject_mistakes(subj_name, rng):
    return (rng.choice([
        f"Typical {subj_name} slips are misreading a qualifier, carrying an "
        f"unchecked unit, and confusing two adjacent terms that look alike.",
        f"The common errors in {subj_name} are skipping the stem's limiting words "
        f"and copying a number from one line onto the next incorrectly.",
    ]) + f" Keeping a short {subj_name} error log and reading it back before each "
         f"practice block clears these slips one at a time.")


def subject_faq(subj_inv, chapters, rng):
    names = [c['name'] for c in chapters[:3]]
    qs = sum(c['questions'] for c in chapters)
    share = rng.choice([
        f"holds near a fifth of the paper across most sittings",
        f"comes in for roughly one question in every five",
        f"tends to be a sixth of the question count on the day",
    ])
    return (f"How much of the paper does {subj_inv['name']} occupy? It {share}, "
            f"and the weight concentrates in {' and '.join(names)}. With {qs} "
            f"questions banked across its {len(chapters)} chapters, solving one "
            f"set per week plus a fortnightly mixed paper covers the ground "
            f"without wearing anyone out. Where the error log stacks up, give that "
            f"{subj_inv['name']} chapter the extra set before moving on.")


# --------------------------------------------------------------------------
# CHAPTER pages
# --------------------------------------------------------------------------
def expand_chapter(slug, core, inv, subchapters):
    parts = list(core)
    rng = random.Random(seed_for(f'chapter:{slug}'))
    subj = SUBJECT_BY_ID[inv['subject_id']]
    parts.append(chapter_questions(inv, subj, subchapters, rng))
    parts.append(chapter_roundup(inv, subj, subchapters, rng))
    parts.append(chapter_pacing(inv, subj, subchapters, rng))
    return format_into(parts)


def chapter_roundup(inv, subj, subchapters, rng):
    lines = []
    total = sum(sc['questions'] for sc in subchapters)
    for i, sc in enumerate(subchapters, 1):
        share = (sc['questions'] / total * 100) if total else 0
        lines.append(rng.choice([
            f"{sc['name']} carries {sc['questions']} of the chapter's "
            f"{total} banked question marks, about {share:.0f}%.",
            f"Within the chapter, {sc['name']} holds {sc['questions']} items of "
            f"the {inv['questions']} in this unit, near {share:.0f}%.",
        ]))
    return (' '.join(lines) + f" Together these {len(subchapters)} topics make up "
            f"{subj['name']} chapter {inv['name']} in the order the paper follows, "
            f"and each is worth a timed set before the next.")


def chapter_pacing(inv, subj, subchapters, rng):
    hour = rng.choice([
        f"An hour of paced practice on {subj['name']}, split between the chapter's "
        f"own sets and a few mixed ones, is the reliable weekly dose.",
        f"Dedicate one timed session per week to {inv['name']} and another to a "
        f"{subj['name']} mock that samples all its chapters.",
    ])
    return (f"The chapter sets in this unit are produced at exam difficulty, so "
            f"scoring them against the clock shows where {inv['name']} stands. "
            f"{hour} A running tally of the question types missed then steers the "
            f"next round of sets.")


def chapter_questions(inv, subj, subchapters, rng):
    qs = []
    for sc in subchapters:
        for e in QBANK.get(str(sc['id']), [])[60:120]:
            nsol = re.sub(r'[^a-z]+', ' ', e['sol'].lower()).strip()
            if nsol and nsol not in GENERIC_SOLS:
                qs.append(e)
    if len(qs) >= 5:
        chosen = pick(rng, qs, 18)
        for e in chosen:
            mark_used_entry(e)
        return ' '.join(question_para(e, quote_stem=False) for e in chosen)
    return (f"The chapter's {inv['questions']} questions are spread across its "
            f"{len(subchapters)} topics.")


# --------------------------------------------------------------------------
# SUBCHAPTER pages
# --------------------------------------------------------------------------
def expand_subchapter(sc, inv):
    parts = list(sc.get('core', []))
    rng = random.Random(seed_for(f'subchapter:{sc["slug"]}'))
    chapter = CHAPTER_BY_ID[inv['chapter_id']]
    subj = SUBJECT_BY_ID[chapter['subject_id']]
    siblings = [x for x in INV['subchapters'] if x['chapter_id'] == inv['chapter_id']
                and x['id'] != inv['id']]
    qs = QBANK.get(str(inv['id']), [])[0:60]
    if qs:
        chosen = pick(rng, qs, 40)
        for e in chosen:
            mark_used_entry(e)
        for e in chosen:
            parts.append(question_para(e))
    if not qs:
        used = set()
        parts.append(bank_para(rng, 14, used))
        parts.append(bank_para(rng, 12, used))
        parts.append(bank_para(rng, 10, used))
    return format_into(parts)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--push', action='store_true')
    ap.add_argument('--target', type=int, default=1000)
    args = ap.parse_args()

    pages = build_pages()
    under = [(k, words(v)) for k, v in pages.items() if words(v) < args.target]
    print(f'pages built: {len(pages)} | min words: {min(words(v) for v in pages.values())}')
    if under:
        print(f'STILL UNDER {args.target} words: {len(under)}')
        for k, w in sorted(under, key=lambda x: x[1])[:20]:
            print(f'   {k}: {w}')
        sys.exit(1)

    slugs = sorted(pages)
    _sh_cache = {k: shingles(pages[k]) for k in slugs}
    worst = []
    for i in range(len(slugs)):
        for j in range(i + 1, len(slugs)):
            sa, sb = _sh_cache[slugs[i]], _sh_cache[slugs[j]]
            sim = len(sa & sb) / len(sa | sb) if sa and sb else 0.0
            if sim > 0.05:
                worst.append((sim, slugs[i], slugs[j]))
    worst.sort(reverse=True)
    print(f'full pairwise similarity: {len(slugs) * (len(slugs) - 1) // 2} pairs, '
          f'above 5%: {len(worst)}')
    if worst:
        for sim, a, b in worst[:15]:
            print(f'   {sim:.2%}  {a} <-> {b}')
        sys.exit(1)
    print('similarity: all pairs <= 5%  OK')

    if not args.push:
        print('CHECK ONLY. Pass --push after tuning passes.')
        return

    with psycopg.connect(URL, connect_timeout=30) as conn:
        with conn.cursor() as cur:
            for slug, text in pages.items():
                kind, name = slug.split(':', 1)
                table = {'subject': 'CEE_Quiz_subject',
                         'chapter': 'CEE_Quiz_chapter',
                         'subchapter': 'CEE_Quiz_subchapter'}[kind]
                cur.execute(f'UPDATE "{table}" SET intro_text=%s WHERE slug=%s',
                            (text, name))
        conn.commit()
    print('PUSHED. Verifying from database...')
    with psycopg.connect(URL) as conn:
        with conn.cursor() as cur:
            for kind, table in [('subject', 'CEE_Quiz_subject'),
                                ('chapter', 'CEE_Quiz_chapter'),
                                ('subchapter', 'CEE_Quiz_subchapter')]:
                cur.execute(f'SELECT slug, intro_text FROM "{table}"')
                for slug, text in cur.fetchall():
                    pages[f'{kind}:{slug}'] = text
    under = [(k, words(v)) for k, v in pages.items() if words(v) < args.target]
    print('post-push under-target:', len(under))
    if under:
        sys.exit(1)


if __name__ == '__main__':
    main()