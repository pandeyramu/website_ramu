from django.core.management.base import BaseCommand
from django.utils.text import slugify

from CEE_Quiz.models import Subject, Chapter, SubChapter


def unique_slug(model, base_slug, instance_id=None):
    slug = base_slug
    suffix = 1
    qs = model.objects
    while True:
        conflict = qs.filter(slug=slug)
        if instance_id is not None:
            conflict = conflict.exclude(pk=instance_id)
        if not conflict.exists():
            return slug
        slug = f"{base_slug}-{suffix}"
        suffix += 1


class Command(BaseCommand):
    help = "Populate slug fields for Subject, Chapter, and SubChapter records"

    def add_arguments(self, parser):
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Show changes without saving",
        )

    def handle(self, *args, **options):
        dry_run = options.get("dry_run")
        total = 0
        updated = 0

        models = [Subject, Chapter, SubChapter]
        for model in models:
            name = model.__name__
            self.stdout.write(f"Processing {name}...")
            objs = model.objects.all()
            for obj in objs:
                total += 1
                if getattr(obj, "slug", None):
                    continue
                base = slugify(getattr(obj, "name", "")) or f"{name.lower()}"
                slug = unique_slug(model, base, instance_id=getattr(obj, "pk", None))
                self.stdout.write(f"  {name} id={obj.pk}: set slug -> {slug}")
                updated += 1
                if not dry_run:
                    obj.slug = slug
                    obj.save()

        self.stdout.write("")
        self.stdout.write(f"Total records scanned: {total}")
        self.stdout.write(f"Slugs added: {updated}")
        if dry_run:
            self.stdout.write("(dry-run; no database changes were made)")
