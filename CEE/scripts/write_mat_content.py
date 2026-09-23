"""Write original MAT content (subject/chapter/subchapter intros + SEO) and
regenerate PageSEO rows for subjects, chapters and subchapters.

Run: python scripts/write_mat_content.py
"""
import psycopg

URL = ''
for line in open('scripts/.env', encoding='utf-8'):
    if line.startswith('SUPABASE_DATABASE_URL='):
        URL = line.split('=', 1)[1].strip()

SUBJECT_INTRO = (
    "MAT (Mental Ability Test) is the fourth section of Nepal's CEE, carrying "
    "40 of the 200 questions. It is the fastest-moving part of the paper: every "
    "MAT question rewards a sharp response, and careless errors cost marks "
    "through negative marking. MAT is not about memorising formulas but about "
    "recognising patterns quickly. Studying under four headings helps - "
    "numerical reasoning, verbal reasoning, logical sequencing, and spatial or "
    "abstract reasoning. Practise each topic in timed sets, then take full MAT "
    "mock tests. On exam day most candidates finish MAT first, so train accuracy "
    "and speed together. The solved sets here show every answer step by step, so "
    "re-read them until each type's starting move feels automatic."
)

CHAPTER_INTROS = {
    'numerical-reasoning': (
        "Numerical reasoning tests your speed with everyday arithmetic: time and "
        "work, percentages, profit and loss, ratio, ages, averages, speed and "
        "distance, and interest. These problems depend on a few evergreen "
        "relationships and careful reading rather than heavy theory. The CEE "
        "usually asks two to four of these under MAT, so a small, well-practised "
        "toolkit is enough. Work each solved set under the suggested time and "
        "review the step-by-step solutions afterwards. Once a set feels quick, "
        "repeat it until the first move of every problem type becomes automatic."
    ),
    'verbal-reasoning-test': (
        "Verbal reasoning is about words and the relationships between them: "
        "synonyms and antonyms, verbal analogies, classifications, coding, ranking "
        "puzzles, and word sequences. The CEE MAT use these to test how quickly "
        "you can map meaning, not what you have memorised. The challenge is "
        "usually reading precision - the gap between two close options is often a "
        "single shade of meaning. Work through the solved sets at a steady pace "
        "and revisit any question that felt ambiguous. Building speed on easy "
        "questions gives you spare time for the genuinely tricky ones."
    ),
    'logical-sequencing': (
        "Logical sequencing asks you to arrange words, numbers, figures, or "
        "statements in the correct order and to spot the rule a sequence follows. "
        "Topics include number and alphabet series, matrix and missing characters, "
        "analogies, venn diagrams, and classification. These questions look "
        "technical but the patterns are simple once you know what to look for. "
        "Begin with the solved sets to see the reasoning written out line by line, "
        "then time yourself on fresh attempts. Two or three correct answers here "
        "can decide your MAT scorecard, so treat each new pattern as an exam-day "
        "advantage."
    ),
    'spatial-relationabstract-reasoning': (
        "Spatial and abstract reasoning moves MAT beyond words into shapes: figure "
        "formation and construction, grouping, paper folding, cubes and dice, "
        "embedded figures, dot situations, and mirror and water images. These "
        "questions test mental rotation, symmetry, and attention to proportion "
        "rather than language or number skills. Because the answer is visual, the "
        "main risk is rushing - a quick glance misreads a rotation or a fold "
        "direction. Use the solved sets to train your eye on the common traps, "
        "then practise speeded drills to sharpen judgement. Staying calm with "
        "figures often earns marks that other candidates throw away."
    ),
}

