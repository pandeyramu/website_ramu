from pathlib import Path
import importlib.util

from django.db import migrations

# ---------------------------------------------------------------------------
# Re-seed Subject/Chapter/SubChapter intro_text with the corrected text.
#
# The original seed migrations (0009, 0011, 0012, 0013) used Python adjacent-
# string concatenation split across source lines, and many segments were
# missing a trailing space. On a fresh database the fixed migration files now
# produce correct text, but databases that already ran those migrations (e.g.
# the live Supabase DB) still hold the joined-word text (e.g. "lawand",
# "forbuoyancy"). This migration reconstructs the exact corrected text by
# replaying the seed pipeline from the corrected source data and overwrites
# the stored intro_text values.
# ---------------------------------------------------------------------------

_MIGRATION_DIR = Path(__file__).resolve().parent


def _load_module(module_name):
    spec = importlib.util.spec_from_file_location(
        module_name, _MIGRATION_DIR / f"{module_name}.py"
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


_m0009 = _load_module("0009_seed_intro_texts")
_m0011 = _load_module("0011_expand_intro_texts")
_m0012 = _load_module("0012_expand_subject_intro_texts")
_m0013 = _load_module("0013_unique_subchapter_intro_texts")


def forwards(apps, schema_editor):
    Subject = apps.get_model('CEE_Quiz', 'Subject')
    Chapter = apps.get_model('CEE_Quiz', 'Chapter')
    SubChapter = apps.get_model('CEE_Quiz', 'SubChapter')

    # Subjects: corrected 0009 base + corrected 0012 extra.
    for slug, base in _m0009.SUBJECT_INTROS.items():
        extra = _m0012.SUBJECT_INTRO_EXTRAS.get(slug, '')
        Subject.objects.filter(slug=slug).update(intro_text=base + extra)

    # Chapters: corrected 0009 text + 0011 closing paragraph.
    for slug, text in _m0009.CHAPTER_INTROS.items():
        Chapter.objects.filter(slug=slug).update(
            intro_text=_m0011.expand(text, '', '')
        )

    # SubChapters: corrected 0013 texts keyed by subchapter name.
    for name, text in _m0013.INTRO_TEXTS.items():
        SubChapter.objects.filter(name=name).update(intro_text=text)


def backwards(apps, schema_editor):
    # Intentionally a no-op: there is no meaningful reversal for a typo fix.
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('CEE_Quiz', '0013_unique_subchapter_intro_texts'),
    ]

    operations = [
        migrations.RunPython(forwards, backwards),
    ]
