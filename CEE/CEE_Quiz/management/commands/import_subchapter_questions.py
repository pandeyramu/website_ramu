import json
from pathlib import Path

from django.core.management.base import BaseCommand, CommandError

from CEE_Quiz.models import Chapter, Question, SubChapter


class Command(BaseCommand):
    help = (
        "Import questions from fixture-style JSON and support subchapter-wise storage. "
        "Each question item can include fields.sub_chapter as subchapter ID or name."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "json_path",
            type=str,
            help="Path to JSON file containing fixture-style question items.",
        )

    def handle(self, *args, **options):
        json_path = Path(options["json_path"]).resolve()
        if not json_path.exists():
            raise CommandError(f"File not found: {json_path}")

        try:
            with open(json_path, "r", encoding="utf-8") as file:
                data = json.load(file)
        except json.JSONDecodeError as exc:
            raise CommandError(f"Invalid JSON in {json_path}: {exc}") from exc

        if not isinstance(data, list):
            raise CommandError("JSON root must be a list of fixture objects.")

        created_count = 0
        skipped_count = 0

        for item in data:
            if item.get("model") != "CEE_Quiz.question":
                skipped_count += 1
                continue

            fields = item.get("fields", {})
            chapter_id = fields.get("chapter")
            if not chapter_id:
                self.stderr.write(self.style.WARNING("Skipped question without chapter."))
                skipped_count += 1
                continue

            try:
                chapter = Chapter.objects.get(id=chapter_id)
            except Chapter.DoesNotExist:
                self.stderr.write(self.style.WARNING(f"Skipped question: chapter {chapter_id} not found."))
                skipped_count += 1
                continue

            sub_chapter_ref = fields.get("sub_chapter")
            sub_chapter = None
            if sub_chapter_ref not in (None, ""):
                if isinstance(sub_chapter_ref, int):
                    sub_chapter = SubChapter.objects.filter(id=sub_chapter_ref, chapter=chapter).first()
                    if not sub_chapter:
                        self.stderr.write(self.style.WARNING(
                            f"Skipped question: sub_chapter id {sub_chapter_ref} is invalid for chapter {chapter.id}."
                        ))
                        skipped_count += 1
                        continue
                else:
                    name = str(sub_chapter_ref).strip()
                    if not name:
                        sub_chapter = None
                    else:
                        max_order = (
                            SubChapter.objects.filter(chapter=chapter)
                            .order_by("-order")
                            .values_list("order", flat=True)
                            .first()
                            or 0
                        )
                        sub_chapter, _ = SubChapter.objects.get_or_create(
                            chapter=chapter,
                            name=name,
                            defaults={"order": max_order + 1},
                        )

            Question.objects.create(
                chapter=chapter,
                sub_chapter=sub_chapter,
                question_text=fields.get("question_text", ""),
                option_a=fields.get("option_a", ""),
                option_b=fields.get("option_b", ""),
                option_c=fields.get("option_c", ""),
                option_d=fields.get("option_d", ""),
                correct_option=fields.get("correct_option", "A"),
            )
            created_count += 1

        self.stdout.write(self.style.SUCCESS(
            f"Import complete. Created {created_count} questions, skipped {skipped_count} entries."
        ))
