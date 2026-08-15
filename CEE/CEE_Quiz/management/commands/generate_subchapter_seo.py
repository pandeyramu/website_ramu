from django.core.management.base import BaseCommand

from CEE_Quiz.models import SubChapter

MAX_LENGTH = 158


def clean_intro(text):
    return " ".join((text or "").replace("\r", " ").replace("\n", " ").split())


def trim_to_limit(text, limit=MAX_LENGTH):
    if len(text) <= limit:
        return text
    cut = text[:limit]
    if " " in cut:
        cut = cut.rsplit(" ", 1)[0]
    return cut


def build_description(sub):
    intro = clean_intro(getattr(sub, "intro_text", ""))
    if intro:
        return trim_to_limit(intro)
    chapter_name = sub.chapter.name if sub.chapter else ""
    return f"Practice {sub.name} MCQ from {chapter_name} for the Common Entrance Examination."


class Command(BaseCommand):
    help = "Generate seo_description for subchapters from their intro_text"

    def add_arguments(self, parser):
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Show what would change without saving",
        )
        parser.add_argument(
            "--overwrite",
            action="store_true",
            help="Regenerate descriptions even for subchapters that already have one",
        )

    def handle(self, *args, **options):
        dry_run = options.get("dry_run")
        overwrite = options.get("overwrite")

        qs = SubChapter.objects.select_related("chapter").all()
        total = 0
        updated = 0

        for sub in qs:
            total += 1
            if not overwrite and sub.seo_description and sub.seo_description.strip():
                continue
            desc = build_description(sub)
            self.stdout.write(f"  id={sub.pk} {sub.name} ({len(desc)} chars)")
            updated += 1
            if not dry_run:
                sub.seo_description = desc
                sub.save(update_fields=["seo_description"])

        self.stdout.write("")
        self.stdout.write(f"Total subchapters scanned: {total}")
        self.stdout.write(f"Descriptions generated: {updated}")
        if dry_run:
            self.stdout.write("(dry-run; no database changes were made)")
