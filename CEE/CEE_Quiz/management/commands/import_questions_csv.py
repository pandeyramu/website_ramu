import csv
import os
import sys
from django.core.management.base import BaseCommand, CommandError
from CEE_Quiz.models import Chapter, SubChapter, Question


class Command(BaseCommand):
    help = (
        "Import questions from a CSV file.\n\n"
        "CSV columns (in order):\n"
        "  chapter_id, sub_chapter_id, question_text, "
        "option_a, option_b, option_c, option_d, correct_option\n\n"
        "- chapter_id      : integer, required\n"
        "- sub_chapter_id  : integer, required — must match a SubChapter.id that belongs to the chapter\n"
        "- correct_option  : A / B / C / D\n\n"
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

    def handle(self, *args, **options):
        csv_path = options["csv_file"]
        dry_run = options["dry_run"]
        skip_errors = options["skip_errors"]
        force_chapter_id = options["chapter_id"]

        if not os.path.isfile(csv_path):
            raise CommandError(f"File not found: {csv_path}")

        # Pre-load chapters and subchapters into memory for fast lookup
        chapter_cache = {c.id: c for c in Chapter.objects.all()}
        subchapter_cache = {s.id: s for s in SubChapter.objects.all()}

        if not chapter_cache:
            raise CommandError("No chapters found in database. Run 'python manage.py seed_all' first.")

        # Pre-load existing question stems from DB for duplicate detection across repeated imports.
        self.stdout.write("Loading existing questions from database for duplicate check...")
        existing_signatures = {
            self._question_signature(
                chapter_id=question.chapter_id,
                sub_chapter_id=question.sub_chapter_id,
                question_text=question.question_text,
            )
            for question in Question.objects.only(
                "chapter_id",
                "sub_chapter_id",
                "question_text",
            )
        }
        self.stdout.write(f"  {len(existing_signatures)} questions already in database.")

        valid_options = {"A", "B", "C", "D"}
        required_columns = {
            "chapter_id", "sub_chapter_id", "question_text",
            "option_a", "option_b", "option_c", "option_d", "correct_option",
        }

        rows_ok = []
        rows_error = []
        rows_duplicate = []
        seen_in_csv = set()

        self.stdout.write(f"\nReading: {csv_path}")
        if dry_run:
            self.stdout.write(self.style.WARNING("  [DRY RUN — no changes will be written]\n"))

        with open(csv_path, newline="", encoding="utf-8-sig") as f:
            reader = csv.DictReader(f, skipinitialspace=True)

            # Validate headers
            if reader.fieldnames is None:
                raise CommandError("CSV file appears to be empty.")
            missing = required_columns - {col.strip() for col in reader.fieldnames}
            if missing:
                raise CommandError(
                    f"CSV is missing required columns: {', '.join(sorted(missing))}\n"
                    f"Expected columns: chapter_id, sub_chapter_id, question_text, "
                    f"option_a, option_b, option_c, option_d, correct_option"
                )

            for line_num, raw_row in enumerate(reader, start=2):  # 2 = first data row
                row = {k.strip(): (v.strip() if v else "") for k, v in raw_row.items() if k is not None}
                errors = []

                # --- chapter_id ---
                if force_chapter_id:
                    chapter_id = force_chapter_id
                else:
                    raw_ch = row.get("chapter_id", "")
                    if not raw_ch:
                        errors.append("chapter_id is empty")
                        chapter_id = None
                    elif not raw_ch.isdigit():
                        errors.append(f"chapter_id '{raw_ch}' is not an integer")
                        chapter_id = None
                    else:
                        chapter_id = int(raw_ch)

                if chapter_id is not None and chapter_id not in chapter_cache:
                    errors.append(f"chapter_id {chapter_id} does not exist in database")
                    chapter_id = None

                chapter = chapter_cache.get(chapter_id) if chapter_id else None

                # --- sub_chapter_id (required) ---
                sub_chapter = None
                raw_sc = row.get("sub_chapter_id", "")
                if not raw_sc:
                    errors.append("sub_chapter_id is required — every question must belong to a subchapter")
                elif not raw_sc.isdigit():
                    errors.append(f"sub_chapter_id '{raw_sc}' is not an integer")
                else:
                    sc_id = int(raw_sc)
                    if sc_id not in subchapter_cache:
                        errors.append(f"sub_chapter_id {sc_id} does not exist in database")
                    else:
                        sub_chapter = subchapter_cache[sc_id]
                        # Verify sub_chapter belongs to the chapter
                        if chapter and sub_chapter.chapter_id != chapter.id:
                            errors.append(
                                f"sub_chapter_id {sc_id} belongs to chapter "
                                f"{sub_chapter.chapter_id}, not chapter {chapter.id}"
                            )
                            sub_chapter = None

                # --- question_text ---
                q_text = row.get("question_text", "")
                if not q_text:
                    errors.append("question_text is empty")

                # --- options ---
                opt_a = row.get("option_a", "")
                opt_b = row.get("option_b", "")
                opt_c = row.get("option_c", "")
                opt_d = row.get("option_d", "")
                for label, val in [("option_a", opt_a), ("option_b", opt_b),
                                   ("option_c", opt_c), ("option_d", opt_d)]:
                    if not val:
                        errors.append(f"{label} is empty")

                # --- correct_option ---
                correct = row.get("correct_option", "").upper()
                if correct not in valid_options:
                    errors.append(f"correct_option '{correct}' must be A, B, C, or D")

                # --- duplicate check (DB + current CSV/import batch) ---
                if q_text and not errors:
                    signature = self._question_signature(
                        chapter_id=chapter.id,
                        sub_chapter_id=sub_chapter.id if sub_chapter else None,
                        question_text=q_text,
                    )
                    if signature in existing_signatures:
                        rows_duplicate.append((line_num, "already in database", q_text))
                        self.stdout.write(self.style.WARNING(
                            f"  Line {line_num}: DUPLICATE (DB) — {q_text[:80]}"
                        ))
                        continue
                    if signature in seen_in_csv:
                        rows_duplicate.append((line_num, "duplicate within CSV", q_text))
                        self.stdout.write(self.style.WARNING(
                            f"  Line {line_num}: DUPLICATE (CSV) — {q_text[:80]}"
                        ))
                        continue
                    seen_in_csv.add(signature)

                if errors:
                    rows_error.append((line_num, errors, row))
                    msg = f"  Line {line_num}: ERRORS — " + "; ".join(errors)
                    if skip_errors:
                        self.stdout.write(self.style.WARNING(msg + " (skipped)"))
                    else:
                        self.stdout.write(self.style.ERROR(msg))
                else:
                    rows_ok.append({
                        "chapter": chapter,
                        "sub_chapter": sub_chapter,
                        "question_text": q_text,
                        "option_a": opt_a,
                        "option_b": opt_b,
                        "option_c": opt_c,
                        "option_d": opt_d,
                        "correct_option": correct,
                    })

        # Abort if errors and not skip-errors
        if rows_error and not skip_errors and not dry_run:
            self.stdout.write(self.style.ERROR(
                f"\nAborted: {len(rows_error)} row(s) had errors. "
                f"Fix them or rerun with --skip-errors."
            ))
            sys.exit(1)

        self.stdout.write(f"\n  Valid rows   : {len(rows_ok)}")
        self.stdout.write(f"  Duplicate rows: {len(rows_duplicate)} (skipped)")
        self.stdout.write(f"  Error rows   : {len(rows_error)}")

        if dry_run:
            self.stdout.write(self.style.SUCCESS("\nDry run complete — nothing written."))
            if rows_ok:
                self.stdout.write("\nSample of valid rows that WOULD be imported:")
                for r in rows_ok[:5]:
                    self.stdout.write(
                        f"  chapter={r['chapter'].id} | "
                        f"sub_chapter={r['sub_chapter'].id if r['sub_chapter'] else 'None'} | "
                        f"correct={r['correct_option']} | "
                        f"q={r['question_text'][:60]}"
                    )
                if len(rows_ok) > 5:
                    self.stdout.write(f"  ... and {len(rows_ok) - 5} more")
            return

        # --- Bulk insert ---
        if not rows_ok:
            self.stdout.write(self.style.WARNING("\nNo valid rows to import."))
            return

        self.stdout.write(f"\nImporting {len(rows_ok)} questions...")

        batch_size = 500
        created = 0
        for i in range(0, len(rows_ok), batch_size):
            batch = rows_ok[i: i + batch_size]
            objs = [
                Question(
                    chapter=r["chapter"],
                    sub_chapter=r["sub_chapter"],
                    question_text=r["question_text"],
                    option_a=r["option_a"],
                    option_b=r["option_b"],
                    option_c=r["option_c"],
                    option_d=r["option_d"],
                    correct_option=r["correct_option"],
                )
                for r in batch
            ]
            Question.objects.bulk_create(objs)
            created += len(objs)
            self.stdout.write(f"  ... {created}/{len(rows_ok)} inserted")

        total_in_db = Question.objects.count()
        self.stdout.write(self.style.SUCCESS(
            f"\nDone! Imported {created} question(s). "
            f"Duplicates skipped: {len(rows_duplicate)}. "
            f"Total questions in database: {total_in_db}"
        ))
        if rows_error:
            self.stdout.write(self.style.WARNING(
                f"{len(rows_error)} row(s) were skipped due to errors."
            ))
