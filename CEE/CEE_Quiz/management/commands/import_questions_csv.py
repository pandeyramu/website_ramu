import csv
import os
import re
import sys
from django.core.management.base import BaseCommand, CommandError
from CEE_Quiz.models import Chapter, SubChapter, Question


class Command(BaseCommand):
    help = (
        "Import questions from a CSV file.\n\n"
        "CSV columns (in order):\n"
        "  chapter_id, sub_chapter_id, question_text, "
        "option_a, option_b, option_c, option_d, correct_option, solution(optional)\n\n"
        "- chapter_id      : integer, required\n"
        "- sub_chapter_id  : integer, required — must match a SubChapter.id that belongs to the chapter\n"
        "- correct_option  : A / B / C / D\n\n"
        "- solution        : optional text shown after submission in review mode\n\n"
        "Usage:\n"
        "  python manage.py import_questions_csv questions.csv\n"
        "  python manage.py import_questions_csv questions.csv --dry-run\n"
        "  python manage.py import_questions_csv questions.csv --skip-errors\n"
        "  python manage.py import_questions_csv questions.csv --chapter-id 1\n"
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "csv_file",
            type=str,
            help="Path to the CSV file to import.",
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            default=False,
            help="Parse and validate without writing to the database.",
        )
        parser.add_argument(
            "--skip-errors",
            action="store_true",
            default=False,
            help="Skip rows with errors instead of aborting.",
        )
        parser.add_argument(
            "--chapter-id",
            type=int,
            default=None,
            help="Only import rows for this chapter ID (ignores chapter_id column).",
        )
        parser.add_argument(
            "--update-duplicates",
            action="store_true",
            default=False,
            help=(
                "When a question already exists (same chapter, subchapter, and normalized question text), "
                "update its options/correct_option instead of skipping it."
            ),
        )
        parser.add_argument(
            "--update-solution-only",
            action="store_true",
            default=False,
            help=(
                "Only update solution for existing matched questions. "
                "Requires --update-duplicates and skips rows that are not already in DB."
            ),
        )

    @staticmethod
    def _norm(text):
        """Normalise question text for duplicate comparison: lowercase, collapse whitespace."""
        return " ".join(text.lower().split())

    def _question_signature(self, *, chapter_id, sub_chapter_id, question_text):
        return (
            chapter_id,
            sub_chapter_id,
            self._norm(question_text),
        )

    @staticmethod
    def _clean_solution(text):
        """Remove model-thought blocks and keep answer text from Explanation onward."""
        cleaned = text or ""
        cleaned = re.sub(r"(?is)<think>.*?</think>", "", cleaned)

        # Repair common malformed escape artifacts from source JSON/CSV.
        # Example: "\times" may arrive as tab + "imes" when backslash+t is decoded.
        cleaned = re.sub(r"\t(?=[A-Za-z])", r"\\t", cleaned)
        cleaned = re.sub(r"\x07(?=[A-Za-z])", r"\\a", cleaned)

        # If present, keep only from the first "Explanation" marker.
        explanation_match = re.search(r"(?is)\bexplanation\b\s*:\s*", cleaned)
        if explanation_match:
            cleaned = cleaned[explanation_match.start():]

        cleaned = re.sub(r"\n{3,}", "\n\n", cleaned)
        return cleaned.strip()

    def handle(self, *args, **options):
        csv_path = options["csv_file"]
        dry_run = options["dry_run"]
        skip_errors = options["skip_errors"]
        force_chapter_id = options["chapter_id"]
        update_duplicates = options["update_duplicates"]
        update_solution_only = options["update_solution_only"]

        if update_solution_only and not update_duplicates:
            raise CommandError("--update-solution-only requires --update-duplicates")

        if not os.path.isfile(csv_path):
            raise CommandError(f"File not found: {csv_path}")

        # Pre-load chapters and subchapters into memory for fast lookup
        chapter_cache = {c.id: c for c in Chapter.objects.all()}
        subchapter_cache = {s.id: s for s in SubChapter.objects.all()}

        if not chapter_cache:
            raise CommandError("No chapters found in database. Run 'python manage.py seed_all' first.")

        # Pre-load existing questions for duplicate detection
        existing_by_signature = {}
        for question in Question.objects.all().only(
            "id",
            "chapter_id",
            "sub_chapter_id",
            "question_text",
            "option_a",
            "option_b",
            "option_c",
            "option_d",
            "correct_option",
            "solution",
        ):
            signature = self._question_signature(
                chapter_id=question.chapter_id,
                sub_chapter_id=question.sub_chapter_id,
                question_text=question.question_text,
            )
            if signature not in existing_by_signature:
                existing_by_signature[signature] = question
        self.stdout.write(f"  {len(existing_by_signature)} questions already in database.")

        # Parse CSV and collect rows
        required_columns = [
            "chapter_id", "sub_chapter_id", "question_text",
            "option_a", "option_b", "option_c", "option_d", "correct_option",
        ]
        rows_to_create = []
        rows_to_update = []
        row_count = 0
        error_count = 0

        try:
            with open(csv_path, "r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                if reader.fieldnames is None:
                    raise CommandError(f"CSV file is empty: {csv_path}")

                for column in required_columns:
                    if column not in reader.fieldnames:
                        raise CommandError(
                            f"Expected columns: chapter_id, sub_chapter_id, question_text, "
                            f"option_a, option_b, option_c, option_d, correct_option, (solution optional)"
                        )

                for row in reader:
                    row_count += 1
                    errors = []

                    # --- chapter_id ---
                    ch_str = row.get("chapter_id", "").strip()
                    if not ch_str or not ch_str.isdigit():
                        errors.append(f"chapter_id is missing or not numeric: '{ch_str}'")
                    else:
                        chapter_id = int(ch_str)
                        if chapter_id not in chapter_cache:
                            errors.append(f"chapter_id {chapter_id} not found")
                        elif force_chapter_id is not None and chapter_id != force_chapter_id:
                            chapter_id = force_chapter_id

                    # --- sub_chapter_id ---
                    sub_str = row.get("sub_chapter_id", "").strip()
                    if not sub_str or not sub_str.isdigit():
                        errors.append(f"sub_chapter_id is missing or not numeric: '{sub_str}'")
                    else:
                        sub_chapter_id = int(sub_str)
                        if sub_chapter_id and sub_chapter_id not in subchapter_cache:
                            errors.append(f"sub_chapter_id {sub_chapter_id} not found")

                    # --- question_text ---
                    q_text = row.get("question_text", "")
                    if not q_text.strip():
                        errors.append("question_text is empty")

                    # --- options ---
                    opt_a = row.get("option_a", "").strip()
                    opt_b = row.get("option_b", "").strip()
                    opt_c = row.get("option_c", "").strip()
                    opt_d = row.get("option_d", "").strip()
                    for opt_name, opt_val in [("A", opt_a), ("B", opt_b), ("C", opt_c), ("D", opt_d)]:
                        if not opt_val:
                            errors.append(f"option_{opt_name} is empty")

                    # --- correct_option ---
                    cor_opt = row.get("correct_option", "").strip().upper()
                    if cor_opt not in ["A", "B", "C", "D"]:
                        errors.append(f"correct_option must be A, B, C, or D: got '{cor_opt}'")

                    if errors:
                        error_count += 1
                        if skip_errors:
                            self.stdout.write(self.style.WARNING(f"Row {row_count}: {'; '.join(errors)}"))
                            continue
                        raise CommandError(f"Row {row_count}: {'; '.join(errors)}")

                    # --- solution (optional) ---
                    solution = row.get("solution", "")
                    if solution:
                        solution = self._clean_solution(solution)

                    # --- Check for duplicates ---
                    signature = self._question_signature(
                        chapter_id=chapter_id,
                        sub_chapter_id=sub_chapter_id,
                        question_text=q_text,
                    )

                    if signature in existing_by_signature:
                        if update_solution_only:
                            existing = existing_by_signature[signature]
                            existing.solution = solution
                            rows_to_update.append(existing)
                        elif update_duplicates:
                            existing = existing_by_signature[signature]
                            existing.option_a = opt_a
                            existing.option_b = opt_b
                            existing.option_c = opt_c
                            existing.option_d = opt_d
                            existing.correct_option = cor_opt
                            if solution:
                                existing.solution = solution
                            rows_to_update.append(existing)
                        continue

                    # --- Create new question ---
                    question = Question(
                        chapter_id=chapter_id,
                        sub_chapter_id=sub_chapter_id,
                        question_text=q_text,
                        option_a=opt_a,
                        option_b=opt_b,
                        option_c=opt_c,
                        option_d=opt_d,
                        correct_option=cor_opt,
                        solution=solution or "",
                    )
                    rows_to_create.append(question)
                    existing_by_signature[signature] = question

        except csv.Error as exc:
            raise CommandError(f"CSV parse error: {exc}") from exc

        # --- Summary ---
        self.stdout.write(f"Rows parsed         : {row_count}")
        self.stdout.write(f"Parse errors        : {error_count}")
        self.stdout.write(f"New questions       : {len(rows_to_create)}")
        self.stdout.write(f"Questions to update : {len(rows_to_update)}")

        if dry_run:
            self.stdout.write(self.style.SUCCESS("Dry run complete. No database changes."))
            return

        if rows_to_create:
            Question.objects.bulk_create(rows_to_create, batch_size=500)
            self.stdout.write(self.style.SUCCESS(f"Created {len(rows_to_create)} questions."))

        if rows_to_update:
            Question.objects.bulk_update(rows_to_update, ["option_a", "option_b", "option_c", "option_d", "correct_option", "solution"], batch_size=500)
            self.stdout.write(self.style.SUCCESS(f"Updated {len(rows_to_update)} questions."))

        self.stdout.write(self.style.SUCCESS("Import complete."))
