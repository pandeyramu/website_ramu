from django.core.management.base import BaseCommand
from CEE_Quiz.models import Chapter, SubChapter


ORGANIC_CHEMISTRY_SUBCHAPTERS = [
    "Some Basic Principles",
    "Purification and Characterization",
    "Nomenclature of Organic Compound",
    "Isomerism",
    "Reaction Mechanism",
    "Hydrocarbons",
    "Halogen Derivatives",
    "Alcohol",
    "Phenols",
    "Ether",
    "Carbonyl Compounds",
    "Carboxylic Compounds and their derivatives",
    "Compounds Containing Nitrogen",
    "The Molecules of life",
    "Polymer and Polymerization",
    "Chemistry In action",
    "Organometallic Compounds",
]


def _normalize_name(value):
    return " ".join(value.strip().split()).lower()


class Command(BaseCommand):
    help = "Seed Organic Chemistry subchapters into the database"

    def add_arguments(self, parser):
        parser.add_argument(
            '--chapter-id',
            type=int,
            help='Explicit chapter ID to seed (recommended when chapter names are ambiguous).',
        )

    def handle(self, *args, **options):
        chapter_id = options.get('chapter_id')

        if chapter_id:
            try:
                chapter = Chapter.objects.get(id=chapter_id)
            except Chapter.DoesNotExist:
                self.stderr.write(self.style.ERROR(f'Chapter with ID {chapter_id} not found.'))
                return
        else:
            exact_matches = Chapter.objects.filter(name__iexact="Organic chemistry")
            if exact_matches.exists():
                chapter = exact_matches.first()
            else:
                candidates = [
                    ch for ch in Chapter.objects.filter(name__icontains="organic")
                    if "inorganic" not in ch.name.lower()
                ]
                if len(candidates) == 1:
                    chapter = candidates[0]
                elif len(candidates) > 1:
                    self.stderr.write(self.style.ERROR(
                        'Multiple Organic chapter candidates found. Please rerun with --chapter-id. Candidates:'
                    ))
                    for ch in candidates:
                        self.stderr.write(f"  - {ch.id}: {ch.name} ({ch.subject.name})")
                    return
                else:
                    self.stderr.write(self.style.ERROR(
                        'Could not find Organic Chemistry chapter. Available chapters:'
                    ))
                    for ch in Chapter.objects.all():
                        self.stderr.write(f"  - {ch.id}: {ch.name} ({ch.subject.name})")
                    return

        self.stdout.write(f"Found chapter: {chapter.name} (ID: {chapter.id})")

        # Mark chapter as having subchapters
        chapter.has_subchapters = True
        chapter.save()
        self.stdout.write(self.style.SUCCESS(f"  ✓ Marked '{chapter.name}' as having subchapters"))

        # Create or update subchapters to exact target names/order
        existing_subchapters = list(SubChapter.objects.filter(chapter=chapter).order_by('order', 'id'))
        existing_by_key = {}
        for sub in existing_subchapters:
            key = _normalize_name(sub.name)
            if key not in existing_by_key:
                existing_by_key[key] = sub

        created_count = 0
        updated_count = 0
        for order, name in enumerate(ORGANIC_CHEMISTRY_SUBCHAPTERS, start=1):
            key = _normalize_name(name)
            matched = existing_by_key.get(key)

            if matched:
                changed = False
                if matched.name != name:
                    matched.name = name
                    changed = True
                if matched.order != order:
                    matched.order = order
                    changed = True
                if changed:
                    matched.save(update_fields=['name', 'order'])
                    updated_count += 1
                    self.stdout.write(f"  ↻ Updated: {order}. {name}")
                else:
                    self.stdout.write(f"  - Already correct: {order}. {name}")
                continue

            sub = SubChapter.objects.create(
                chapter=chapter,
                name=name,
                order=order,
            )
            if sub:
                created_count += 1
                self.stdout.write(f"  ✓ Created: {order}. {name}")

        self.stdout.write(self.style.SUCCESS(
            f"\nDone! {created_count} new subchapters created, {updated_count} updated. "
            f"Total: {SubChapter.objects.filter(chapter=chapter).count()} subchapters."
        ))
