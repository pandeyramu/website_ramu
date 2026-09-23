"""Give each MAT solved set a unique intro based on the topics it actually covers."""
import psycopg

url = ''
for line in open('scripts/.env', encoding='utf-8'):
    if line.startswith('SUPABASE_DATABASE_URL='):
        url = line.split('=', 1)[1].strip()

CHAPTER_LEAD = {
    'numerical-reasoning': 'These questions sharpen your speed with everyday '
                          'arithmetic that shows up across the MAT paper.',
    'verbal-reasoning-test': 'The questions here test how quickly you read meaning '
                            'into words, relations and coded messages.',
    'logical-sequencing': 'Expect to think in order: patterns, positions and '
                         'arrangements are what this set drills.',
    'spatial-relationabstract-reasoning': 'This set is all about shapes: rotation, '
                                          'folding, grouping and hidden figures.',
}

with psycopg.connect(url) as conn:
    with conn.cursor() as cur:
        cur.execute('''SELECT ss.id, ch.name, ch.slug, ss.set_number, ss.question_ids
                       FROM "CEE_Quiz_solutionset" ss
                       JOIN "CEE_Quiz_chapter" ch ON ss.chapter_id = ch.id
                       WHERE ch.subject_id = 5 ORDER BY ch.id, ss.set_number''')
        rows = cur.fetchall()
        updated = 0
        for ss_id, ch_name, ch_slug, set_num, qids_raw in rows:
            qids = [int(x) for x in qids_raw.split(',') if x.strip()] if qids_raw else []
            topics = []
            if qids:
                cur.execute('''SELECT DISTINCT sc.name
                               FROM "CEE_Quiz_question" q
                               JOIN "CEE_Quiz_subchapter" sc ON q.sub_chapter_id = sc.id
                               WHERE q.id = ANY(%s::bigint[]) ORDER BY sc.name''',
                            ([x for x in qids[:500]],))
                topics = [r[0] for r in cur.fetchall()]
            n = len(qids)
            lead = CHAPTER_LEAD.get(ch_slug, '')
            count = f'{n} solved {ch_name} questions'
            if topics:
                covered = ', '.join(topics[:5])
                extra = f' and {len(topics) - 5} more' if len(topics) > 5 else ''
                tail = f' They cover {covered}{extra}.'
            else:
                tail = ''
            intro = (f'Solved Set {set_num} in the {ch_name} chapter brings you {count}. '
                     f'{lead}{tail} Every question has a verified answer, the reasoning '
                     f'behind it, and a step-by-step solution to follow. Work the set '
                     f'in exam conditions first, then compare your method with ours.')
            cur.execute('UPDATE "CEE_Quiz_solutionset" SET intro_text=%s WHERE id=%s',
                        (' '.join(intro.split()), ss_id))
            updated += cur.rowcount
        print('MAT solved-set intros updated:', updated)
    conn.commit()

with psycopg.connect(url) as conn:
    with conn.cursor() as cur:
        cur.execute('''SELECT COALESCE(ss.intro_text, ''), count(*)
                       FROM "CEE_Quiz_solutionset" ss
                       JOIN "CEE_Quiz_chapter" ch ON ss.chapter_id = ch.id
                       WHERE ch.subject_id = 5
                       GROUP BY ss.intro_text HAVING count(*) > 1''')
        dups = cur.fetchall()
        print('duplicate intro groups remaining:', len(dups))
        for text, cnt in dups:
            print(f'   x{cnt}: {" ".join(text.split())[:90]}')