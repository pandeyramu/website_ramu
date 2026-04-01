import os
import tempfile
import csv
import json
from io import StringIO

from django.core.management import call_command
from django.core.management.base import CommandError
from django.test import TestCase

from .models import Chapter, Question, Subject, SubChapter


class ImportQuestionsCsvCommandTests(TestCase):
    def setUp(self):
        self.subject = Subject.objects.create(name="Chemistry")
        self.chapter = Chapter.objects.create(subject=self.subject, name="Organic", has_subchapters=True)
        self.subchapter = SubChapter.objects.create(chapter=self.chapter, name="Hydrocarbons", order=1)

    def _write_csv(self, rows):
        handle = tempfile.NamedTemporaryFile("w", newline="", encoding="utf-8", suffix=".csv", delete=False)
        writer = csv.writer(handle)
        writer.writerow([
            "chapter_id",
            "sub_chapter_id",
            "question_text",
            "option_a",
            "option_b",
            "option_c",
            "option_d",
            "correct_option",
            "solution",
        ])
        writer.writerows(rows)
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
                "Benzene has a delocalized pi-electron system, so it is aromatic.",
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
                "Methane is CH4, the first alkane in the homologous series.",
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
                "Duplicate row should be skipped.",
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
                "Product remains unchanged for duplicate-by-stem behavior.",
            ]
        ])

        call_command("import_questions_csv", csv_path, stdout=StringIO())

        self.assertEqual(Question.objects.count(), 1)

    def test_updates_existing_question_when_flag_enabled(self):
        existing = Question.objects.create(
            chapter=self.chapter,
            sub_chapter=self.subchapter,
            question_text="Which is aromatic?",
            option_a="Cyclohexane",
            option_b="Benzene",
            option_c="Ethanol",
            option_d="Acetone",
            correct_option="B",
        )

        csv_path = self._write_csv([
            [
                str(self.chapter.id),
                str(self.subchapter.id),
                "Which is aromatic?",
                "Cyclohexene",
                "Cyclohexane",
                "Benzene",
                "Methanol",
                "C",
                "Benzene is aromatic because of cyclic conjugation and Huckel rule.",
            ]
        ])

        output = StringIO()
        call_command("import_questions_csv", csv_path, "--update-duplicates", stdout=output)

        self.assertEqual(Question.objects.count(), 1)
        existing.refresh_from_db()
        self.assertEqual(existing.option_a, "Cyclohexene")
        self.assertEqual(existing.option_b, "Cyclohexane")
        self.assertEqual(existing.option_c, "Benzene")
        self.assertEqual(existing.option_d, "Methanol")
        self.assertEqual(existing.correct_option, "C")
        self.assertEqual(existing.solution, "Benzene is aromatic because of cyclic conjugation and Huckel rule.")
        self.assertIn("Updated 1 existing question(s)", output.getvalue())

    def test_reconstructs_unquoted_solution_tail_from_extra_columns(self):
        handle = tempfile.NamedTemporaryFile("w", newline="", encoding="utf-8", suffix=".csv", delete=False)
        handle.write(
            "chapter_id,sub_chapter_id,question_text,option_a,option_b,option_c,option_d,correct_option,solution\n"
        )
        handle.write(
            f"{self.chapter.id},{self.subchapter.id},Which gas is most abundant?,Oxygen,Nitrogen,Carbon dioxide,Hydrogen,B,Nitrogen dominates dry air, roughly 78 percent by volume\n"
        )
        handle.close()
        self.addCleanup(lambda: os.path.exists(handle.name) and os.remove(handle.name))

        call_command("import_questions_csv", handle.name, stdout=StringIO())

        question = Question.objects.get(question_text="Which gas is most abundant?")
        self.assertEqual(
            question.solution,
            "Nitrogen dominates dry air, roughly 78 percent by volume",
        )

    def test_update_solution_only_updates_existing_without_touching_options(self):
        existing = Question.objects.create(
            chapter=self.chapter,
            sub_chapter=self.subchapter,
            question_text="What is work unit?",
            option_a="Newton",
            option_b="Joule",
            option_c="Watt",
            option_d="Pascal",
            correct_option="B",
            solution="",
        )

        csv_path = self._write_csv([
            [
                str(self.chapter.id),
                str(self.subchapter.id),
                "What is work unit?",
                "Changed A",
                "Changed B",
                "Changed C",
                "Changed D",
                "A",
                "Work is force times displacement, so SI unit is Joule.",
            ],
            [
                str(self.chapter.id),
                str(self.subchapter.id),
                "Brand new question text",
                "A1",
                "B1",
                "C1",
                "D1",
                "A",
                "Should be skipped in solution-only mode.",
            ],
        ])

        call_command(
            "import_questions_csv",
            csv_path,
            "--update-duplicates",
            "--update-solution-only",
            stdout=StringIO(),
        )

        self.assertEqual(Question.objects.count(), 1)
        existing.refresh_from_db()
        self.assertEqual(existing.option_a, "Newton")
        self.assertEqual(existing.option_b, "Joule")
        self.assertEqual(existing.option_c, "Watt")
        self.assertEqual(existing.option_d, "Pascal")
        self.assertEqual(existing.correct_option, "B")
        self.assertEqual(existing.solution, "Work is force times displacement, so SI unit is Joule.")

    def test_strips_think_block_from_solution(self):
        existing = Question.objects.create(
            chapter=self.chapter,
            sub_chapter=self.subchapter,
            question_text="Static friction definition",
            option_a="Up to mu_s N",
            option_b="mu_k N",
            option_c="Always zero",
            option_d="Depends only on area",
            correct_option="A",
            solution="",
        )

        csv_path = self._write_csv([
            [
                str(self.chapter.id),
                str(self.subchapter.id),
                "Static friction definition",
                "Up to mu_s N",
                "mu_k N",
                "Always zero",
                "Depends only on area",
                "A",
                "<think>internal chain of thought</think>\n\nExplanation: Static friction adjusts up to a maximum of mu_s N.",
            ],
        ])

        call_command(
            "import_questions_csv",
            csv_path,
            "--update-duplicates",
            "--update-solution-only",
            stdout=StringIO(),
        )

        existing.refresh_from_db()
        self.assertEqual(existing.solution, "Explanation: Static friction adjusts up to a maximum of mu_s N.")

    def test_keeps_solution_from_explanation_marker(self):
        existing = Question.objects.create(
            chapter=self.chapter,
            sub_chapter=self.subchapter,
            question_text="Marker cleanup question",
            option_a="A",
            option_b="B",
            option_c="C",
            option_d="D",
            correct_option="A",
            solution="",
        )

        csv_path = self._write_csv([
            [
                str(self.chapter.id),
                str(self.subchapter.id),
                "Marker cleanup question",
                "A",
                "B",
                "C",
                "D",
                "A",
                "intro text before answer. Explanation: This is the saved explanation.",
            ],
        ])

        call_command(
            "import_questions_csv",
            csv_path,
            "--update-duplicates",
            "--update-solution-only",
            stdout=StringIO(),
        )

        existing.refresh_from_db()
        self.assertEqual(existing.solution, "Explanation: This is the saved explanation.")


