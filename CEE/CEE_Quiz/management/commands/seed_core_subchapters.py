from django.core.management.base import BaseCommand

from CEE_Quiz.models import Chapter, SubChapter


SUBCHAPTERS_BY_CHAPTER_ID = {
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
}


def _normalize_name(value):
    return " ".join(value.strip().split()).lower().rstrip(".")


class Command(BaseCommand):
    help = "Seed subchapters for Physics (1-8), Physical Chemistry (9), and Inorganic Chemistry (10)."

    def handle(self, *args, **options):
        total_created = 0
        total_updated = 0

        for chapter_id, target_names in SUBCHAPTERS_BY_CHAPTER_ID.items():
            try:
                chapter = Chapter.objects.get(id=chapter_id)
            except Chapter.DoesNotExist:
                self.stderr.write(self.style.WARNING(f"Skipped chapter {chapter_id}: not found."))
                continue

            chapter.has_subchapters = True
            chapter.save(update_fields=['has_subchapters'])

            existing_subchapters = list(
                SubChapter.objects.filter(chapter=chapter).order_by('order', 'id')
            )
            existing_by_key = {}
            for sub in existing_subchapters:
                key = _normalize_name(sub.name)
                if key not in existing_by_key:
                    existing_by_key[key] = sub

            created_count = 0
            updated_count = 0

            self.stdout.write(f"\nChapter {chapter.id}: {chapter.name}")

            for order, name in enumerate(target_names, start=1):
                key = _normalize_name(name)
                matched = existing_by_key.get(key)

                if matched:
                    changed = False
                    clean_name = name.rstrip('.')
                    if matched.name != clean_name:
                        matched.name = clean_name
                        changed = True
                    if matched.order != order:
                        matched.order = order
                        changed = True
                    if changed:
                        matched.save(update_fields=['name', 'order'])
                        updated_count += 1
                        self.stdout.write(f"  ↻ Updated: {order}. {clean_name}")
                    else:
                        self.stdout.write(f"  - Already correct: {order}. {clean_name}")
                    continue

                clean_name = name.rstrip('.')
                SubChapter.objects.create(
                    chapter=chapter,
                    name=clean_name,
                    order=order,
                )
                created_count += 1
                self.stdout.write(f"  ✓ Created: {order}. {clean_name}")

            total_created += created_count
            total_updated += updated_count
            total_for_chapter = SubChapter.objects.filter(chapter=chapter).count()

            self.stdout.write(self.style.SUCCESS(
                f"  => Done for chapter {chapter.id}: created {created_count}, "
                f"updated {updated_count}, total {total_for_chapter}"
            ))

        self.stdout.write(self.style.SUCCESS(
            f"\nAll done. Total created: {total_created}, total updated: {total_updated}."
        ))