SUBCHAPTER_CONTENT = {  # slug: (intro_text, seo_description)
    'time-and-work': (
        "Time-and-work problems ask how long a person or a machine takes to "
        "complete a task, alone or together. The trick is to treat the total work "
        "as one unit and convert every rate into work done per day. In the CEE MAT "
        "these questions usually need just one or two equations.",
        "Time and Work MCQ practice for CEE MAT with work-rate problems, pipes and "
        "cisterns, and efficiency-based questions."),
    'percentage': (
        "Percentage is the busiest idea in MAT arithmetic. Successive discounts, "
        "price changes, and increases or decreases all reduce to the same basic "
        "relationship, so the skill is spotting the quantity called the original. "
        "Master the shortcuts, but always know what the percentage is being taken "
        "of.",
        "Percentage MCQ questions for CEE MAT: quick tricks, successive percentage, "
        "increase-decrease and base-value problems."),
    'profit-and-loss': (
        "Profit and loss questions reward clear bookkeeping: cost price, selling "
        "price, gain per cent and, in tougher CEE questions, marked price versus "
        "discount. Keep profit as a fraction of cost price unless the question says "
        "otherwise, and a small table will save most errors.",
        "Profit and Loss MCQs for CEE MAT: cost price, selling price, discount, "
        "marked price and gain per cent methods."),
    'ratio-and-proportion': (
        "Ratio and proportion links two or more quantities through a constant "
        "multiplier, and it drives most MAT word problems. Questions combine ratios "
        "with ages, mixtures and shares. Write the ratio chain in one line and the "
        "algebra usually follows.",
        "Ratio and Proportion MCQ practice for CEE MAT covering compounded ratios, "
        "mixtures and proportion applications."),
    'problem-on-ages': (
        "Ages questions set up two or three people whose ages relate in fixed "
        "ratios, either now, some years ago, or in the future. It is simplest to "
        "pitch the ages as multiples of the common ratio and write the difference "
        "as one equation.",
        "Problem on Ages MCQs for CEE MAT: age ratio problems and past-and-future "
        "age statements with quick solution steps."),
    'averages': (
        "Averages fold a list of numbers into a single value. MAT uses them two "
        "ways: finding the mean of a group, or working back from a changed average "
        "to a missing value. Keep total sums in focus rather than the raw numbers.",
        "Averages MCQ questions for CEE MAT: mean, missing value and group average "
        "problems with shortcuts."),
    'time-speed-and-distance': (
        "Time, speed and distance marry a simple formula with careful units and a "
        "few classic setups: trains and platforms, boats against currents, and "
        "meeting-point puzzles. Convert units before you calculate and the rest is "
        "routine.",
        "Time, Speed and Distance MCQs for CEE MAT: trains, relative speed, and "
        "boat-and-stream problems with formulas."),
    'permutation-and-combination': (
        "Permutation and combination count ways of arranging or selecting items. "
        "MAT keeps the numbers small, so the exam mostly judges whether you know "
        "when order matters. If order matters it is a permutation, otherwise a "
        "combination.",
        "Permutation and Combination MCQ practice for CEE MAT: nPr and nCr "
        "arrangements and selections explained."),
    'partnership': (
        "Partnership splits profit between investors in proportion to what they "
        "invest and for how long. The CEE version usually gives two partners and a "
        "ratio; weight each capital by its time and the answer is clean.",
        "Partnership MCQs for CEE MAT: profit sharing with capitals and time "
        "periods, with worked examples."),
    'simple-interest-and-compound-interest': (
        "Interest problems frame money growth over time. Simple interest grows by "
        "a fixed sum each year; compound interest multiplies. At CEE level, spot "
        "the period and check whether interest compounds yearly, half-yearly, or "
        "quarterly.",
        "Simple and Compound Interest MCQ for CEE MAT: SI, CI, rate, time and "
        "amount problems with formulas."),
    'distance-and-direction': (
        "Distance and direction questions trace a path through north, south, east "
        "and west moves and ask for net displacement or a compass bearing. Draw a "
        "small sketch as you read; the answer then falls out of the diagram.",
        "Distance and Direction MCQ for CEE MAT: path tracing, shortest distance "
        "and direction-sense problems."),
    'coding-and-decoding': (
        "Coding and decoding turns letters, numbers, or symbols into a hidden "
        "message. The rule is usually consistent: a letter shift, a reversal, or a "
        "position swap. Study the example pairs carefully, infer the rule, then "
        "decode the target.",
        "Coding and Decoding MCQs for CEE MAT: letter and number shifts, reversed "
        "alphabet, and symbol coding."),
    'ranking-order': (
        "Ranking-order questions place people or items in a line and quiz you on "
        "positions, total counts, or who stands between whom. Fix one end as the "
        "anchor and translate every from-the-left or from-the-right into a clear "
        "picture.",
        "Ranking Order MCQ practice for CEE MAT: position-based reasoning and the "
        "number of persons between two ranks."),
    'verbal-classification': (
        "Verbal classification offers four words and asks which one does not "
        "belong. MAT looks for a clean, robust rule: odd one out by category, "
        "function, or property. Prefer the item that breaks the strongest shared "
        "rule.",
        "Verbal Classification MCQ for CEE MAT: odd-one-out word problems grouped "
        "by meaning, function or quality."),
    'verbal-analogy': (
        "Verbal analogy compares word pairs: A is to B as C is to D. Put the "
        "relationship into words first, then test each option against that exact "
        "relationship. The strongest analogy matches the original pair at the same "
        "level of specificity.",
        "Verbal Analogy MCQ questions for CEE MAT: word-pair relationships, "
        "synonym, antonym and class analogies."),
    'synonym-and-antonym': (
        "Synonym and antonym questions check precise vocabulary. A word can have "
        "many near-synonyms, so the exam expects the closest match. Read one fresh "
        "English word each day alongside these practice sets.",
        "Synonym and Antonym MCQs for CEE MAT vocabulary: choosing the closest "
        "meaning and its opposite, with word lists."),
    'verbal-puzzle': (
        "Verbal puzzles dress logic problems in a story: neighbours in houses, "
        "friends competing for ranks, or students in seats. Turn the sentences "
        "into notes, combine the constraints, and the puzzle collapses to a small "
        "set of possibilities.",
        "Verbal Puzzle MCQ for CEE MAT: seating, ordering and constraint-based "
        "logic problems with step-by-step methods."),
    'blood-relations': (
        "Blood-relations questions map family trees from sentences like the son of "
        "my father's brother. Draw the tree as a small diagram and label the "
        "generations; the exam then asks who is whose what at one or two removes.",
        "Blood Relations MCQ practice for CEE MAT: family-tree problems, generation "
        "logic and coded relations."),
    'statement-and-reasons': (
        "Statement-and-reasons gives you facts plus one or two conclusions, and "
        "asks which conclusion truly follows. Do not bring outside knowledge; "
        "judge only on what the statements say. Check which conclusion follows "
        "necessarily rather than merely possibly.",
        "Statement and Reasons MCQ for CEE MAT: conclusions drawn from premises "
        "and strict logic testing."),
    'arithmetical-operation': (
        "Arithmetical-operation puzzles replace ordinary operators with unusual "
        "definitions such as A>B meaning A multiplied by B minus 2. Work strictly "
        "inside the given rule and keep the order of operations fixed.",
        "Arithmetical Operation MCQ for CEE MAT: symbol redefinition and operator "
        "puzzles with worked rules."),
    'number-series': (
        "Number series lay down a sequence with a pattern hidden in differences, "
        "products, or alternating rules. Write the gaps between consecutive terms; "
        "the pattern usually lives in that gap row. Try addition or multiplication "
        "first, then both.",
        "Number Series MCQ practice for CEE MAT: arithmetic, geometric and mixed "
        "pattern series with shortcuts."),
    'alphabet-series': (
        "Alphabet-series sequences treat letters as positions on a circular wheel. "
        "Track positions (A=1 through Z=26) and look for the same gap logic as "
        "numbers, including reverse runs around the alphabet.",
        "Alphabet Series MCQ for CEE MAT: letter-position sequences and circular "
        "alphabet reasoning."),
    'continuous-patterns-and-positional-series': (
        "Continuous patterns repeat a block of letters, numbers, or symbols with a "
        "twist after each cycle. Find the repeating block, locate the missing "
        "element inside it, and read the sequence one block at a time.",
        "Continuous Patterns and Positional Series MCQ for CEE MAT: repeating "
        "blocks and positional reasoning."),
    'matrix-and-missing-characters': (
        "Matrix questions present a grid where each row and column follows one "
        "rule, with one cell missing. Solve two complete rows to guess the rule, "
        "confirm it on a third, then fill the blank. Column rules often differ "
        "from row rules.",
        "Matrix and Missing Characters MCQ practice for CEE MAT: grid logic, "
        "row-column rules and finding the missing entry."),
    'analogy': (
        "This analogy variant focuses on numbers and figures: understand how the "
        "first pair transforms, then apply the very same change to the third item. "
        "Keep the operation exact, including any rotation or shading changes.",
        "Analogy MCQ questions for CEE MAT: applying first-pair relationships to "
        "numbers and figures."),
    'classification': (
        "Classification in MAT asks which figure, number, or word breaks the "
        "set's common property. Inspect every option for the strongest shared rule "
        "first; the exception often breaks size, orientation, or count.",
        "Classification MCQ for CEE MAT: odd-one-out among numbers, letters and "
        "figures based on shared properties."),
    'logical-sequence-of-words': (
        "Arranging words in a logical order may follow size, process stages, "
        "hierarchy, or chronology. Decide the dimension of ordering before "
        "comparing options; the sequence must make sense at every adjacent step.",
        "Logical Sequence of Words MCQ for CEE MAT: arranging events, stages and "
        "hierarchies in sensible order."),
    'logical-venn-diagram': (
        "Venn diagrams sort overlapping categories such as country, city, and "
        "river. Identify which sets can overlap and which are exclusive, then pick "
        "the diagram whose circles mirror exactly those relations.",
        "Logical Venn Diagram MCQ practice for CEE MAT: set relationships and "
        "best-diagram selection."),
    'common-properties': (
        "Common-properties questions look for a trait shared by several given "
        "items, then apply it to the answer options. Name the property in one "
        "phrase and test every option against that same phrase so you do not drift "
        "to a vague similarity.",
        "Common Properties MCQ for CEE MAT: identifying shared features among "
        "numbers, letters and figures."),
    'series': (
        "The general series exercise blends number, alphabet, and mixed-item "
        "patterns. Because the type is not announced, scan for the ordering "
        "principle first - differences, ratios, alternations, or combined links - "
        "then predict the next term.",
        "Series MCQ questions for CEE MAT: identifying pattern types in "
        "number-letter-symbol sequences."),
    'classification-test': (
        "A full classification test groups items and asks for the odd one out "
        "under time pressure. Prefer a rule that cleanly separates all intended "
        "options, and be ready to re-run the test when two rules compete.",
        "Classification Test MCQ for CEE MAT: timed odd-one-out drills with "
        "numbers, words and figures."),
    'analogy-2': (
        "The second analogy track pairs that transform in more than one way at "
        "once, such as rotating and changing shading together. Track both changes "
        "independently, then apply them to the target in the same order.",
        "Analogy (advanced) MCQ practice for CEE MAT: multi-step transformations "
        "between figure pairs."),
    'matrix': (
        "Matrix reasoning generalises the missing-character idea to several rows "
        "and columns, each with its own rule. Solve row by row, confirm with the "
        "final row, and choose the option that keeps every confirmed rule "
        "satisfied.",
        "Matrix MCQ for CEE MAT: multi-row reasoning grids with independent row "
        "and column patterns."),
    'figure-formation': (
        "Figure-formation combines two or more shapes into a definite whole and "
        "asks which option matches the assembled figure. Trace the pieces in your "
        "mind, match corners and lengths exactly, and reject options that distort "
        "proportions.",
        "Figure Formation MCQ for CEE MAT: assembling parts into a single figure "
        "with spatial matching."),
    'construction-of-figure': (
        "Construction-of-figure questions rebuild a target figure from given "
        "parts, choosing the option in which all pieces appear once without "
        "overlap. Verify every piece by shape and orientation before confirming "
        "the assembly.",
        "Construction of Figure MCQ for CEE MAT: fitting pieces to make the target "
        "shape with precision."),
    'analytic-reasoning-test': (
        "Analytic reasoning bundles the classic verbal-logic tools, often seating "
        "or ranking puzzles with several clues. Write one clue per line, look for "
        "the strongest link, and fill the arrangement step by step until only one "
        "order remains possible.",
        "Analytic Reasoning Test MCQ for CEE MAT: multi-clue seating and ordering "
        "logic problems."),
    'grouping-figure': (
        "Grouping figures asks you to sort several small figures into classes "
        "using shared features. Group by properties such as number of sides, "
        "symmetry, or interior shading, then match the option that reproduces the "
        "same classes.",
        "Grouping Figure MCQ practice for CEE MAT: classifying figures into "
        "defined groups by common features."),
    'paper-folding': (
        "Paper-folding questions show a sheet being folded, then perhaps punched, "
        "and ask for the opened result. Recreate the folds in reverse to unfold "
        "the holes, or rule out options whose hole pattern breaks the fold "
        "symmetry.",
        "Paper Folding MCQ for CEE MAT: hole patterns after folds, with symmetry "
        "shortcuts."),
    'cube-and-dice': (
        "Cube and dice questions work out hidden faces from nets or rolled dice. "
        "Opposite faces never touch, so track which faces share an edge and which "
        "sit opposite; this small map solves nearly every cube question.",
        "Cube and Dice MCQ for CEE MAT: opposite faces, dice rolls and open-net "
        "reasoning."),
    'embedded-figure': (
        "An embedded figure hides somewhere inside a larger, busier drawing. Scan "
        "systematically region by region, looking for the exact outline of the "
        "hidden shape, and confirm by matching at least two distinctive corners.",
        "Embedded Figure MCQ for CEE MAT: locating a target shape inside complex "
        "figures."),
    'dot-situation': (
        "Dot-situation problems place one or more dots that must lie inside "
        "selected overlaps or non-overlaps of several figures. Label each region - "
        "inside A, inside B, in both, outside both - and check every dot against "
        "its label.",
        "Dot Situation MCQ for CEE MAT: placing dots across overlapping figure "
        "regions."),
    'water-image-and-mirror-image': (
        "Mirror and water images invert a figure: a mirror flips left and right "
        "while water flips top and bottom. Test a single asymmetric feature, such "
        "as a small notch, to tell the true option from the rotated "
        "approximations.",
        "Water Image and Mirror Image MCQ practice for CEE MAT: vertical and "
        "horizontal inversion rules."),
}