class ImportSolutionsJsonCommandTests(TestCase):
    def setUp(self):
        self.subject = Subject.objects.create(name="Physics")
        self.chapter = Chapter.objects.create(subject=self.subject, name="Friction", has_subchapters=True)
        self.subchapter = SubChapter.objects.create(chapter=self.chapter, name="Static Friction", order=1)

    def _write_json(self, payload):
        handle = tempfile.NamedTemporaryFile("w", encoding="utf-8", suffix=".json", delete=False)
        json.dump(payload, handle, ensure_ascii=False)
        handle.close()
        self.addCleanup(lambda: os.path.exists(handle.name) and os.remove(handle.name))
        return handle.name

    def test_updates_solution_from_id_map_json(self):
        q = Question.objects.create(
            chapter=self.chapter,
            sub_chapter=self.subchapter,
            question_text="What is static friction?",
            option_a="Up to mu_s N",
            option_b="mu_k N",
            option_c="Zero",
            option_d="Depends only on area",
            correct_option="A",
            solution="",
        )

        json_path = self._write_json({str(q.id): "Explanation: Static friction acts up to a maximum of mu_s N."})
        output = StringIO()
        call_command("import_solutions_json", json_path, stdout=output)

        q.refresh_from_db()
        self.assertEqual(q.solution, "Explanation: Static friction acts up to a maximum of mu_s N.")
        self.assertIn("Done. Updated 1 question solution(s).", output.getvalue())

    def test_strips_think_block_in_json_solution(self):
        q = Question.objects.create(
            chapter=self.chapter,
            sub_chapter=self.subchapter,
            question_text="When does motion start?",
            option_a="F > mu_s N",
            option_b="F < mu_s N",
            option_c="Always",
            option_d="Never",
            correct_option="A",
            solution="",
        )

        json_path = self._write_json({
            str(q.id): "<think>hidden text</think>\n\nExplanation: Motion begins when applied force exceeds max static friction."
        })
        call_command("import_solutions_json", json_path, stdout=StringIO())

        q.refresh_from_db()
        self.assertEqual(
            q.solution,
            "Explanation: Motion begins when applied force exceeds max static friction.",
        )

    def test_json_keeps_solution_from_explanation_marker(self):
        q = Question.objects.create(
            chapter=self.chapter,
            sub_chapter=self.subchapter,
            question_text="JSON marker cleanup",
            option_a="A",
            option_b="B",
            option_c="C",
            option_d="D",
            correct_option="A",
            solution="",
        )

        json_path = self._write_json({
            str(q.id): "header text before answer. Explanation: Keep from here only.",
        })
        call_command("import_solutions_json", json_path, stdout=StringIO())

        q.refresh_from_db()
        self.assertEqual(q.solution, "Explanation: Keep from here only.")

    def test_json_repairs_tab_escape_in_latex_commands(self):
        q = Question.objects.create(
            chapter=self.chapter,
            sub_chapter=self.subchapter,
            question_text="JSON latex repair",
            option_a="A",
            option_b="B",
            option_c="C",
            option_d="D",
            correct_option="A",
            solution="",
        )

        # Single backslashes in source content can become control chars like tab (\t).
        broken = "Explanation: $ f_k = 0.2 \times 6 = 1.2 \\text{N} $"
        json_path = self._write_json({str(q.id): broken})
        call_command("import_solutions_json", json_path, stdout=StringIO())

        q.refresh_from_db()
        self.assertIn("\\times", q.solution)
        self.assertIn("\\text", q.solution)

    def test_dry_run_does_not_write(self):
        q = Question.objects.create(
            chapter=self.chapter,
            sub_chapter=self.subchapter,
            question_text="Dry run question",
            option_a="A",
            option_b="B",
            option_c="C",
            option_d="D",
            correct_option="A",
            solution="original",
        )

        json_path = self._write_json({str(q.id): "new value"})
        call_command("import_solutions_json", json_path, "--dry-run", stdout=StringIO())

        q.refresh_from_db()
        self.assertEqual(q.solution, "original")

    def test_fail_on_missing_raises_error(self):
        json_path = self._write_json({"999999": "missing"})
        with self.assertRaisesMessage(CommandError, "question id(s) not found"):
            call_command("import_solutions_json", json_path, "--fail-on-missing", stdout=StringIO())

    def test_map_by_question_number_maps_serial_to_ordered_questions(self):
        q1 = Question.objects.create(
            chapter=self.chapter,
            sub_chapter=self.subchapter,
            question_text="Q1",
            option_a="A",
            option_b="B",
            option_c="C",
            option_d="D",
            correct_option="A",
            solution="old1",
        )
        q2 = Question.objects.create(
            chapter=self.chapter,
            sub_chapter=self.subchapter,
            question_text="Q2",
            option_a="A",
            option_b="B",
            option_c="C",
            option_d="D",
            correct_option="B",
            solution="old2",
        )

        # 0-based serials: 0 -> first question, 1 -> second question.
        json_path = self._write_json({
            "0": "Explanation: Solution for first displayed question",
            "1": "Explanation: Solution for second displayed question",
        })

        call_command(
            "import_solutions_json",
            json_path,
            "--map-by-question-number",
            stdout=StringIO(),
        )

        q1.refresh_from_db()
        q2.refresh_from_db()
        self.assertEqual(q1.solution, "Explanation: Solution for first displayed question")
        self.assertEqual(q2.solution, "Explanation: Solution for second displayed question")

    def test_map_by_question_number_fail_on_missing_raises_error(self):
        Question.objects.create(
            chapter=self.chapter,
            sub_chapter=self.subchapter,
            question_text="Only one question",
            option_a="A",
            option_b="B",
            option_c="C",
            option_d="D",
            correct_option="A",
            solution="",
        )

        json_path = self._write_json({"5": "Explanation: out of range serial"})
        with self.assertRaisesMessage(CommandError, "question number(s) not found"):
            call_command(
                "import_solutions_json",
                json_path,
                "--map-by-question-number",
                "--fail-on-missing",
                stdout=StringIO(),
            )

    def test_explanation_only_trims_option_wise_tail(self):
        q = Question.objects.create(
            chapter=self.chapter,
            sub_chapter=self.subchapter,
            question_text="Heating in wire",
            option_a="Magnetic field",
            option_b="Electron collisions",
            option_c="Voltage only",
            option_d="Capacitance",
            correct_option="B",
            solution="",
        )

        raw = (
            "Explanation: The wire heats mainly due to electron collisions in the conductor.\n\n"
            "The other options are incorrect for the following reasons:\n\n"
            "A) Magnetic field ...\n\n"
            "C) Voltage only ..."
        )
        json_path = self._write_json({str(q.id): raw})

        call_command(
            "import_solutions_json",
            json_path,
            "--explanation-only",
            stdout=StringIO(),
        )

        q.refresh_from_db()
        self.assertEqual(
            q.solution,
            "Explanation: The wire heats mainly due to electron collisions in the conductor.",
        )

    def test_map_by_question_number_with_chapter_scope(self):
        other_chapter = Chapter.objects.create(subject=self.subject, name="Other", has_subchapters=False)

        # Global first question lives in another chapter.
        other_q = Question.objects.create(
            chapter=other_chapter,
            sub_chapter=None,
            question_text="Other chapter first",
            option_a="A",
            option_b="B",
            option_c="C",
            option_d="D",
            correct_option="A",
            solution="",
        )
        target_q = Question.objects.create(
            chapter=self.chapter,
            sub_chapter=self.subchapter,
            question_text="Scoped chapter target",
            option_a="A",
            option_b="B",
            option_c="C",
            option_d="D",
            correct_option="B",
            solution="",
        )

        # Serial 0 should map to first question inside selected chapter, not global table.
        json_path = self._write_json({"0": "Explanation: chapter-scoped mapping"})
        call_command(
            "import_solutions_json",
            json_path,
            "--map-by-question-number",
            f"--chapter-id={self.chapter.id}",
            stdout=StringIO(),
        )

        other_q.refresh_from_db()
        target_q.refresh_from_db()
        self.assertEqual(other_q.solution, "")
        self.assertEqual(target_q.solution, "Explanation: chapter-scoped mapping")


class ExportQuestionsForSolutionCommandTests(TestCase):
    def setUp(self):
        self.subject = Subject.objects.create(name="Physics")
        self.chapter = Chapter.objects.create(subject=self.subject, name="Mechanics", has_subchapters=True)
        self.subchapter = SubChapter.objects.create(chapter=self.chapter, name="Kinematics", order=1)

    def test_exports_id_based_json_rows(self):
        q = Question.objects.create(
            chapter=self.chapter,
            sub_chapter=self.subchapter,
            question_text="What is velocity?",
            option_a="distance/time",
            option_b="displacement/time",
            option_c="mass*acceleration",
            option_d="force/area",
            correct_option="B",
            solution="",
        )

        with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as f:
            output_path = f.name
        self.addCleanup(lambda: os.path.exists(output_path) and os.remove(output_path))

        call_command("export_questions_for_solution", output_path, stdout=StringIO())

        with open(output_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        self.assertEqual(len(data), 1)
        row = data[0]
        self.assertEqual(row["id"], q.id)
        self.assertEqual(row["question_text"], "What is velocity?")
        self.assertEqual(row["solution"], "")
