import csv
import json
from pathlib import Path
from django.core.management.base import BaseCommand, CommandError
from CEE_Quiz.models import Chapter, SubChapter, Question


class Command(BaseCommand):
    help = (
        "Import questions from a JSON file and assign them to subchapters.\n\n"
        "JSON format: list of objects with:\n"
        "  - chapter_id (required)\n"
        "  - sub_chapter_id (required, or 0 to skip)\n"
        "  - question_text (required)\n"
        "  - option_a, option_b, option_c, option_d (required)\n"
        "  - correct_option (required: A/B/C/D)\n"
        "  - solution (optional)\n"
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "json_file",
            type=str,
            help="Path to JSON file containing questions.",
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            default=False,
            help="Validate without writing to database.",
        )

    def handle(self, *args, **options):
        json_path = Path(options["json_file"]).resolve()
        dry_run = options["dry_run"]

        if not json_path.exists():
            raise CommandError(f"File not found: {json_path}")

        try:
            with open(json_path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except json.JSONDecodeError as exc:
            raise CommandError(f"Invalid JSON: {exc}") from exc

        if not isinstance(data, list):
            raise CommandError("JSON root must be a list of question objects.")

        rows_to_create = []
        errors = 0

        for idx, obj in enumerate(data, start=1):
            try:
                if not isinstance(obj, dict):
                    raise CommandError(f"Item #{idx} is not an object")

                chapter_id = obj.get("chapter_id")
                sub_chapter_id = obj.get("sub_chapter_id", 0)
                question_text = obj.get("question_text", "").strip()
                option_a = obj.get("option_a", "").strip()
                option_b = obj.get("option_b", "").strip()
                option_c = obj.get("option_c", "").strip()
                option_d = obj.get("option_d", "").strip()
                correct_option = str(obj.get("correct_option", "")).strip().upper()
                solution = obj.get("solution", "")

                if not chapter_id or not question_text:
                    raise CommandError(f"Missing chapter_id or question_text")

                if correct_option not in ["A", "B", "C", "D"]:
                    raise CommandError(f"correct_option must be A/B/C/D, got '{correct_option}'")

                if not all([option_a, option_b, option_c, option_d]):
                    raise CommandError(f"Missing one or more options")

                question = Question(
                    chapter_id=chapter_id,
                    sub_chapter_id=sub_chapter_id if sub_chapter_id and sub_chapter_id > 0 else None,
                    question_text=question_text,
                    option_a=option_a,
                    option_b=option_b,
                    option_c=option_c,
                    option_d=option_d,
                    correct_option=correct_option,
                    solution=solution or "",
                )
                rows_to_create.append(question)

            except Exception as e:
                errors += 1
                self.stdout.write(self.style.WARNING(f"Item #{idx}: {str(e)}"))

        self.stdout.write(f"Items parsed: {len(data)}")
        self.stdout.write(f"Parse errors: {errors}")
        self.stdout.write(f"Questions to create: {len(rows_to_create)}")

        if dry_run:
            self.stdout.write(self.style.SUCCESS("Dry run complete."))
            return

        if rows_to_create:
            Question.objects.bulk_create(rows_to_create, batch_size=500)
            self.stdout.write(self.style.SUCCESS(f"Created {len(rows_to_create)} questions."))
