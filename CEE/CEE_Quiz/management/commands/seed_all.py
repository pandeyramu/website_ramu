from django.core.management.base import BaseCommand
from CEE_Quiz.models import Subject, Chapter, SubChapter


SUBJECTS = [
    {"id": 1, "name": "Physics"},
    {"id": 2, "name": "Chemistry"},
    {"id": 3, "name": "Biology"},
]

# id: (name, subject_id)
CHAPTERS = [
    (1,  "Mechanics(10)",                                                              1),
    (2,  "Heat and Thermodynamics(6)",                                                 1),
    (3,  "Geometrical optics and physical optics(6)",                                  1),
    (4,  "Current electricity and magnetism(9)",                                       1),
    (5,  "Sound waves, electrostatics and capacitors(6)",                              1),
    (6,  "Modern physics and nuclear physics(6)",                                      1),
    (7,  "Solid and semiconductor devices (electronics)(4)",                           1),
    (8,  "Particle physics, source of energy and universe(3)",                         1),
    (9,  "General and physical chemistry(18)",                                         2),
    (10, "Inorganic chemistry(14)",                                                    2),
    (11, "Organic chemistry(18)",                                                      2),
    (12, "Basic component of life and biodiversity(11)",                               3),
    (13, "Ecology and Environment(5)",                                                  3),
    (14, "Cell biology and genetics(12)",                                              3),
    (15, "Anatomy and Physiology(7)",                                                  3),
    (16, "Developmental and Applied Botany(5)",                                        3),
    (17, "Biology, origin and evolution of life(4)",                                   3),
    (18, "General characteristics and classification of protozoa to chordates(8)",     3),
    (19, "Plasmodium, Earthworm and Frog(8)",                                          3),
    (20, "Human Biology and human diseases(14)",                                       3),
    (21, "Animal tissues(4)",                                                          3),
    (22, "Environmental pollution, adaptation and animal behavior, application of Zoology(2)", 3),
]

# chapter_id: [subchapter names in order]
SUBCHAPTERS = {
    1: [
        "Units, Dimensions and Errors",
        "Vectors and Scalars",
        "Motion in a Straight Line",
        "Motion in Plane and Projectile Motion",
        "Newton's Laws of Motion",
        "Friction",
        "Work, Energy, Power and Collision",
        "Circular Motion",
        "Gravitation",
        "Rotational Motion",
        "Simple Harmonic Motion",
        "Elasticity",
        "Surface Tension",
        "Fluid Dynamics and Viscosity",
        "Hydrostatics",
    ],
    2: [
        "Thermometry",
        "Thermal Expansion",
        "Calorimetry, Change of State and Hygrometry",
        "Kinetic Theory of Gases and Gas Laws",
        "Transmission of Heat",
        "Thermodynamics",
    ],
    3: [
        "Reflection at Plane and Curved Mirrors",
        "Refraction at Plane Surfaces and Total Internal Reflection",
        "Refraction Through Prism and Dispersion",
        "Refraction Through Lenses",
        "Chromatic Aberration",
        "Wave Nature of Light (Interference, Diffraction, Polarisation)",
    ],
    4: [
        "Electric Current",
        "Heating Effects of Current",
        "Thermoelectricity",
        "Meters",
        "Magnetism",
        "Magnetic Effects of Current",
        "Electromagnetic Induction",
        "Alternating Current",
        "Capacitance",
    ],
    5: [
        "Waves",
        "Stationary / Standing Waves",
        "Doppler's Effect and Musical Sound",
        "Charge and Electric Force",
        "Electric Field and Potential",
        "Capacitance and Capacitors",
    ],
    6: [
        "Cathode Rays, Positive Rays and Electrons",
        "Photoelectric Effect",
        "X-Rays",
        "Atomic Structure and Spectrum",
        "Radioactivity",
        "Nuclear Physics",
    ],
    7: [
        "Energy Bands in Solids",
        "Semiconductor and Diode",
        "Transistor",
        "Logic Gates",
    ],
    8: [
        "Particle Physics",
        "Source of Energy",
        "Universe",
    ],
    9: [
        "Language of Chemistry-Stoichiometry",
        "Chemical Calculation",
        "Atomic Structure",
        "Radioactivity and Nuclear Transformation",
        "Chemical Bonding",
        "Oxidation and Reduction",
        "Acids, Bases and Salts",
        "Gaseous and Liquid States",
        "Solid State",
        "Colloids and Catalysis",
        "Volumetric Analysis",
        "Chemical Equilibrium",
        "Ionic Equilibrium",
        "Solutions",
        "Chemical Kinetics",
        "Electrochemistry",
        "Thermodynamics",
    ],
    10: [
        "Periodic Table",
        "Hydrogen and Its Compounds",
        "The Alkali Metals",
        "The Alkaline Earth Metals",
        "Carbon Family",
        "Nitrogen Family",
        "Oxygen Family (Group 16)",
        "The Halogen Family",
        "Metals and Metallurgy",
        "Heavy Metals",
        "Transition Metal and Co-ordination Chemistry",
        "Cement",
        "Paper and Pulp",
    ],
    11: [
        "Some Basic Principles",
        "Purification and Characterization",
        "Nomenclature of Organic Compound",
        "Isomerism",
        "Reaction Mechanism",
        "Hydrocarbons",
        "Halogen Derivatives",
        "Alcohol",
        "Phenols",
        "Ether",
        "Carbonyl Compounds",
        "Carboxylic Compounds and their derivatives",
        "Compounds Containing Nitrogen",
        "The Molecules of life",
        "Polymer and Polymerization",
        "Chemistry In action",
        "Organometallic Compounds",
    ],
    12: [
        "Virus",
        "Kingdom Monera",
        "Kingdom Mycota",
        "Algae",
        "Bryophytes",
        "Pteridophytes",
        "Gymnosperms",
        "Morphology of Angiosperms",
        "Taxonomy of Angiosperms",
    ],
    13: [
        "Ecology and Conservation",
    ],
    14: [
        "Cell Biology",
        "Cell Cycle and Reproduction",
        "Genetics: Inheritance and Variation",
        "Genetic Materials",
    ],
    15: [
        "Plant Anatomy",
        "Water Relation",
        "Transpiration",
        "Photosynthesis",
        "Respiration",
    ],
    16: [
        "Growth and Development",
        "Developmental Biology",
        "Application of Biology",
    ],
    17: [
        "Introduction to Biology",
        "Origin and Evolution",
    ],
    18: [
        "Kingdom Protista",
        "Kingdom Animalia I",
        "Kingdom Animalia II",
        "Chordates Characters",
    ],
    19: [
        "Earthworm",
        "Frog",
        "Plasmodium",
    ],
    20: [
        "Nervous System",
        "Receptors and Sense Organs",
        "Cardiovascular System",
        "Endocrinology",
        "Respiratory System",
        "Digestive System",
        "Excretory System",
        "Reproductive System",
        "Developmental Biology",
        "Substances Abuse and Human Diseases",
    ],
    21: [
        "Animal Tissues",
    ],
    22: [
        "Behaviour and Adaptation",
    ],
}


