from django.db import migrations, models


def add_solution_column_if_missing(apps, schema_editor):
    table_name = "CEE_Quiz_question"

    with schema_editor.connection.cursor() as cursor:
        vendor = schema_editor.connection.vendor

        if vendor == "postgresql":
            cursor.execute(
                'ALTER TABLE "CEE_Quiz_question" '
                'ADD COLUMN IF NOT EXISTS "solution" text NOT NULL DEFAULT \'\''
            )
            return

        if vendor == "sqlite":
            cursor.execute('PRAGMA table_info("CEE_Quiz_question")')
            existing = {row[1] for row in cursor.fetchall()}
            if "solution" not in existing:
                cursor.execute(
                    'ALTER TABLE "CEE_Quiz_question" '
                    'ADD COLUMN "solution" text NOT NULL DEFAULT \'\''
                )
            return

        # Fallback for other engines.
        existing = {
            c.name
            for c in schema_editor.connection.introspection.get_table_description(
                cursor, table_name
            )
        }
        if "solution" not in existing:
            cursor.execute(
                'ALTER TABLE "CEE_Quiz_question" '
                'ADD COLUMN "solution" text NOT NULL DEFAULT \'\''
            )


def noop_reverse(apps, schema_editor):
    # Keep rollback no-op; removing columns safely is backend-specific.
    return


class Migration(migrations.Migration):

    dependencies = [
        ("CEE_Quiz", "0004_chapter_has_subchapters_subchapter_and_more"),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            database_operations=[
                migrations.RunPython(
                    add_solution_column_if_missing,
                    reverse_code=noop_reverse,
                ),
            ],
            state_operations=[
                migrations.AddField(
                    model_name="question",
                    name="solution",
                    field=models.TextField(blank=True, default=""),
                ),
            ],
        ),
    ]
