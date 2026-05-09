import csv
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from CEE_Quiz.models import Chapter, SubChapter, Question, Subject


class Command(BaseCommand):
    help = 'Import questions from CSV file (fast batch import)'

    def add_arguments(self, parser):
        parser.add_argument('csv_file', type=str, help='Path to the CSV file')
        parser.add_argument('--batch-size', type=int, default=500, help='Batch size for bulk_create')

    def handle(self, *args, **options):
        csv_file = options['csv_file']
        batch_size = options['batch_size']
        
        # Chapter code to subject mapping
        chapter_mapping = {
            'PHY': 'Physics',
            'CHE': 'Chemistry',
            'ZOO': 'Zoology',
            'BOT': 'Botany',
            'MAT': 'MAT'
        }
        
        # Pre-cache all chapters and subchapters
        self.stdout.write("Caching chapters and subchapters...")
        chapters_cache = {}
        subchapters_cache = {}
        
        for subject_name in chapter_mapping.values():
            try:
                subject = Subject.objects.get(name=subject_name)
                chapters = list(Chapter.objects.filter(subject=subject).order_by('id'))
                chapters_cache[subject_name] = chapters
                
                # Cache subchapters for each chapter
                for chapter in chapters:
                    subchapters_cache[chapter.id] = list(
                        SubChapter.objects.filter(chapter=chapter).order_by('order')
                    )
            except Subject.DoesNotExist:
                self.stdout.write(
                    self.style.WARNING(f"Subject '{subject_name}' not found. Skipping.")
                )
        
        try:
            questions_batch = []
            total_rows = 0
            imported_count = 0
            error_count = 0
            
            with open(csv_file, 'r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                
                with transaction.atomic():
                    for row in reader:
                        total_rows += 1
                        try:
                            # Parse chapter_id
                            parts = row['chapter_id'].split('-')
                            chapter_code = parts[0].upper()
                            chapter_num = int(parts[1]) if len(parts) > 1 else 1
                            
                            if chapter_code not in chapter_mapping:
                                error_count += 1
                                continue
                            
                            subject_name = chapter_mapping[chapter_code]
                            if subject_name not in chapters_cache:
                                error_count += 1
                                continue
                            
                            chapters = chapters_cache[subject_name]
                            if chapter_num - 1 >= len(chapters):
                                error_count += 1
                                continue
                            
                            chapter = chapters[chapter_num - 1]
                            
                            # Get subchapter by its database ID.
                            # The CSV stores the actual SubChapter primary key in sub_chapter_id.
                            sub_chapter = None
                            sub_chapter_id_str = row.get('sub_chapter_id', '').strip()
                            if sub_chapter_id_str:
                                try:
                                    sub_chapter_id = int(sub_chapter_id_str)
                                    sub_chapter = next(
                                        (sc for sc in subchapters_cache.get(chapter.id, []) if sc.id == sub_chapter_id),
                                        None,
                                    )
                                    if not sub_chapter:
                                        self.stdout.write(
                                            self.style.WARNING(
                                                f"SubChapter id '{sub_chapter_id}' not found for Chapter '{chapter.name}'. Question will have no sub-chapter."
                                            )
                                        )
                                    else:
                                        pass
                                except ValueError:
                                    self.stdout.write(
                                        self.style.WARNING(
                                            f"Could not process sub_chapter_id '{sub_chapter_id_str}' for Chapter '{chapter.name}'."
                                        )
                                    )
                            
                            # Create question object (not saved yet)
                            question = Question(
                                chapter=chapter,
                                sub_chapter=sub_chapter,
                                question_text=row['question_text'].strip(),
                                option_a=row['option_a'].strip(),
                                option_b=row['option_b'].strip(),
                                option_c=row['option_c'].strip(),
                                option_d=row['option_d'].strip(),
                                correct_option=row['correct_option'].upper(),
                                solution=row.get('solution', '').strip()
                            )
                            
                            questions_batch.append(question)
                            imported_count += 1
                            
                            # Bulk create when batch is full
                            if len(questions_batch) >= batch_size:
                                Question.objects.bulk_create(questions_batch)
                                self.stdout.write(f"Imported {imported_count} questions...")
                                questions_batch = []
                            
                        except Exception as e:
                            error_count += 1
                            if total_rows % 500 == 0:
                                self.stdout.write(
                                    self.style.WARNING(f"Row {total_rows}: {str(e)}")
                                )
                    
                    # Final batch
                    if questions_batch:
                        Question.objects.bulk_create(questions_batch)
            
            self.stdout.write(
                self.style.SUCCESS(
                    f"\n{'='*50}\n"
                    f"Import completed!\n"
                    f"{'='*50}\n"
                    f"Total rows processed: {total_rows}\n"
                    f"Successfully imported: {imported_count}\n"
                    f"Errors: {error_count}\n"
                    f"Total questions in DB: {Question.objects.count()}\n"
                    f"{'='*50}"
                )
            )
            
        except FileNotFoundError:
            raise CommandError(f"CSV file '{csv_file}' not found")
