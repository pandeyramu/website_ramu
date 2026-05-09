import csv
import json
from pathlib import Path

from django.core.management.base import BaseCommand, CommandError

from CEE_Quiz.models import Subject, Chapter, SubChapter, Question


class Command(BaseCommand):
    help = "Import questions from a CSV into the CEE_Quiz app."

    def add_arguments(self, parser):
        parser.add_argument("csv_path", type=str, help="Path to CSV file to import")
        parser.add_argument(
            "--mapping-file",
            type=str,
            default="",
            help=(
                "Optional JSON file mapping CSV chapter codes to DB chapter IDs. "
                "Format: {\"PHY-1\": 12, \"CHE-1\": 9}"
            ),
        )
        parser.add_argument(
            "--create-missing",
            action="store_true",
            help="Create missing Subjects/Chapters/SubChapters when they don't exist.",
        )
        parser.add_argument(
            "--skip-duplicates",
            action="store_true",
            help="Skip questions with identical question_text already in DB.",
        )

    def _load_mapping(self, path_str):
        if not path_str:
            return {}
        path = Path(path_str)
        if not path.exists():
            raise CommandError(f"Mapping file not found: {path}")
        try:
            with path.open("r", encoding="utf-8") as fh:
                data = json.load(fh)
        except json.JSONDecodeError as exc:
            raise CommandError(f"Invalid JSON mapping file: {exc}") from exc
        if not isinstance(data, dict):
            raise CommandError("Mapping file root must be an object/dictionary.")
        return data

    def _resolve_chapter(self, code, mapping, create_missing):
        # mapping maps CSV code strings to integer Chapter IDs
        if not code:
            return None
        if code in mapping:
            try:
                return Chapter.objects.get(id=int(mapping[code]))
            except Chapter.DoesNotExist:
                raise CommandError(f"Mapped chapter id for '{code}' does not exist: {mapping[code]}")

        # try to find chapter by exact name or contains
        chap = Chapter.objects.filter(name__iexact=code).first()
        if chap:
            return chap
        chap = Chapter.objects.filter(name__icontains=code).first()
        if chap:
            return chap

        if not create_missing:
            return None

        # create Subject (use prefix before dash if present)
        subj_name = code.split("-")[0] if "-" in code else code
        subject, _ = Subject.objects.get_or_create(name=subj_name)
        new_chap = Chapter.objects.create(subject=subject, name=code)
        return new_chap

    def _resolve_subchapter(self, chapter, sub_id, create_missing):
        if not chapter or not sub_id:
            return None

        # try numeric id first
        try:
            sub_int = int(sub_id)
        except Exception:
            sub_int = None

        if sub_int is not None:
            # try id then order
            sub = SubChapter.objects.filter(id=sub_int, chapter=chapter).first()
            if sub:
                return sub
            sub = SubChapter.objects.filter(chapter=chapter, order=sub_int).first()
            if sub:
                return sub

        # try name
        sub = SubChapter.objects.filter(chapter=chapter, name__iexact=str(sub_id)).first()
        if sub:
            return sub

        sub = SubChapter.objects.filter(chapter=chapter, name__icontains=str(sub_id)).first()
        if sub:
            return sub

        if not create_missing:
            return None

        # create subchapter using the provided identifier as name
        order = sub_int if sub_int is not None else 0
        return SubChapter.objects.create(chapter=chapter, name=str(sub_id), order=order)

    def handle(self, *args, **options):
        csv_path = Path(options["csv_path"]).resolve()
        mapping = self._load_mapping(options.get("mapping_file", ""))
        create_missing = options["create_missing"]
        skip_duplicates = options["skip_duplicates"]

        if not csv_path.exists():
            raise CommandError(f"CSV file not found: {csv_path}")

        created = 0
        skipped = 0
        errors = 0

        with csv_path.open("r", encoding="utf-8") as fh:
            reader = csv.DictReader(fh)
            for i, row in enumerate(reader, start=1):
                try:
                    qtext = (row.get("question_text") or row.get("question") or "").strip()
                    if not qtext:
                        self.stdout.write(self.style.WARNING(f"Row {i}: empty question_text, skipping"))
                        skipped += 1
                        continue

                    if skip_duplicates and Question.objects.filter(question_text__iexact=qtext).exists():
                        skipped += 1
                        continue

                    chapter_code = (row.get("chapter_id") or "").strip()
                    sub_id = (row.get("sub_chapter_id") or row.get("subchapter") or "").strip()

                    chapter = self._resolve_chapter(chapter_code, mapping, create_missing)
                    if chapter is None:
                        self.stdout.write(self.style.WARNING(f"Row {i}: chapter '{chapter_code}' not found, use --create-missing or provide mapping"))
                        skipped += 1
                        continue

                    sub_chapter = self._resolve_subchapter(chapter, sub_id, create_missing)

                    question = Question(
                        chapter=chapter,
                        sub_chapter=sub_chapter,
                        question_text=qtext,
                        option_a=(row.get("option_a") or "").strip(),
                        option_b=(row.get("option_b") or "").strip(),
                        option_c=(row.get("option_c") or "").strip(),
                        option_d=(row.get("option_d") or "").strip(),
                        correct_option=((row.get("correct_option") or "").strip()[:1].upper() or "A"),
                        solution=(row.get("solution") or "").strip(),
                    )
                    question.save()
                    created += 1
                except Exception as exc:
                    self.stdout.write(self.style.ERROR(f"Row {i}: failed to import question: {exc}"))
                    errors += 1

        self.stdout.write(self.style.SUCCESS(f"Import finished: created={created} skipped={skipped} errors={errors}"))
