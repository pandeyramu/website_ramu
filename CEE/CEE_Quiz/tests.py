import os
import tempfile
from io import StringIO

from django.core.management import call_command
from django.test import TestCase

from .models import Chapter, Question, Subject, SubChapter


class ImportQuestionsCsvCommandTests(TestCase):
    def setUp(self):
        self.subject = Subject.objects.create(name="Chemistry")
        self.chapter = Chapter.objects.create(subject=self.subject, name="Organic", has_subchapters=True)
        self.subchapter = SubChapter.objects.create(chapter=self.chapter, name="Hydrocarbons", order=1)

    def _write_csv(self, rows):
        handle = tempfile.NamedTemporaryFile("w", newline="", encoding="utf-8", suffix=".csv", delete=False)
        handle.write(
            "chapter_id,sub_chapter_id,question_text,option_a,option_b,option_c,option_d,correct_option\n"
        )
        for row in rows:
            handle.write(",".join(row) + "\n")
        handle.close()
        self.addCleanup(lambda: os.path.exists(handle.name) and os.remove(handle.name))
        return handle.name

    def test_skips_question_already_present_in_database(self):
        Question.objects.create(
            chapter=self.chapter,
            sub_chapter=self.subchapter,
            question_text="What is benzene?",
            option_a="Alkane",
            option_b="Aromatic compound",
            option_c="Alcohol",
            option_d="Ester",
            correct_option="B",
        )

        csv_path = self._write_csv([
            [
                str(self.chapter.id),
                str(self.subchapter.id),
                "  What   is BENZENE?  ",
                "alkane",
                "Aromatic compound",
                "Alcohol",
                "Ester",
                "b",
            ]
        ])

        output = StringIO()
        call_command("import_questions_csv", csv_path, stdout=output)

        self.assertEqual(Question.objects.count(), 1)
        self.assertIn("Duplicate rows: 1", output.getvalue())

    def test_skips_duplicate_rows_within_same_csv(self):
        csv_path = self._write_csv([
            [
                str(self.chapter.id),
                str(self.subchapter.id),
                "What is methane?",
                "C2H6",
                "CH4",
                "C3H8",
                "C4H10",
                "B",
            ],
            [
                str(self.chapter.id),
                str(self.subchapter.id),
                "What is methane?",
                "C2H6",
                "CH4",
                "C3H8",
                "C4H10",
                "B",
            ],
        ])

        output = StringIO()
        call_command("import_questions_csv", csv_path, stdout=output)

        self.assertEqual(Question.objects.count(), 1)
        self.assertIn("Duplicate rows: 1", output.getvalue())

    def test_skips_same_question_text_when_answer_set_differs(self):
        Question.objects.create(
            chapter=self.chapter,
            sub_chapter=self.subchapter,
            question_text="What is the product?",
            option_a="Ethene",
            option_b="Ethyne",
            option_c="Ethane",
            option_d="Methane",
            correct_option="C",
        )

        csv_path = self._write_csv([
            [
                str(self.chapter.id),
                str(self.subchapter.id),
                "What is the product?",
                "Propene",
                "Propyne",
                "Propane",
                "Butane",
                "C",
            ]
        ])

        call_command("import_questions_csv", csv_path, stdout=StringIO())

        self.assertEqual(Question.objects.count(), 1)