class Command(BaseCommand):
    help = "Seed all Subjects, Chapters, and SubChapters from scratch."

    def handle(self, *args, **options):
        self.stdout.write(self.style.MIGRATE_HEADING("\n=== Seeding Subjects ==="))
        subject_map = {}
        for s in SUBJECTS:
            obj, created = Subject.objects.update_or_create(
                id=s["id"],
                defaults={"name": s["name"]},
            )
            subject_map[s["id"]] = obj
            status = "Created" if created else "Already exists"
            self.stdout.write(f"  {'✓' if created else '-'} [{s['id']}] {s['name']} — {status}")

        self.stdout.write(self.style.MIGRATE_HEADING("\n=== Seeding Chapters ==="))
        chapter_map = {}
        for (ch_id, ch_name, subj_id) in CHAPTERS:
            has_subs = ch_id in SUBCHAPTERS
            obj, created = Chapter.objects.update_or_create(
                id=ch_id,
                defaults={
                    "name": ch_name,
                    "subject": subject_map[subj_id],
                    "has_subchapters": has_subs,
                },
            )
            chapter_map[ch_id] = obj
            status = "Created" if created else "Already exists"
            self.stdout.write(f"  {'✓' if created else '-'} [{ch_id}] {ch_name} — {status}")

        self.stdout.write(self.style.MIGRATE_HEADING("\n=== Seeding SubChapters ==="))
        total_created = 0
        total_skipped = 0
        for ch_id, names in SUBCHAPTERS.items():
            chapter = chapter_map[ch_id]
            self.stdout.write(f"\n  Chapter {ch_id}: {chapter.name}")
            for order, name in enumerate(names, start=1):
                obj, created = SubChapter.objects.update_or_create(
                    chapter=chapter,
                    name=name,
                    defaults={"order": order},
                )
                if created:
                    total_created += 1
                    self.stdout.write(f"    ✓ {order}. {name}")
                else:
                    total_skipped += 1
                    self.stdout.write(f"    - {order}. {name} (exists)")

        self.stdout.write(self.style.SUCCESS(
            f"\n\nAll done!"
            f"\n  Subjects : {len(SUBJECTS)}"
            f"\n  Chapters : {len(CHAPTERS)}"
            f"\n  SubChapters created : {total_created}, skipped : {total_skipped}"
        ))
