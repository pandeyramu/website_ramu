"""
Fix AI-generation artifacts leaked into question solutions.

Cleans three classes of problems:
  1. Correction artifacts  - "(option_b was corrected from X to Y)"
  2. AI self-talk          - "Wait, this contradicts... Let me recheck..."
  3. Markdown leaks        - literal ** / ### / ``` in plain-text fields

Questions whose solution had to be truncated (self-talk removed) are marked
verified=False so they disappear from public preview pages until manually
reviewed in the admin. A JSON report of every touched question is written to
the directory the command runs from.

Usage:
  python manage.py fix_solution_artifacts            # dry run, shows what would change
  python manage.py fix_solution_artifacts --apply    # write changes + report file
"""
import json
import re

from django.core.management.base import BaseCommand
from django.db.utils import IntegrityError
from django.utils import timezone

from CEE_Quiz.models import Question

CORRECTION_PAREN = re.compile(r'\s*\((?:option_[abcd]|[A-Da-d])\s+was corrected from[^)]*\)')
CORRECTION_SENTENCE = re.compile(r'\s*(?:Option\s+[A-Da-d]|option_[abcd])\s+was corrected from[^\n\r]*')
SELF_TALK = re.compile(
    r'\b(?:[Ww]ait[,!\u2014-]|wait\u2014|[Ll]et me\s+(?:recheck|recalculate|correct|verify)|'
    r'[Hh]mm[,]|I apologize|My mistake|my mistake|'
    r'this contradicts the answer|contradicts the given answer|'
    r"but user's answer|user's answer placement)"
)
# Patterns that indicate the stored correct_option itself may be wrong.
ANSWER_CONFLICT = re.compile(
    r'(Conflict Note|placement requires|answer placement|Final Correction|'
    r'Revised Solution|\*\*Correction\*\*|correct answer is [A-D],? but)'
)
MARKDOWN_BOLD_UNDERSCORE = re.compile(r'__([^\s_][^_]*[^\s_]|[^\s_])__')
MARKDOWN = re.compile(r'(\*\*|###|```)')
LEADING_MD_HEADING = re.compile(r'^\s*#{1,6}\s*', re.M)


class Command(BaseCommand):
    help = 'Clean AI-generation artifacts from question/solution text.'

    def add_arguments(self, parser):
        parser.add_argument('--apply', action='store_true',
                            help='Actually save changes. Without this flag, dry run only.')
        parser.add_argument('--report', default='artifact_fix_report.json',
                            help='Path of the JSON report file.')

    def handle(self, *args, **opts):
        apply_changes = opts['apply']
        stats = {'scanned': 0, 'correction_artifact': 0, 'self_talk_truncated': 0,
                 'markdown_stripped': 0, 'marked_unverified': 0, 'needs_manual': 0,
                 'text_collision_hidden': 0}
        report = []

        for q in Question.objects.all().iterator():
            stats['scanned'] += 1
            changes = {}
            needs_manual = False
            originals = {f: getattr(q, f) or '' for f in ('question_text', 'solution')}

            for field in ('question_text', 'solution'):
                text = getattr(q, field) or ''
                if not text:
                    continue
                new = text

                # Answer-key conflicts: cannot be auto-fixed safely.
                if field == 'solution' and ANSWER_CONFLICT.search(new):
                    needs_manual = True
                    changes['solution_answer_conflict'] = ANSWER_CONFLICT.search(new).group(0)

                new, n1 = CORRECTION_PAREN.subn('', new)
                new, n2 = CORRECTION_SENTENCE.subn('', new)
                if n1 or n2:
                    changes[f'{field}_correction_removed'] = n1 + n2

                m = SELF_TALK.search(new)
                if m:
                    truncated = new[:m.start()].rstrip()
                    truncated = re.sub(r'[\.,;:\u2014-]+$', '', truncated).rstrip()
                    if len(truncated) >= 60:
                        changes[f'{field}_truncated_at'] = m.group(0)
                        if field == 'solution':
                            needs_manual = True
                        new = truncated + '.'
                    else:
                        needs_manual = True
                        changes[f'{field}_self_talk_unfixable'] = m.group(0)

                stripped = MARKDOWN_BOLD_UNDERSCORE.sub(r'\1', new)
                stripped = MARKDOWN.sub('', stripped)
                stripped = LEADING_MD_HEADING.sub('', stripped)
                if stripped != new:
                    changes[f'{field}_markdown_stripped'] = True
                    new = stripped

                if new != text:
                    changes[field] = {'before': text[:200], 'after': new[:200]}
                    setattr(q, field, new)

            if changes or needs_manual:
                report.append({'id': q.id, 'changes': list(changes.keys()),
                               'detail': {k: v for k, v in changes.items() if not k.endswith(('_removed', '_at'))},
                               'needs_manual': needs_manual})
                if 'solution_correction_removed' in changes or 'question_text_correction_removed' in changes:
                    stats['correction_artifact'] += 1
                if any('_truncated_at' in k for k in changes):
                    stats['self_talk_truncated'] += 1
                if any('_markdown_stripped' in k for k in changes):
                    stats['markdown_stripped'] += 1
                if needs_manual:
                    stats['needs_manual'] += 1

                if apply_changes:
                    if needs_manual:
                        q.verified = False
                        stats['marked_unverified'] += 1
                    try:
                        q.save()
                    except IntegrityError:
                        # Cleaned question_text collides with another row's text
                        # (unique constraint). Restore original text, hide the row.
                        for field in ('question_text', 'solution'):
                            setattr(q, field, originals[field])
                        q.verified = False
                        stats['text_collision_hidden'] += 1
                        report.append({'id': q.id,
                                       'changes': ['text_collision_hidden'],
                                       'detail': {'colliding_text':
                                                  originals['question_text'][:200]},
                                       'needs_manual': True})
                        q.save(update_fields=['question_text', 'solution', 'verified'])

        action = 'APPLIED' if apply_changes else 'DRY RUN (use --apply to write)'
        self.stdout.write(f'\n=== {action} ===')
        for k, v in stats.items():
            self.stdout.write(f'{k}: {v}')
        if apply_changes:
            with open(opts['report'], 'w', encoding='utf-8') as f:
                json.dump({'generated': timezone.now().isoformat(), 'stats': stats,
                           'questions': report}, f, ensure_ascii=False, indent=2)
            self.stdout.write(f'Report written to {opts["report"]}')
