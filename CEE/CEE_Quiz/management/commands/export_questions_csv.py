import csv
from pathlib import Path

from django.core.management.base import BaseCommand, CommandError

from CEE_Quiz.models import Question


class Command(BaseCommand):
    help = "Export the Question table to a CSV file for Supabase upload."

    def add_arguments(self, parser):
        parser.add_argument(
            "--output",
            type=str,
            default="questions_export.csv",
            help="Output CSV path. Defaults to questions_export.csv in the current directory.",
        )

    def handle(self, *args, **options):
        output_path = Path(options["output"]).expanduser().resolve()
        output_path.parent.mkdir(parents=True, exist_ok=True)

        questions = Question.objects.all().order_by("id")
        if not questions.exists():
            raise CommandError("No questions found to export.")

        fieldnames = [
            "id",
            "question_text",
            "solution",
            "option_a",
            "option_b",
            "option_c",
            "option_d",
            "correct_option",
            "chapter_id",
            "sub_chapter_id",
        ]

        with output_path.open("w", encoding="utf-8", newline="") as csv_file:
            writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
            writer.writeheader()

            for question in questions.iterator(chunk_size=1000):
                writer.writerow(
                    {
                        "id": question.id,
                        "question_text": question.question_text,
                        "solution": question.solution or "",
                        "option_a": question.option_a,
                        "option_b": question.option_b,
                        "option_c": question.option_c,
                        "option_d": question.option_d,
                        "correct_option": question.correct_option,
                        "chapter_id": question.chapter_id,
                        "sub_chapter_id": question.sub_chapter_id or "",
                    }
                )

        self.stdout.write(self.style.SUCCESS(f"Exported {questions.count()} questions to {output_path}"))