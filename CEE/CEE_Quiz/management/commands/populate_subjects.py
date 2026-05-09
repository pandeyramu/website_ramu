from django.core.management.base import BaseCommand
from CEE_Quiz.models import Subject, Chapter, SubChapter

class Command(BaseCommand):
    help = 'Populate subjects, chapters, and subchapters into the database'

    def handle(self, *args, **kwargs):
        # Define data structure
        data = {
            'Physics': {
                'PHY-1': {
                    'name': 'Mechanics',
                    'subchapters': [
                        'Physical quantities, vectors and scalars',
                        'Kinematics',
                        'Dynamics',
                        'Rotational dynamics',
                        'Fluid statics and dynamics',
                        'Circular and Periodic motion',
                        'Gravity',
                        'Elasticity',
                    ]
                },
                'PHY-2': {
                    'name': 'Heat and Thermodynamics',
                    'subchapters': [
                        'Thermal energy, heat, temperature and thermometers',
                        'Thermal expansion',
                        'Quantity of heat',
                        'Ideal gas',
                        'First law of thermodynamics',
                        'Second law of thermodynamics',
                    ]
                },
                'PHY-3': {
                    'name': 'Waves and Optics',
                    'subchapters': [
                        'Wave motion',
                        'Stationary waves',
                        'Acoustic phenomena',
                        'Reflection, refraction and dispersion',
                        'Interference',
                        'Diffraction and polarization',
                    ]
                },
                'PHY-4': {
                    'name': 'Current Electricity and Magnetism',
                    'subchapters': [
                        'Electrical quantities',
                        'Electrical circuits',
                        'Thermoelectric effect',
                        'Alternating currents',
                        'Magnetic properties of materials',
                        'Magnetic field',
                        'Electromagnetic induction',
                    ]
                },
                'PHY-5': {
                    'name': 'Electrostatics and Capacitors',
                    'subchapters': [
                        'Electric charge and electric field',
                        'Electric field strength, potential and potential energy',
                        'Capacitors',
                    ]
                },
                'PHY-6': {
                    'name': 'Modern Physics',
                    'subchapters': [
                        'Nuclear physics',
                        'Electron',
                        'Photon and photoelectric effect',
                        'Wave particle duality and X-rays',
                        'Radioactivity',
                        'Solid and semiconductor devices',
                        'Particle physics and recent trends',
                    ]
                }
            },
            'Chemistry': {
                'CHE-1': {
                    'name': 'Physical Chemistry',
                    'subchapters': [
                        'Basic Concepts in Chemistry',
                        'Stoichiometry',
                        'Atomic Structure',
                        'Classification of Elements and Periodicity',
                        'Chemical Bonding and Shape of Molecules',
                        'Redox Reaction',
                        'States of Matter',
                        'Chemical Equilibrium',
                        'Volumetric Analysis',
                        'Ionic Equilibrium',
                        'Chemical Kinetics',
                        'Electrochemistry',
                        'Chemical Thermodynamics',
                        'Nuclear Chemistry',
                    ]
                },
                'CHE-2': {
                    'name': 'Inorganic Chemistry',
                    'subchapters': [
                        'Chemistry of Non-metals',
                        'Chemistry of Metals',
                        'Bio-inorganic Chemistry',
                    ]
                },
                'CHE-3': {
                    'name': 'Organic Chemistry',
                    'subchapters': [
                        'General Organic Chemistry',
                        'Hydrocarbons',
                        'Aromatic Hydrocarbons',
                        'Haloalkanes and Haloarenes',
                        'Alcohols and Phenols',
                        'Ethers',
                        'Aldehydes and Ketones',
                        'Carboxylic Acid and its Derivatives',
                        'Nitro-compounds',
                        'Amines',
                        'Organometallic Compounds',
                    ]
                },
                'CHE-4': {
                    'name': 'Applied Chemistry',
                    'subchapters': [
                        'Manufacturing Processes',
                        'Applications of Non-metals, Metals and Compounds',
                        'Chemistry in Service to Mankind',
                    ]
                },
                'CHE-5': {
                    'name': 'Analytical Chemistry',
                    'subchapters': [
                        'Chemical Tests',
                        'Separation Techniques',
                        'Types of Titration',
                    ]
                }
            },
            'Zoology': {
                'ZOO-1': {
                    'name': 'Evolutionary Biology',
                    'subchapters': [
                        'Origin of life',
                        'Evidences of evolution',
                        'Theories of evolution',
                        'Human evolution',
                    ]
                },
                'ZOO-2': {
                    'name': 'Animal Diversity and Classification',
                    'subchapters': [
                        'Animal diversity from Protozoa to Chordata',
                    ]
                },
                'ZOO-3': {
                    'name': 'Animal Tissues and Histology',
                    'subchapters': [
                        'Types of animal tissues',
                    ]
                },
                'ZOO-4': {
                    'name': 'Study of Selected Animals',
                    'subchapters': [
                        'Plasmodium',
                        'Earthworm (Pheretima)',
                        'Frog (Rana)',
                    ]
                },
                'ZOO-5': {
                    'name': 'Human Biology and Physiology',
                    'subchapters': [
                        'Digestive System',
                        'Respiratory System',
                        'Circulatory System',
                        'Excretory System',
                        'Nervous System',
                        'Sense Organs',
                        'Endocrinology',
                        'Reproductive System',
                    ]
                },
                'ZOO-6': {
                    'name': 'Microbial Diseases and Immunology',
                    'subchapters': [
                        'Microbial diseases',
                        'Immunity',
                        'Vaccines',
                    ]
                },
                'ZOO-7': {
                    'name': 'Medical Technology and Applied Biology',
                    'subchapters': [
                        'Medical technology',
                        'Applied microbiology',
                    ]
                },
                'ZOO-8': {
                    'name': 'Biota, Environment and Conservation',
                    'subchapters': [
                        'Animal Behavior',
                        'Environmental pollution',
                        'Adaptations',
                        'Conservation Biology',
                    ]
                }
            },
            'Botany': {
                'BOT-1': {
                    'name': 'Basic Components of Life',
                    'subchapters': [
                        'Carbohydrates, lipids and minerals',
                        'Proteins and enzymes',
                    ]
                },
                'BOT-2': {
                    'name': 'Biodiversity',
                    'subchapters': [
                        'Introduction and classification systems',
                        'Monera and Virus',
                        'Fungi and Lichens',
                        'Algae',
                        'Bryophytes',
                        'Pteridophytes',
                        'Gymnosperms',
                        'Angiosperms',
                        'Economic importance of plant groups',
                        'Medicinal plants of Nepal',
                    ]
                },
                'BOT-3': {
                    'name': 'Ecology and Vegetation',
                    'subchapters': [
                        'Ecosystem ecology',
                        'Biogeochemical cycles and ecological imbalances',
                        'Vegetation and adaptation',
                    ]
                },
                'BOT-4': {
                    'name': 'Cell Biology',
                    'subchapters': [
                        'Prokaryotic and eukaryotic cells',
                        'Cell organelles',
                        'Cell cycle and cell division',
                    ]
                },
                'BOT-5': {
                    'name': 'Genetics',
                    'subchapters': [
                        'Genetic material – DNA and RNA',
                        'Mendelian Genetics and Linkage',
                        'Sex-linked Inheritance',
                        'Mutation, Polyploidy and Genetic Disorders',
                    ]
                },
                'BOT-6': {
                    'name': 'Plant Anatomy',
                    'subchapters': [
                        'Plant tissues and vascular bundles',
                        'Anatomy of monocot and dicot root, stem and leaf',
                    ]
                },
                'BOT-7': {
                    'name': 'Plant Physiology',
                    'subchapters': [
                        'Water relations',
                        'Photosynthesis',
                        'Respiration',
                        'Plant growth and seed germination',
                    ]
                },
                'BOT-8': {
                    'name': 'Developmental Botany',
                    'subchapters': [
                        'Reproduction and sporogenesis in angiosperms',
                        'Embryo and endosperm',
                    ]
                },
                'BOT-9': {
                    'name': 'Applied Botany',
                    'subchapters': [
                        'Plant tissue culture',
                        'Genetic engineering',
                        'Biofertilizers and food security',
                    ]
                }
            }
        }

        # Clear existing data
        SubChapter.objects.all().delete()
        Chapter.objects.all().delete()
        Subject.objects.all().delete()

        # Populate data
        for subject_name, chapters_data in data.items():
            subject = Subject.objects.create(name=subject_name)
            self.stdout.write(f"Created subject: {subject_name}")

            for chapter_code, chapter_info in chapters_data.items():
                chapter_name = chapter_info['name']
                subchapters_list = chapter_info['subchapters']
                
                chapter = Chapter.objects.create(
                    subject=subject,
                    name=chapter_name,
                    has_subchapters=True
                )
                self.stdout.write(f"  Created chapter: {chapter_name}")

                for order, subchapter_name in enumerate(subchapters_list, start=1):
                    SubChapter.objects.create(
                        chapter=chapter,
                        name=subchapter_name,
                        order=order
                    )
                    self.stdout.write(f"    Created subchapter: {subchapter_name}")

        self.stdout.write(self.style.SUCCESS('Successfully populated all subjects, chapters, and subchapters!'))