def fmt(text):
    return ' '.join(text.split())


def clip(text, n):
    text = fmt(text)
    return text if len(text) <= n else text[: n - 1].rstrip() + '…'


def main():
    with psycopg.connect(URL, connect_timeout=30) as conn:
        with conn.cursor() as cur:
            # MAT subject intro
            cur.execute('UPDATE "CEE_Quiz_subject" SET intro_text=%s WHERE slug=%s',
                        (fmt(SUBJECT_INTRO), 'mat'))
            print('subject mat: intro set')

            # MAT chapter intros
            n = 0
            for slug, text in CHAPTER_INTROS.items():
                cur.execute('UPDATE "CEE_Quiz_chapter" SET intro_text=%s WHERE slug=%s',
                            (fmt(text), slug))
                n += cur.rowcount
            print('mat chapters intros updated:', n)

            # MAT subchapter intros + seos
            n = 0
            for slug, (intro, seo) in SUBCHAPTER_CONTENT.items():
                cur.execute(
                    'UPDATE "CEE_Quiz_subchapter" SET intro_text=%s, seo_description=%s '
                    'WHERE slug=%s', (fmt(intro), fmt(seo), slug))
                n += cur.rowcount
            print('mat subchapters updated:', n)

            # ---- regenerate PageSEO rows for subjects/chapters/subchapters ----
            rows = []
            cur.execute('SELECT slug, name FROM "CEE_Quiz_subject"')
            for slug, name in cur.fetchall():
                title = f'{name} MCQ Questions | Chapter Wise | CEE MCQ'
                desc = ('Practice chapter-wise {name} MCQ questions for Nepal\'s '
                        'CEE entrance exam. Free quiz sets, solutions and timed '
                        'tests.').format(name=name)
                rows.append((slug,
                             clip(title, 70),
                             clip(desc, 160),
                             f'{name} MCQ, CEE {name}, chapter wise questions',
                             clip(f'{name} Chapters | CEE MCQ', 70),
                             clip(f'Practice chapter wise MCQ questions for '
                                  f'{name}. Prepare for Nepal\'s CEE.', 160)))

            cur.execute('''SELECT ch.slug, ch.name, s.name AS subject
                           FROM "CEE_Quiz_chapter" ch
                           JOIN "CEE_Quiz_subject" s ON ch.subject_id = s.id''')
            for slug, name, subject in cur.fetchall():
                title = f'{name} MCQ | {subject} | CEE MCQ'
                ded = (f'{name} MCQ practice for CEE {subject}. Chapter-wise '
                       f'questions with solutions to prepare for Nepal\'s Common '
                       f'Entrance Examination.')
                rows.append((slug,
                             clip(title, 70),
                             clip(ded, 160),
                             f'CEE MCQ, {name} MCQ, {subject}, chapter wise questions',
                             clip(title, 70),
                             clip(ded, 160)))

            cur.execute('''SELECT sc.slug, sc.name, ch.name AS chapter, s.name AS subject
                           FROM "CEE_Quiz_subchapter" sc
                           JOIN "CEE_Quiz_chapter" ch ON sc.chapter_id = ch.id
                           JOIN "CEE_Quiz_subject" s ON ch.subject_id = s.id''')
            for slug, name, chapter, subject in cur.fetchall():
                title = f'{name} MCQ | {chapter} | CEE MCQ'
                ded = (f'{name} MCQ practice from {chapter} for CEE {subject}. '
                       f'Timed quiz sets with step-by-step solutions.'
                       if name != chapter else
                       f'{name} MCQ practice for CEE {subject} with solutions.')
                rows.append((slug,
                             clip(title, 70),
                             clip(ded, 160),
                             f'CEE MCQ, {name} MCQ, {chapter} MCQ, {subject}',
                             clip(title, 70),
                             clip(ded, 160)))

            cur.execute('SELECT page_slug FROM "CEE_Quiz_pageseo"')
            existing = {r[0] for r in cur.fetchall()}
            cur.execute('SELECT MAX(id) FROM "CEE_Quiz_pageseo"')
            next_id = (cur.fetchone()[0] or 0) + 1
            inserted = 0
            for slug, t, d, k, ogt, ogd in rows:
                if slug in existing:
                    continue
                cur.execute(
                    'INSERT INTO "CEE_Quiz_pageseo" '
                    '(id, page_slug, meta_title, meta_description, meta_keywords, '
                    ' og_title, og_description) VALUES (%s,%s,%s,%s,%s,%s,%s)',
                    (next_id, slug, t, d, k, ogt, ogd))
                inserted += 1
                next_id += 1
            print('pageseo rows inserted:', inserted, '| total rows now:', len(existing) + inserted)
        conn.commit()

    # verify
    with psycopg.connect(URL) as conn:
        with conn.cursor() as cur:
            cur.execute('SELECT count(*) FROM "CEE_Quiz_subchapter" '
                        'WHERE intro_text IS NULL OR LENGTH(btrim(intro_text)) = 0 '
                        '   OR seo_description IS NULL OR LENGTH(btrim(seo_description)) = 0')
            print('subchapters still missing intro or seo:', cur.fetchone()[0])
            cur.execute('SELECT count(*) FROM "CEE_Quiz_chapter" '
                        'WHERE intro_text IS NULL OR LENGTH(btrim(intro_text)) = 0')
            print('chapters still missing intro:', cur.fetchone()[0])
            cur.execute('SELECT count(*) FROM "CEE_Quiz_pageseo"')
            print('pageseo total:', cur.fetchone()[0])


if __name__ == '__main__':
    main()