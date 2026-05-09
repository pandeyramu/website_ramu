from django.core.management.base import BaseCommand
from django.db.models import Q
from CEE_Quiz.models import SubChapter, Question
import random

class Command(BaseCommand):
    help = 'Generate a random full test with 200 questions or topic-based test'

    def add_arguments(self, parser):
        parser.add_argument(
            '--type',
            type=str,
            default='full',
            help='Test type: full (200 questions) or topic (specific subject)'
        )
        parser.add_argument(
            '--subject',
            type=str,
            help='Subject name for topic test (Physics, Chemistry, Botany, Zoology, MAT)'
        )
        parser.add_argument(
            '--count',
            type=int,
            help='Number of questions for custom test'
        )

    def handle(self, *args, **options):
        test_type = options['type']
        
        # Test configuration - questions per subject/chapter
        test_config = {
            'full': {
                'Physics': {
                    'Mechanics': 10,
                    'Heat and Thermodynamics': 7,
                    'Waves and Optics': 8,
                    'Current Electricity and Magnetism': 9,
                    'Electrostatics and Capacitors': 4,
                    'Modern Physics': 12,
                },
                'Chemistry': {
                    'Physical Chemistry': 17,
                    'Inorganic Chemistry': 10,
                    'Organic Chemistry': 17,
                    'Applied Chemistry': 3,
                    'Analytical Chemistry': 3,
                },
                'Botany': {
                    'Basic Components of Life': 2,
                    'Biodiversity': 9,
                    'Ecology and Vegetation': 4,
                    'Cell Biology': 5,
                    'Genetics': 6,
                    'Plant Anatomy': 3,
                    'Plant Physiology': 6,
                    'Developmental Botany': 2,
                    'Applied Botany': 3,
                },
                'Zoology': {
                    'Evolutionary Biology': 3,
                    'Animal Diversity and Classification': 4,
                    'Animal Tissues and Histology': 4,
                    'Study of Selected Animals': 6,
                    'Human Biology and Physiology': 15,
                    'Microbial Diseases and Immunology': 4,
                    'Medical Technology and Applied Biology': 2,
                    'Biota, Environment and Conservation': 2,
                },
                'MAT': {
                    'Verbal Reasoning': 5,
                    'Numerical Reasoning': 5,
                    'Logical Sequencing': 5,
                    'Spatial Relation / Abstract Reasoning': 5,
                }
            }
        }

        if test_type == 'full':
            self.generate_full_test(test_config['full'])
        elif test_type == 'topic' and options.get('subject'):
            self.generate_topic_test(options['subject'], test_config['full'])
        elif test_type == 'custom' and options.get('count'):
            self.generate_custom_test(options['count'])
        else:
            self.stdout.write(self.style.ERROR('Invalid arguments'))

    def generate_full_test(self, config):
        """Generate a full test with all subjects"""
        test_questions = []
        
        for subject_name, chapters_config in config.items():
            if subject_name == 'MAT':
                # MAT questions - would need separate table/handling
                self.stdout.write(f"MAT questions: 20 (requires separate setup)")
                continue
            
            self.stdout.write(f"\n{subject_name}:")
            
            for chapter_name, question_count in chapters_config.items():
                # Get all subchapters for this chapter
                subchapters = SubChapter.objects.filter(
                    chapter__name=chapter_name,
                    chapter__subject__name=subject_name
                )
                
                # Count available questions per subchapter
                available_questions = Question.objects.filter(
                    sub_chapter__in=subchapters
                ).count()
                
                self.stdout.write(
                    f"  {chapter_name}: {question_count} questions needed "
                    f"({available_questions} available)"
                )
                
                # Select random questions
                if available_questions >= question_count:
                    selected = Question.objects.filter(
                        sub_chapter__in=subchapters
                    ).order_by('?')[:question_count]
                    test_questions.extend(list(selected))
                else:
                    self.stdout.write(
                        self.style.WARNING(
                            f"    ⚠ Not enough questions! Need {question_count}, "
                            f"have {available_questions}"
                        )
                    )
        
        self.stdout.write(
            self.style.SUCCESS(
                f'\nTotal questions selected: {len(test_questions)}'
            )
        )

    def generate_topic_test(self, subject_name, config):
        """Generate a test for a specific subject"""
        if subject_name not in config:
            self.stdout.write(
                self.style.ERROR(
                    f'Subject {subject_name} not found in config'
                )
            )
            return
        
        chapters_config = config[subject_name]
        total_questions = 0
        
        self.stdout.write(f"\n{subject_name} Test:")
        
        for chapter_name, question_count in chapters_config.items():
            subchapters = SubChapter.objects.filter(
                chapter__name=chapter_name,
                chapter__subject__name=subject_name
            )
            
            available_questions = Question.objects.filter(
                sub_chapter__in=subchapters
            ).count()
            
            self.stdout.write(
                f"  {chapter_name}: {question_count} questions "
                f"({available_questions} available)"
            )
            
            total_questions += question_count
        
        self.stdout.write(
            self.style.SUCCESS(
                f'\nTotal questions for {subject_name}: {total_questions}'
            )
        )

    def generate_custom_test(self, count):
        """Generate a custom test with specified number of questions"""
        available = Question.objects.count()
        
        if available < count:
            self.stdout.write(
                self.style.ERROR(
                    f'Not enough questions! Need {count}, have {available}'
                )
            )
            return
        
        questions = Question.objects.all().order_by('?')[:count]
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Generated custom test with {len(questions)} questions'
            )
        )
