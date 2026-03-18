from django.core.management.base import BaseCommand

from CEE_Quiz.models import Chapter, SubChapter


SUBCHAPTERS_BY_CHAPTER_ID = {
    12: [
        "Virus",
        "Kingdom Monera",
        "Kingdom Mycota",
        "Algae",
        "Bryophytes",
        "Pteridophytes",
        "Gymnosperms",
        "Morphology of Angiosperms",
        "Taxonomy of Angiosperms",
    ],
    13: [
        "Ecology and COnservation",
    ],
    14: [
        "Cell Biology",
        "Cell Cycle and Reproduction",
        "Genetics: Inheritance and Variation",
        "Genetic Materials",
    ],
    15: [
        "Plant Anatomy",
        "Water Relation",
        "Transpiration",
        "Photosynthesis",
        "Respiration",
    ],
    16: [
        "Growth and Development",
        "Development Biology",
        "Application and Biology",
    ],
    17: [
        "Introduction to Biology",
        "Origin and Evolution",
    ],
    18: [
        "Kingdom Protista",
        "Kingdom Animalia I",
        "Kingdom Animalia II",
        "Chordates Characters",
    ],
    19: [
        "Earthworm",
        "Frog",
        "Plasmodium",
    ],
    20: [
        "Nervous System",
        "Receptors and Sense Organs",
        "Cardiovascular System",
        "Endocrinology",
        "Respiratory System",
        "Digestive System",
        "Excretory System",
        "Reproductive System",
        "Developmental Biology",
        "Substances Abuse and Human Diseases",
    ],
    21: [
        "Animal Tissues",
    ],
    22: [
        "Behaviour and Adaptation",
    ],
}


def _normalize_name(value):
    return " ".join(value.strip().split()).lower().rstrip(".")


class Command(BaseCommand):
    help = "Seed subchapters for Biology chapters (12-22)."

    def handle(self, *args, **options):
        total_created = 0
        total_updated = 0

        for chapter_id, target_names in SUBCHAPTERS_BY_CHAPTER_ID.items():
            try:
                chapter = Chapter.objects.get(id=chapter_id)
            except Chapter.DoesNotExist:
                self.stderr.write(self.style.WARNING(f"Skipped chapter {chapter_id}: not found."))
                continue

            chapter.has_subchapters = True
            chapter.save(update_fields=['has_subchapters'])

            existing_subchapters = list(
                SubChapter.objects.filter(chapter=chapter).order_by('order', 'id')
            )
            existing_by_key = {}
            for sub in existing_subchapters:
                key = _normalize_name(sub.name)
                if key not in existing_by_key:
                    existing_by_key[key] = sub

            created_count = 0
            updated_count = 0

            self.stdout.write(f"\nChapter {chapter.id}: {chapter.name}")

            for order, name in enumerate(target_names, start=1):
                key = _normalize_name(name)
                matched = existing_by_key.get(key)

                if matched:
                    changed = False
                    clean_name = name.rstrip('.')
                    if matched.name != clean_name:
                        matched.name = clean_name
                        changed = True
                    if matched.order != order:
                        matched.order = order
                        changed = True
                    if changed:
                        matched.save(update_fields=['name', 'order'])
                        updated_count += 1
                        self.stdout.write(f"  ↻ Updated: {order}. {clean_name}")
                    else:
                        self.stdout.write(f"  - Already correct: {order}. {clean_name}")
                    continue

                clean_name = name.rstrip('.')
                SubChapter.objects.create(
                    chapter=chapter,
                    name=clean_name,
                    order=order,
                )
                created_count += 1
                self.stdout.write(f"  ✓ Created: {order}. {clean_name}")

            total_created += created_count
            total_updated += updated_count
            total_for_chapter = SubChapter.objects.filter(chapter=chapter).count()

            self.stdout.write(self.style.SUCCESS(
                f"  => Done for chapter {chapter.id}: created {created_count}, "
                f"updated {updated_count}, total {total_for_chapter}"
            ))

        self.stdout.write(self.style.SUCCESS(
            f"\nAll done. Total created: {total_created}, total updated: {total_updated}."
        ))
